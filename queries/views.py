import logging

from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import ai_service
from .models import CustomerQuery
from .serializers import CustomerQuerySerializer, StatusUpdateSerializer

logger = logging.getLogger(__name__)


class CustomerQueryViewSet(viewsets.ModelViewSet):
    """CRUD + status update + AI analysis + dashboard for customer queries."""
    queryset = CustomerQuery.objects.all()
    serializer_class = CustomerQuerySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "priority", "status"]
    search_fields = ["customer_name", "email"]
    ordering_fields = ["created_at", "priority", "status"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(request=None, responses=CustomerQuerySerializer)
    @action(detail=True, methods=["post"], url_path="analyze")
    def analyze(self, request, pk=None):
        """Run AI analysis: sets category, priority and a suggested response."""
        query = self.get_object()
        try:
            result = ai_service.analyze_query(query.subject, query.description)
        except Exception:  # last line of defence - should not normally happen
            logger.exception("Unexpected AI analysis error for query %s", query.pk)
            return Response({"detail": "AI analysis failed. Please try again later."},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
        query.category = result["category"]
        query.priority = result["priority"]
        query.suggested_response = result["suggested_response"]
        query.ai_source = result["source"]
        query.save(update_fields=["category", "priority", "suggested_response", "ai_source", "updated_at"])
        return Response({
            "query_id": query.pk,
            "category": query.category,
            "priority": query.priority,
            "suggested_response": query.suggested_response,
            "ai_source": query.ai_source,
        })

    @extend_schema(request=StatusUpdateSerializer, responses=CustomerQuerySerializer)
    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        """Update only the status (Pending / In Progress / Resolved)."""
        query = self.get_object()
        serializer = StatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query.status = serializer.validated_data["status"]
        query.save(update_fields=["status", "updated_at"])
        return Response(CustomerQuerySerializer(query).data)

    @extend_schema(responses={200: dict})
    @action(detail=False, methods=["get"], url_path="dashboard", filter_backends=[], pagination_class=None)
    def dashboard(self, request):
        """Totals by status."""
        agg = CustomerQuery.objects.aggregate(
            total=Count("id"),
            pending=Count("id", filter=Q(status=CustomerQuery.Status.PENDING)),
            in_progress=Count("id", filter=Q(status=CustomerQuery.Status.IN_PROGRESS)),
            resolved=Count("id", filter=Q(status=CustomerQuery.Status.RESOLVED)),
        )
        return Response(agg)
