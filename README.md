# Online Learning Hub

A production-oriented Django 5 e-learning platform with PostgreSQL, Django REST Framework, JWT authentication, Bootstrap templates, role-based dashboards, course management, enrollments, reviews, certificates, notifications, and payment-ready models for Stripe, Razorpay, and PayPal.

## Features

- Custom email-login user model with `STUDENT`, `INSTRUCTOR`, and `ADMIN` roles
- Public homepage, course catalog, search/filtering, course detail, about, contact, privacy, and terms pages
- Student workflows: enrollments, progress, submissions, certificates, notifications, and profile management
- Instructor workflows: course, lesson, quiz, assignment, resource, student, review, and revenue management foundations
- Admin workflows through Django Admin for users, courses, categories, payments, certificates, notifications, and reports
- REST API under `/api/v1/` with JWT endpoints, pagination, search, ordering, and role-aware querysets
- Local media storage with settings ready to swap to S3 later
- Production settings for PostgreSQL, static collection, WhiteNoise, Gunicorn, and Nginx

## Local Setup

```powershell
cd "C:\Users\yukth\OneDrive\Desktop\Online Learning\onlinelearning"
.\.env\Scripts\activate
pip install -r requirements.txt
copy .env.example .env.local
```

For local SQLite development set this in `.env.local`:

```env
DATABASE_ENGINE=sqlite
DJANGO_DEBUG=True
```

Then run:

```powershell
python manage.py migrate
python manage.py loaddata fixtures/sample_data.json
python manage.py createsuperuser
python manage.py runserver
```

## API

- Register: `POST /api/v1/auth/register/`
- Login: `POST /api/v1/auth/login/`
- Refresh token: `POST /api/v1/auth/token/refresh/`
- Courses: `/api/v1/courses/`
- Lessons: `/api/v1/lessons/`
- Enrollments: `/api/v1/enrollments/`
- Reviews: `/api/v1/reviews/`
- Certificates: `/api/v1/certificates/`
- Payments: `/api/v1/payments/`
- Notifications: `/api/v1/notifications/`

Use JWT as `Authorization: Bearer <access_token>`.

## Search And Filtering

Course filtering works in templates and API:

```text
/courses/?q=python&category=development&level=BEGINNER&min_price=10&max_price=100&rating=4
/api/v1/courses/?search=python&category=development&level=BEGINNER&min_price=10&max_price=100&min_rating=4
```

## Tests

```powershell
python manage.py test accounts courses api
```

## Deployment

See `DEPLOYMENT.md` for PostgreSQL, Gunicorn, Nginx, static/media, and environment variable guidance.
