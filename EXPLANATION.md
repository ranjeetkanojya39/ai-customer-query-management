# AI Integration — Short Explanation

**Which AI model/API was used?**
Google Gemini API (`gemini-2.0-flash`, configurable via `GEMINI_MODEL`) through its REST endpoint. No model training was done; I used an existing LLM and a free-tier key.

**How was it integrated with Django?**
All AI logic is isolated in `queries/ai_service.py`. The `POST /api/queries/{id}/analyze/` action in the DRF viewset loads the query, calls `analyze_query(subject, description)`, saves the returned category, priority and suggested response on the model, and returns them as JSON. The API key is read from the `GEMINI_API_KEY` environment variable (`.env`, git-ignored). Keeping the AI code in a separate service module keeps views thin and lets the provider be swapped easily.

**How is the AI response processed and interpreted?**
The prompt asks the model to reply only with JSON (`category`, `priority`, `suggested_response`) and `responseMimeType: application/json` is set to enforce it. The response is parsed, markdown fences are stripped, and every field is validated: category must be one of Technical / Billing / General / Account Related, priority one of Low / Medium / High (case-insensitive match, normalised to canonical form), and the reply must be non-empty (truncated to 500 chars). Anything invalid is treated as an AI failure.

**Fallback mechanism (bonus):**
If the key is missing, the request times out (15 s), the API errors, or the output is invalid, a keyword-based analyser produces category, priority and a template response, so the endpoint never fails. The response includes `ai_source` (`gemini` / `fallback`) for transparency.

**Challenges faced**
1. LLMs sometimes return text around JSON or different casing ("HIGH", "billing") — solved with strict prompting, JSON mime type, fence stripping and normalisation.
2. Handling API downtime/timeouts without breaking the user flow — solved with timeouts, broad exception handling and the fallback engine.
3. Testing AI code without real network calls — solved by mocking `requests.post` in unit tests (success and failure paths).
4. Keeping secrets out of source code — environment variables + `.env.example`.
