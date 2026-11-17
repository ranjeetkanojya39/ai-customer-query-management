# API Documentation & Sample Requests

Interactive docs: `/api/docs/` (Swagger). Schema: `/api/schema/`.

## 1. Register — `POST /api/register/`
```bash
curl -X POST http://127.0.0.1:8000/api/register/ -H "Content-Type: application/json" \
 -d '{"username":"ranjeet","email":"ranjeet@example.com","password":"Str0ng!Pass#1","password2":"Str0ng!Pass#1"}'
```
**201**
```json
{"message":"User registered successfully.","user":{"id":1,"username":"ranjeet","email":"ranjeet@example.com"},"token":"9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
```
**400** (validation) → `{"password2":["Passwords do not match."]}`

## 2. Login — `POST /api/login/`
```bash
curl -X POST http://127.0.0.1:8000/api/login/ -H "Content-Type: application/json" \
 -d '{"username":"ranjeet","password":"Str0ng!Pass#1"}'
```
**200** → `{"message":"Login successful.","token":"<token>","user":{...}}`
**400** → `{"non_field_errors":["Invalid username or password."]}`

## 3. Create query — `POST /api/queries/`
```bash
curl -X POST http://127.0.0.1:8000/api/queries/ -H "Authorization: Token <token>" -H "Content-Type: application/json" \
 -d '{"customer_name":"Rahul Sharma","email":"rahul@example.com","subject":"Double payment","description":"My payment has been deducted twice, but my subscription is still not activated."}'
```
**201**
```json
{"id":1,"customer_name":"Rahul Sharma","email":"rahul@example.com","subject":"Double payment",
 "description":"My payment has been deducted twice, but my subscription is still not activated.",
 "category":null,"priority":null,"status":"Pending","suggested_response":"","ai_source":"",
 "created_at":"2026-11-17T10:30:00+05:30","updated_at":"2026-11-17T10:30:00+05:30"}
```

## 4. List — `GET /api/queries/?status=Pending&search=rahul&page=1`
**200**
```json
{"count":1,"next":null,"previous":null,"results":[{"id":1,"customer_name":"Rahul Sharma", "...":"..."}]}
```

## 5. Details — `GET /api/queries/1/`  → 200 (or 404 `{"detail":"No CustomerQuery matches the given query."}`)

## 6. Update — `PUT /api/queries/1/` (all required fields) or `PATCH` (partial)
```bash
curl -X PATCH http://127.0.0.1:8000/api/queries/1/ -H "Authorization: Token <token>" -H "Content-Type: application/json" -d '{"priority":"High"}'
```

## 7. Update status — `PATCH /api/queries/1/status/`
```bash
curl -X PATCH http://127.0.0.1:8000/api/queries/1/status/ -H "Authorization: Token <token>" -H "Content-Type: application/json" -d '{"status":"In Progress"}'
```
**200** → full query object with `"status":"In Progress"`. Invalid value → 400.

## 8. Delete — `DELETE /api/queries/1/` → 204 No Content

## 9. AI analysis — `POST /api/queries/1/analyze/`
```bash
curl -X POST http://127.0.0.1:8000/api/queries/1/analyze/ -H "Authorization: Token <token>"
```
**200**
```json
{"query_id":1,"category":"Billing","priority":"High",
 "suggested_response":"We apologise for the inconvenience. Our team will verify the payment transaction and help activate your subscription.",
 "ai_source":"gemini"}
```
`ai_source` is `"gemini"` when the AI API answered, `"fallback"` when the rule-based engine was used.
The result is also saved on the query (category, priority, suggested_response).

## 10. Dashboard — `GET /api/queries/dashboard/`
```json
{"total":12,"pending":8,"in_progress":2,"resolved":2}
```

## Error codes
401 not authenticated · 400 validation error · 404 not found · 503 unexpected AI failure
