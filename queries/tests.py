from unittest.mock import MagicMock, patch

import requests
from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import CustomerQuery

PAYLOAD = {
    "customer_name": "Rahul Sharma",
    "email": "rahul@example.com",
    "subject": "Double payment",
    "description": "My payment has been deducted twice, but my subscription is still not activated.",
}


class AuthTests(APITestCase):
    def test_register_login_flow(self):
        r = self.client.post("/api/register/", {"username": "ranjeet", "email": "r@x.com",
                                                "password": "Str0ng!Pass#1", "password2": "Str0ng!Pass#1"})
        self.assertEqual(r.status_code, 201)
        self.assertIn("token", r.data)
        r = self.client.post("/api/login/", {"username": "ranjeet", "password": "Str0ng!Pass#1"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("token", r.data)

    def test_register_validation(self):
        r = self.client.post("/api/register/", {"username": "a", "email": "bad", "password": "123", "password2": "456"})
        self.assertEqual(r.status_code, 400)

    def test_login_invalid(self):
        r = self.client.post("/api/login/", {"username": "nope", "password": "nope"})
        self.assertEqual(r.status_code, 400)


@override_settings(GEMINI_API_KEY="")
class QueryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("tester", "t@x.com", "Pass#12345")
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def _create(self, **extra):
        return self.client.post("/api/queries/", {**PAYLOAD, **extra})

    def test_auth_required(self):
        self.client.credentials()
        self.assertEqual(self.client.get("/api/queries/").status_code, 401)

    def test_crud(self):
        r = self._create()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["status"], "Pending")
        qid = r.data["id"]
        self.assertEqual(self.client.get(f"/api/queries/{qid}/").status_code, 200)
        r = self.client.put(f"/api/queries/{qid}/", {**PAYLOAD, "subject": "Updated subject"})
        self.assertEqual(r.data["subject"], "Updated subject")
        self.assertEqual(self.client.delete(f"/api/queries/{qid}/").status_code, 204)
        self.assertEqual(self.client.get(f"/api/queries/{qid}/").status_code, 404)

    def test_validation(self):
        r = self._create(description="short")
        self.assertEqual(r.status_code, 400)
        r = self._create(email="not-an-email")
        self.assertEqual(r.status_code, 400)

    def test_status_update(self):
        qid = self._create().data["id"]
        r = self.client.patch(f"/api/queries/{qid}/status/", {"status": "Resolved"})
        self.assertEqual(r.data["status"], "Resolved")
        r = self.client.patch(f"/api/queries/{qid}/status/", {"status": "Wrong"})
        self.assertEqual(r.status_code, 400)

    def test_analyze_fallback_matches_assignment_example(self):
        qid = self._create().data["id"]
        r = self.client.post(f"/api/queries/{qid}/analyze/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["category"], "Billing")
        self.assertEqual(r.data["priority"], "High")
        self.assertEqual(r.data["ai_source"], "fallback")
        self.assertTrue(r.data["suggested_response"])

    @override_settings(GEMINI_API_KEY="fake")
    @patch("queries.ai_service.requests.post")
    def test_analyze_with_gemini_success(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, raise_for_status=lambda: None, json=lambda: {
            "candidates": [{"content": {"parts": [{"text":
                '{"category": "billing", "priority": "HIGH", "suggested_response": "We will check your payment."}'}]}}]})
        qid = self._create().data["id"]
        r = self.client.post(f"/api/queries/{qid}/analyze/")
        self.assertEqual(r.data["ai_source"], "gemini")
        self.assertEqual(r.data["category"], "Billing")
        self.assertEqual(r.data["priority"], "High")

    @override_settings(GEMINI_API_KEY="fake")
    @patch("queries.ai_service.requests.post", side_effect=requests.ConnectionError("down"))
    def test_analyze_falls_back_when_api_down(self, _):
        qid = self._create().data["id"]
        r = self.client.post(f"/api/queries/{qid}/analyze/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["ai_source"], "fallback")

    def test_filter_search_pagination_dashboard(self):
        for i in range(12):
            self._create(customer_name=f"User{i}", email=f"u{i}@x.com")
        CustomerQuery.objects.filter(email="u0@x.com").update(status="Resolved", category="Billing")
        r = self.client.get("/api/queries/")
        self.assertEqual(r.data["count"], 12)
        self.assertEqual(len(r.data["results"]), 10)
        self.assertEqual(self.client.get("/api/queries/?status=Resolved").data["count"], 1)
        self.assertEqual(self.client.get("/api/queries/?category=Billing").data["count"], 1)
        self.assertEqual(self.client.get("/api/queries/?search=u5@x.com").data["count"], 1)
        d = self.client.get("/api/queries/dashboard/").data
        self.assertEqual((d["total"], d["pending"], d["resolved"]), (12, 11, 1))
