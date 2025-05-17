# Deployment Guide

This guide describes how to deploy Abigon on Ubuntu Server with Nginx, Gunicorn, PostgreSQL, and Redis.

## System Requirements

- Ubuntu Server 22.04 LTS
- Python 3.10+
- PostgreSQL 14
- Redis 6.0
- Nginx

## Installation Steps

### 1. System Packages

```bash
sudo apt update
sudo apt install python3-venv python3-dev postgresql postgresql-contrib redis-server nginx build-essential libpq-dev
```

### 2. PostgreSQL Setup

```bash
sudo -u postgres psql -c "CREATE DATABASE abigon;"
sudo -u postgres psql -c "CREATE USER abigon WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "ALTER ROLE abigon SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE abigon SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE abigon SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE abigon TO abigon;"
```

### 3. Python Environment

```bash
python3 -m venv ~/envs/abigon_env
source ~/envs/abigon_env/bin/activate
pip install -r requirements.txt
```

### 4. Gunicorn Setup

Create socket file:
```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

Content:
```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Create service file:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Content:
```ini
[Unit]
Description=Gunicorn service
Requires=gunicorn.socket
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/env/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    classifieds.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 5. Nginx Setup

Create site configuration:
```bash
sudo nano /etc/nginx/sites-available/abigon
```

Content:
```nginx
server {
    listen 80;
    server_name your_domain;

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    location /static/ {
        root /path/to/project;
    }

    location /media/ {
        root /path/to/project;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/abigon /etc/nginx/sites-enabled/
```

### 6. Final Steps

1. Collect static files:
```bash
python manage.py collectstatic
```

2. Set permissions:
```bash
sudo usermod -a -G www-data your_user
sudo chown -R your_user:www-data /path/to/project/staticfiles/
sudo chown -R your_user:www-data /path/to/project/mediafiles/
sudo chmod -R 755 /path/to/project/staticfiles/
sudo chmod -R 755 /path/to/project/mediafiles/
```

3. Start services:
```bash
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl restart nginx
```

## SSL Configuration

For SSL setup, we recommend using Let's Encrypt with Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain
```

## Monitoring

To monitor the services:

```bash
sudo systemctl status nginx
sudo systemctl status gunicorn.socket
sudo systemctl status gunicorn
sudo journalctl -u gunicorn
```

## Troubleshooting

1. Check Nginx error logs:
```bash
sudo tail -f /var/log/nginx/error.log
```

2. Check Gunicorn logs:
```bash
sudo journalctl -u gunicorn
```

3. Test Nginx configuration:
```bash
sudo nginx -t
``` 