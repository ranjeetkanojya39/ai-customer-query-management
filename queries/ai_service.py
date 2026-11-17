"""
AI integration layer.

Primary  : Google Gemini API (REST) -> returns strict JSON {category, priority, suggested_response}
Fallback : deterministic keyword-based analyser, used when the API key is missing,
           the API is down / times out, or the model returns invalid output.
The view never crashes because of the AI service.
"""
import json
import logging
import re

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

CATEGORIES = ["Technical", "Billing", "General", "Account Related"]
PRIORITIES = ["Low", "Medium", "High"]

PROMPT = """You are a customer-support triage assistant.
Analyse the customer query below and reply ONLY with a JSON object with exactly these keys:
  "category": one of ["Technical", "Billing", "General", "Account Related"],
  "priority": one of ["Low", "Medium", "High"],
  "suggested_response": a polite, professional reply of 1-2 sentences (max 300 characters).
Priority guide: High = money lost/blocked service/security/urgent; Medium = something not working but workaround exists; Low = general questions/feedback.

Subject: {subject}
Description: {description}"""


class AIServiceError(Exception):
    pass


def analyze_query(subject: str, description: str) -> dict:
    """Return {"category", "priority", "suggested_response", "source"}."""
    if settings.GEMINI_API_KEY:
        try:
            result = _analyze_with_gemini(subject, description)
            result["source"] = "gemini"
            return result
        except Exception as exc:  # network, HTTP, JSON, validation - all handled
            logger.warning("Gemini analysis failed, using fallback: %s", exc)
    result = _analyze_with_rules(subject, description)
    result["source"] = "fallback"
    return result


# ---------------------------------------------------------------- Gemini
def _analyze_with_gemini(subject, description):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": PROMPT.format(subject=subject, description=description)}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
    }
    try:
        resp = requests.post(url, json=payload, timeout=settings.AI_TIMEOUT_SECONDS,
                             headers={"x-goog-api-key": settings.GEMINI_API_KEY,
                                      "Content-Type": "application/json"})
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
        raise AIServiceError(f"Gemini request failed: {exc}") from exc
    return _parse_and_validate(text)


def _parse_and_validate(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AIServiceError(f"Model returned invalid JSON: {exc}") from exc
    category = _canonical(data.get("category"), CATEGORIES)
    priority = _canonical(data.get("priority"), PRIORITIES)
    reply = str(data.get("suggested_response", "")).strip()
    if not category or not priority or not reply:
        raise AIServiceError(f"Model output missing/invalid fields: {data}")
    return {"category": category, "priority": priority, "suggested_response": reply[:500]}


def _canonical(value, allowed):
    if not isinstance(value, str):
        return None
    for item in allowed:
        if item.lower() == value.strip().lower():
            return item
    return None


# ---------------------------------------------------------------- Fallback
CATEGORY_KEYWORDS = {
    "Billing": ["payment", "paid", "refund", "invoice", "charged", "deducted", "billing", "bill",
                "subscription", "price", "transaction", "money", "card", "debit", "credit"],
    "Account Related": ["password", "login", "log in", "sign in", "account", "username", "profile",
                        "otp", "locked", "verification", "reset", "hacked", "email change"],
    "Technical": ["error", "bug", "crash", "not working", "slow", "not loading", "app", "website",
                  "server", "down", "freez", "broken", "failed", "issue", "glitch", "install"],
}
HIGH_WORDS = ["urgent", "immediately", "asap", "twice", "deducted", "not activated", "unable", "cannot",
              "can't", "fraud", "hacked", "critical", "down", "lost", "stolen", "blocked", "emergency"]
LOW_WORDS = ["how to", "question", "feedback", "suggestion", "information", "inquiry", "enquiry",
             "thanks", "thank you", "curious", "wondering"]

RESPONSES = {
    "Billing": "We apologise for the inconvenience. Our team will verify your payment/billing details and get back to you shortly.",
    "Account Related": "Thank you for reaching out. Our team will review your account and help you regain access or resolve the issue soon.",
    "Technical": "Sorry for the trouble. Our technical team is looking into the issue and will update you as soon as it is resolved.",
    "General": "Thank you for contacting us. Our team has received your query and will respond with the details shortly.",
}


def _analyze_with_rules(subject, description):
    text = f"{subject} {description}".lower()
    scores = {cat: sum(kw in text for kw in kws) for cat, kws in CATEGORY_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    category = best if scores[best] > 0 else "General"

    if any(w in text for w in HIGH_WORDS):
        priority = "High"
    elif any(w in text for w in LOW_WORDS) or category == "General":
        priority = "Low"
    else:
        priority = "Medium"
    return {"category": category, "priority": priority, "suggested_response": RESPONSES[category]}
