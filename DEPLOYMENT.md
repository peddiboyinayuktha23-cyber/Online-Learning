# Online Learning Hub Deployment Guide

## Server Packages

Install Python 3.12, PostgreSQL, Nginx, and build tools. Create a PostgreSQL database and user:

```sql
CREATE DATABASE onlinelearning;
CREATE USER onlinelearning WITH PASSWORD 'change-me';
GRANT ALL PRIVILEGES ON DATABASE onlinelearning TO onlinelearning;
```

## Environment

Create `.env.local` from `.env.example` and set:

```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=strong-production-secret
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
DATABASE_ENGINE=postgresql
POSTGRES_DB=onlinelearning
POSTGRES_USER=onlinelearning
POSTGRES_PASSWORD=change-me
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

## Build

```bash
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## Gunicorn

Example systemd service:

```ini
[Unit]
Description=Online Learning Hub
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/onlinelearning
EnvironmentFile=/var/www/onlinelearning/.env.local
ExecStart=/var/www/onlinelearning/.env/bin/gunicorn onlinelearning.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

## Nginx

```nginx
server {
    server_name your-domain.com www.your-domain.com;

    location /static/ {
        alias /var/www/onlinelearning/staticfiles/;
    }

    location /media/ {
        alias /var/www/onlinelearning/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Use Certbot or your preferred TLS provider for HTTPS. For S3 later, replace Django's default file storage with `django-storages`, add AWS credentials via environment variables, and update `MEDIA_URL`.
