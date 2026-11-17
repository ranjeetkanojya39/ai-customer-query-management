# AI-Powered Customer Query Management System

## 1. Project Overview

The AI-Powered Customer Query Management System is a backend application developed using Python, Django, and Django REST Framework.

The application allows users to register, log in, submit customer queries, and manage them through REST APIs.

It also integrates Google's Gemini AI to automatically analyse customer queries, identify their category and priority, and generate suggested responses.

If the Gemini API is unavailable or no API key is configured, the application uses a rule-based fallback mechanism to analyse queries.

## 2. Key Features

### User Management
- User registration and login.
- Django authentication system.
- Token-based authentication.
- Password validation and secure password storage.
- Protected API endpoints.

### Customer Query Management
- Create new customer queries.
- View all submitted queries.
- View individual query details.
- Update existing queries.
- Delete queries.
- Update query status.

### AI-Powered Query Analysis
- Automatically identify query categories.
- Determine query priority.
- Generate suggested customer responses.
- Integrate Google Gemini API.
- Use rule-based fallback when the AI service is unavailable.

### Additional Features
- Search queries by customer name or email.
- Filter queries by category, priority, and status.
- Pagination for query lists.
- Dashboard with query statistics.
- API unit tests.
- Swagger API documentation.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| Django | Web application framework |
| Django REST Framework | REST API development |
| SQLite | Database |
| Django Authentication | User authentication |
| Token Authentication | API security |
| Google Gemini API | AI-powered query analysis |
| Requests | HTTP requests to Gemini API |
| Python-dotenv | Environment variable management |
| django-filter | API filtering |
| drf-spectacular | Swagger API documentation |

## 4. Project Structure

```text
query_management/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── accounts/
│   ├── serializers.py
│   ├── views.py
│   └── ...
│
├── queries/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── ai_service.py
│   ├── tests.py
│   └── ...
│
├── .env.example
├── .gitignore
├── requirements.txt
├── manage.py
├── API_DOCS.md
├── EXPLANATION.md
└── README.md
```

## 5. Installation and Setup

Follow these steps to run the project locally.

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd query_management
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file by copying `.env.example`.

Windows:

```bash
copy .env.example .env
```

Open the `.env` file and configure your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key
```

Get your free API key from Google AI Studio.

Keep your API key private. Never upload your `.env` file to GitHub.

### Step 5: Apply Database Migrations

```bash
python manage.py migrate
```

### Step 6: Create an Admin Account (Optional)

```bash
python manage.py createsuperuser
```

### Step 7: Start the Development Server

```bash
python manage.py runserver
```

The application will be available at:

http://127.0.0.1:8000/

## 6. API Documentation

Swagger documentation is available at:

http://127.0.0.1:8000/api/docs/

You can explore API endpoints and test requests using the Swagger interface.

## 7. API Endpoints

### Authentication APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/register/ | Register a new user |
| POST | /api/login/ | Login and receive an authentication token |

### Customer Query APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/queries/ | Create a new query |
| GET | /api/queries/ | Retrieve all queries |
| GET | /api/queries/{id}/ | Retrieve a specific query |
| PUT | /api/queries/{id}/ | Update a query |
| PATCH | /api/queries/{id}/ | Partially update a query |
| DELETE | /api/queries/{id}/ | Delete a query |
| PATCH | /api/queries/{id}/status/ | Update query status |
| POST | /api/queries/{id}/analyze/ | Analyse query using AI |
| GET | /api/queries/dashboard/ | View query statistics |

### Authentication Header

All customer query APIs require a valid authentication token.

Include the following header in your requests:

```http
Authorization: Token your_authentication_token
```

## 8. AI Integration

The application uses Google's Gemini API to analyse customer queries.

The AI performs three main tasks:

1. Category Classification: Identifies whether a query belongs to Technical, Billing, General, or Account Related.
2. Priority Detection: Determines whether the query has Low, Medium, or High priority.
3. Response Generation: Creates a short suggested response for the customer.

### Example

Input:

"My payment has been deducted twice, but my subscription is still not activated."

Expected Output:

```json
{
    "category": "Billing",
    "priority": "High",
    "suggested_response": "We apologise for the inconvenience. Our team will verify the payment transaction and help activate your subscription.",
    "ai_source": "gemini"
}
```

### AI Fallback Mechanism

If the Gemini API is unavailable or the API key is not configured, the application uses a rule-based fallback mechanism.

This helps the application continue analysing customer queries without depending entirely on the external AI service.

## 9. Search, Filtering and Pagination

The query listing API supports additional query parameters.

Examples:

Search by customer name or email:

```text
/api/queries/?search=rahul
```

Filter by category:

```text
/api/queries/?category=Billing
```

Filter by priority:

```text
/api/queries/?priority=High
```

Filter by status:

```text
/api/queries/?status=Pending
```

Pagination:

```text
/api/queries/?page=2
```

Ordering:

```text
/api/queries/?ordering=-created_at
```

## 10. Running Tests

To run the project's automated tests, execute:

```bash
python manage.py test
```

This command runs the available Django application tests.

## 11. Security

The application follows basic security practices:

- Sensitive information is stored in environment variables.
- API keys are not included in source code.
- The `.env` file is excluded using `.gitignore`.
- Django password validators are used.
- Passwords are stored using Django's secure password hashing.
- Authentication tokens protect customer query APIs.

## 12. Future Improvements

Possible future enhancements include:

- Frontend dashboard for administrators.
- Email notifications for query updates.
- Advanced AI-based query analysis.
- Role-based access control.
- Deployment to a cloud platform.

## 13. Author

**Ranjeet Kanojiya**

Python | Django | Django REST Framework | MySQL | REST APIs | AI Integration

GitHub: github.com/ranjeetkanojya39

---

**Project:** AI-Powered Customer Query Management System

**Framework:** Django & Django REST Framework

**Language:** Python
