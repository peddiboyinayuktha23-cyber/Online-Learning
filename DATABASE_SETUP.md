# Online Learning Portal Database Setup

This project is configured for Django, PostgreSQL, environment variables, a custom email-login user model, media uploads, and production-ready app boundaries.

## 1. Installation and Project Commands

Windows PowerShell:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
pip install django
pip install psycopg2-binary
pip install python-dotenv
pip install Pillow
pip freeze > requirements.txt
django-admin startproject onlinelearning .
python manage.py startapp accounts
python manage.py startapp courses
python manage.py startapp enrollments
python manage.py startapp payments
python manage.py startapp reviews
python manage.py startapp certificates
python manage.py startapp notifications
```

Linux/macOS:

```bash
python3 -m venv env
source env/bin/activate
pip install django
pip install psycopg2-binary
pip install python-dotenv
pip install Pillow
pip freeze > requirements.txt
django-admin startproject onlinelearning .
python manage.py startapp accounts
python manage.py startapp courses
python manage.py startapp enrollments
python manage.py startapp payments
python manage.py startapp reviews
python manage.py startapp certificates
python manage.py startapp notifications
```

## 2. PostgreSQL Setup

Example credentials used by `onlinelearning/.env.local`:

```text
DATABASE_NAME=online_learning
DATABASE_USER=postgres
DATABASE_PASSWORD=securepassword
```

Windows with `psql`:

```powershell
psql -U postgres
CREATE DATABASE online_learning;
ALTER USER postgres WITH PASSWORD 'securepassword';
GRANT ALL PRIVILEGES ON DATABASE online_learning TO postgres;
\q
```

Linux:

```bash
sudo -u postgres psql
CREATE DATABASE online_learning;
ALTER USER postgres WITH PASSWORD 'securepassword';
GRANT ALL PRIVILEGES ON DATABASE online_learning TO postgres;
\q
```

macOS with Homebrew PostgreSQL:

```bash
brew services start postgresql
psql postgres
CREATE DATABASE online_learning;
ALTER USER postgres WITH PASSWORD 'securepassword';
GRANT ALL PRIVILEGES ON DATABASE online_learning TO postgres;
\q
```

For a stricter production database user:

```sql
CREATE DATABASE online_learning;
CREATE USER online_learning_user WITH PASSWORD 'use-a-long-random-password';
ALTER ROLE online_learning_user SET client_encoding TO 'utf8';
ALTER ROLE online_learning_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE online_learning_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE online_learning TO online_learning_user;
```

Then update `.env.local` or production environment variables.

## 3. Environment Configuration

The project loads `onlinelearning/.env.local` first. A `.env` path already exists as a virtual environment folder in this workspace, so the real dotenv file is named `.env.local`.

For immediate local development without PostgreSQL installed, use:

```text
DATABASE_ENGINE=sqlite
SQLITE_DATABASE_NAME=local.sqlite3
```

For PostgreSQL development or production, use:

```text
DATABASE_ENGINE=postgresql
```

Important production values:

```text
DJANGO_SECRET_KEY=replace-this-with-a-long-random-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
DATABASE_NAME=online_learning
DATABASE_USER=online_learning_user
DATABASE_PASSWORD=change-me
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
```

## 4. Migrations

Run these after PostgreSQL is running:

```powershell
.\env\Scripts\python.exe manage.py makemigrations
.\env\Scripts\python.exe manage.py migrate
.\env\Scripts\python.exe manage.py createsuperuser
```

Linux/macOS:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 4.1 API Setup

The REST API is available under:

```text
/api/v1/
```

Core API endpoints:

```text
POST /api/v1/auth/register/
GET  /api/v1/users/me/
PATCH /api/v1/users/me/
GET  /api/v1/categories/
GET  /api/v1/courses/
GET  /api/v1/courses/<slug>/
GET  /api/v1/ratings/
GET/POST /api/v1/enrollments/
GET/POST /api/v1/wishlist/
GET/POST /api/v1/reviews/
GET /api/v1/certificates/
GET /api/v1/notifications/
```

Private endpoints are scoped to the logged-in user unless the request comes from an admin account. Admin-only endpoints include course content management internals, coupons, and payment transactions.

API files:

```text
api/serializers.py    database-to-JSON serializers
api/views.py          viewsets, permissions, query optimization
api/urls.py           versioned API router
api/permissions.py    owner/admin API access rules
```

DRF browser login is enabled at:

```text
/api-auth/login/
```

## 5. Common Migration Fixes

Custom user model issues:

- Keep `AUTH_USER_MODEL = "accounts.CustomUser"` before the first production migration.
- Do not import `CustomUser` directly in models from other apps. Use `settings.AUTH_USER_MODEL`.
- If you already migrated with Django's default `auth.User`, create a fresh database for development or write a planned data migration before production.

Migration conflicts:

```bash
python manage.py makemigrations --merge
python manage.py showmigrations
python manage.py migrate
```

Missing tables:

```bash
python manage.py showmigrations
python manage.py migrate --plan
python manage.py migrate
```

App registry or circular import errors:

- Use string relations like `"courses.Course"` and `"enrollments.Enrollment"`.
- Keep reusable helpers in the same app or utility modules that do not import models too early.

PostgreSQL connection refused:

- Start the PostgreSQL service.
- Confirm `DATABASE_HOST`, `DATABASE_PORT`, user, password, and database name.
- Test with `psql -h 127.0.0.1 -U postgres -d online_learning`.

## 6. Query Optimization Notes

Use `select_related` for single-valued relations:

```python
Course.objects.select_related("instructor", "category").filter(is_published=True)
Enrollment.objects.select_related("student", "course").filter(student=request.user)
Payment.objects.select_related("student", "enrollment", "coupon")
```

Use `prefetch_related` for collections:

```python
Course.objects.prefetch_related("sections__lessons", "reviews")
CourseProgress.objects.prefetch_related("completed_lessons")
```

Use pagination for course, review, payment, and notification lists before exposing them to users.

## 7. Final App Structure

```text
accounts/        custom user model, student/instructor profiles, email login, roles, admin
courses/         categories, courses, sections, lessons, video, resources, quizzes, assignments
enrollments/     enrollments, wishlist, Progress model, completed courses
payments/        coupons, payments, transactions, subscriptions
reviews/         reviews, rating summaries, replies
certificates/    certificates, verification codes, PDFs
notifications/   in-app and email notifications
```

## 8. Security Checklist

- Keep secrets in environment variables, not source code.
- Keep `DEBUG=False` in production.
- Use Django ORM parameterization instead of raw SQL string interpolation.
- Serve private media through protected views or signed storage URLs in production.
- Use HTTPS and secure cookies in production.
- Keep CSRF middleware enabled.
- Let Django hash passwords through `set_password`, forms, or admin.
