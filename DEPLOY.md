# NamAirSales — Deployment Guide (Ubuntu)

Stack: **gunicorn** (app server) + **nginx** (reverse proxy) + **PostgreSQL** + **systemd** (process manager)

---

## Common pitfalls before you start

### SECRET_KEY with `$` breaks django-environ

`django-environ` treats `$` in unquoted `.env` values as shell variable
interpolation. A key like `...b50$7gwx...` turns `$7` into an empty string,
so Django receives a blank key and raises:

```
ImproperlyConfigured: Set the SECRET_KEY environment variable
```

**Rule:** always wrap the SECRET_KEY value in single quotes in `.env`:

```env
SECRET_KEY='your-key-here'
```

**Rule:** never use `python manage.py generate-secret-key` or any key that
contains a `$`. Generate one that doesn't:

```bash
source venv/bin/activate
python -c "
from django.core.management.utils import get_random_secret_key
for _ in range(50):
    k = get_random_secret_key()
    if '\$' not in k:
        print(k); break
"
```

---

## 1. Install system packages

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    python3 python3-venv python3-pip \
    postgresql postgresql-contrib \
    nginx \
    git
```

---

## 2. Create a PostgreSQL database

```bash
sudo -u postgres psql
```

Inside the psql shell:

```sql
CREATE USER namairsales WITH PASSWORD 'choose_a_strong_password';
CREATE DATABASE namairsales OWNER namairsales;
\q
```

---

## 3. Create a dedicated system user

```bash
sudo useradd --system --shell /bin/bash --home /srv/namairsales namairsales
sudo mkdir -p /srv/namairsales
sudo chown namairsales:namairsales /srv/namairsales
```

---

## 4. Clone the repository

```bash
sudo -u namairsales git clone https://github.com/YOUR_USERNAME/namairsales.git /srv/namairsales/app
```

---

## 5. Set up the Python environment

```bash
cd /srv/namairsales/app
sudo -u namairsales python3 -m venv venv
sudo -u namairsales venv/bin/pip install -r requirements.txt
```

---

## 6. Create `.env` on the server

```bash
sudo -u namairsales nano /srv/namairsales/app/.env
```

```env
SECRET_KEY='paste-a-dollar-free-key-in-single-quotes'
DEBUG=False
ALLOWED_HOSTS=192.168.1.100,namairsales.local
DATABASE_URL=postgres://namairsales:choose_a_strong_password@localhost/namairsales
```

> Find your server's LAN IP with: `ip a | grep 'inet ' | grep -v 127`

---

## 7. Initialize the application

```bash
cd /srv/namairsales/app
sudo -u namairsales venv/bin/python manage.py migrate
sudo -u namairsales venv/bin/python manage.py collectstatic --noinput
sudo -u namairsales venv/bin/python manage.py createsuperuser
```

---

## 8. Create a systemd service

```bash
sudo nano /etc/systemd/system/namairsales.service
```

```ini
[Unit]
Description=NamAirSales gunicorn daemon
After=network.target postgresql.service

[Service]
User=namairsales
Group=namairsales
WorkingDirectory=/srv/namairsales/app
ExecStart=/srv/namairsales/app/venv/bin/gunicorn \
    config.wsgi:application \
    --bind unix:/srv/namairsales/namairsales.sock \
    --workers 3
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable namairsales
sudo systemctl start namairsales
sudo systemctl status namairsales
```

`Active: active (running)` means it's working.

---

## 9. Configure nginx

```bash
sudo nano /etc/nginx/sites-available/namairsales
```

```nginx
server {
    listen 80;
    server_name 192.168.1.100;

    location / {
        proxy_pass http://unix:/srv/namairsales/namairsales.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/namairsales /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Open `http://192.168.1.100` in a browser — the app should load.

---

## 10. One-command updates

### Create the deploy script

```bash
sudo -u namairsales nano /srv/namairsales/app/deploy.sh
```

```bash
#!/bin/bash
set -e
cd /srv/namairsales/app

git pull
venv/bin/pip install -r requirements.txt -q
venv/bin/python manage.py migrate --noinput
venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart namairsales

echo "Deployed."
```

```bash
sudo chmod +x /srv/namairsales/app/deploy.sh
```

### Allow passwordless service restart

```bash
sudo visudo
```

Add at the bottom:

```
namairsales ALL=(ALL) NOPASSWD: /bin/systemctl restart namairsales
```

### Deploy any update

From your dev machine:

```bash
git push
```

On the server (SSH in, then):

```bash
sudo -u namairsales /srv/namairsales/app/deploy.sh
```

---

## Quick reference

| Task | Command |
|------|---------|
| View live logs | `sudo journalctl -u namairsales -f` |
| Restart app | `sudo systemctl restart namairsales` |
| Restart nginx | `sudo systemctl restart nginx` |
| Open DB shell | `cd /srv/namairsales/app && sudo -u namairsales venv/bin/python manage.py dbshell` |
| Check config | `cd /srv/namairsales/app && sudo -u namairsales venv/bin/python manage.py check --deploy` |
