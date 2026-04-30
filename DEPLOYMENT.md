# 🚀 Guide de Déploiement - BabiCouture

Guide complet pour déployer BabiCouture en production sur différentes plateformes.

## Table des matières

- [Checklist Pre-Deployment](#checklist-pre-deployment)
- [Déploiement Local/VPS](#déploiement-localvps)
- [Déploiement Docker](#déploiement-docker)
- [Déploiement Heroku](#déploiement-heroku)
- [Déploiement AWS](#déploiement-aws)
- [Monitoring & Maintenance](#monitoring--maintenance)

---

## Checklist Pre-Deployment

### Sécurité

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` défini et sécurisé
- [ ] `ALLOWED_HOSTS` configuré correctement
- [ ] HTTPS/SSL certificat valide
- [ ] Base de données PostgreSQL (pas SQLite)
- [ ] Redis sécurisé (pas accessible publiquement)
- [ ] Secrets stockés dans `.env` (pas commités)
- [ ] CORS configuré pour votre domaine

### Performance

- [ ] Static files collectés (`collectstatic`)
- [ ] Gzip compression activé
- [ ] Cache configuré (Redis)
- [ ] Database indexes créés
- [ ] CDN configuré (optionnel)
- [ ] Rate limiting activé

### Monitoring

- [ ] Logging configuré
- [ ] Error tracking (Sentry)
- [ ] Uptime monitoring
- [ ] Database backups automatiques
- [ ] Application health checks

---

## Déploiement Local/VPS

### Architecture recommandée

```
Internet
  ↓
Nginx (Reverse Proxy)
  ↓
Gunicorn Workers
  ↓
Django Application
  ↓
PostgreSQL + Redis
```

### 1. Configuration du serveur

**Ubuntu 20.04+**

```bash
# Mises à jour
sudo apt update && sudo apt upgrade -y

# Installer les dépendances
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server curl

# Vérifier les installations
python3 --version
psql --version
nginx -v
redis-cli --version
```

### 2. Cloner le projet

```bash
# Créer le répertoire d'application
sudo mkdir -p /var/www/babicouture
sudo chown $USER:$USER /var/www/babicouture

# Cloner le repo
cd /var/www/babicouture
git clone <your-repo-url> .
```

### 3. Créer l'environnement virtuel

```bash
cd /var/www/babicouture

# Créer venv
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurer PostgreSQL

```bash
# Connecter à PostgreSQL
sudo -i -u postgres

# Créer la base de données et utilisateur
createdb babicouture
createuser babicouture_user
psql

# Dans psql:
ALTER USER babicouture_user WITH PASSWORD 'your-secure-password';
ALTER ROLE babicouture_user SET client_encoding TO 'utf8';
ALTER ROLE babicouture_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE babicouture_user SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE babicouture TO babicouture_user;
\q

# Quitter l'utilisateur postgres
exit
```

### 5. Configurer Django

```bash
# Créer .env
cd /var/www/babicouture
cat > .env << EOF
DEBUG=False
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=babicouture
DB_USER=babicouture_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0
EOF

# Migrations
source venv/bin/activate
python manage.py migrate

# Créer superuser
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Vérifier que tout fonctionne
python manage.py check --deploy
```

### 6. Configurer Gunicorn

```bash
# Créer un fichier de configuration
sudo cat > /var/www/babicouture/gunicorn.conf.py << 'EOF'
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
EOF

# Créer le répertoire des logs
sudo mkdir -p /var/log/gunicorn
sudo chown $USER:$USER /var/log/gunicorn
```

### 7. Créer un service Gunicorn

```bash
# Créer le fichier de service
sudo cat > /etc/systemd/system/gunicorn.service << 'EOF'
[Unit]
Description=BabiCouture Gunicorn Application Server
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/babicouture
ExecStart=/var/www/babicouture/venv/bin/gunicorn \
    --config /var/www/babicouture/gunicorn.conf.py \
    gateway.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Activer le service
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

### 8. Configurer Nginx

```bash
# Créer la configuration Nginx
sudo cp nginx.conf /etc/nginx/sites-available/babicouture

# Activer le site
sudo ln -s /etc/nginx/sites-available/babicouture /etc/nginx/sites-enabled/

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
```

### 9. Configurer SSL/TLS (Let's Encrypt)

```bash
# Installer Certbot
sudo apt install -y certbot python3-certbot-nginx

# Générer le certificat
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Vérifier le renouvellement automatique
sudo systemctl status certbot.timer
```

### 10. Configurer Celery (Tâches asynchrones)

```bash
# Créer un service Celery
sudo cat > /etc/systemd/system/celery.service << 'EOF'
[Unit]
Description=BabiCouture Celery Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/babicouture
ExecStart=/var/www/babicouture/venv/bin/celery \
    -A gateway worker \
    -l info

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Créer un service Celery Beat (tâches planifiées)
sudo cat > /etc/systemd/system/celery-beat.service << 'EOF'
[Unit]
Description=BabiCouture Celery Beat Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/babicouture
ExecStart=/var/www/babicouture/venv/bin/celery \
    -A gateway beat \
    -l info \
    -s /var/run/celery/beat-schedule

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Activer les services
sudo systemctl daemon-reload
sudo systemctl enable celery celery-beat
sudo systemctl start celery celery-beat
```

---

## Déploiement Docker

### 1. Build l'image

```bash
# Depuis la racine du projet
docker build -t babicouture:latest .
```

### 2. Lancer avec Docker Compose

```bash
# Créer .env
cp .env.example .env

# Éditer .env pour production
nano .env

# Lancer
docker-compose up -d

# Vérifier le statut
docker-compose ps

# Voir les logs
docker-compose logs -f web
```

### 3. Initialiser la base de données

```bash
# Migrations
docker-compose exec web python manage.py migrate

# Créer admin
docker-compose exec web python manage.py createsuperuser

# Collecter statiques
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Arrêter et nettoyer

```bash
# Arrêter les services
docker-compose down

# Supprimer les volumes (données)
docker-compose down -v

# Voir les logs d'erreur
docker-compose logs --tail=100 web
```

---

## Déploiement Heroku

### 1. Prérequis

```bash
# Installer Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Se connecter
heroku login

# Vérifier l'installation
heroku --version
```

### 2. Créer l'app Heroku

```bash
# Créer l'application
heroku create babicouture-app

# Voir l'URL
heroku info

# Ajouter les remotes
heroku git:remote -a babicouture-app
```

### 3. Configurer les variables d'environnement

```bash
# Set variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
heroku config:set ALLOWED_HOSTS=babicouture-app.herokuapp.com

# Ajouter PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# Ajouter Redis
heroku addons:create heroku-redis:premium-0

# Vérifier les variables
heroku config
```

### 4. Configurer Procfile

```bash
# Créer Procfile à la racine
cat > Procfile << 'EOF'
web: gunicorn gateway.wsgi
worker: celery -A gateway worker
beat: celery -A gateway beat
EOF

# Commiter
git add Procfile
git commit -m "Add Procfile for Heroku"
```

### 5. Déployer

```bash
# Push vers Heroku
git push heroku main

# Voir les logs
heroku logs --tail

# Lancer les migrations
heroku run python manage.py migrate

# Créer admin
heroku run python manage.py createsuperuser
```

---

## Déploiement AWS

### Option 1 : EC2 + RDS + ElastiCache

```bash
# 1. Lancer une instance EC2 (Ubuntu 20.04)
# 2. Créer une RDS PostgreSQL instance
# 3. Créer un ElastiCache Redis cluster
# 4. Configurer Security Groups
# 5. Suivre le guide "Déploiement Local/VPS" ci-dessus

# Dans .env :
# DB_HOST=your-rds-endpoint.amazonaws.com
# REDIS_URL=redis://your-elasticache-endpoint:6379
```

### Option 2 : Elastic Beanstalk

```bash
# Installer EB CLI
pip install awsebcli

# Initialiser l'application
eb init -p python-3.10 babicouture

# Créer l'environnement
eb create babicouture-env

# Configurer les variables
eb setenv DEBUG=False SECRET_KEY=... ALLOWED_HOSTS=...

# Déployer
eb deploy

# Voir les logs
eb logs

# SSH dans l'instance
eb ssh
```

### Option 3 : ECS (Elastic Container Service)

```bash
# Pousser l'image Docker vers ECR
aws ecr get-login-password --region us-east-1 | docker login \
    --username AWS \
    --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag babicouture:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/babicouture:latest

docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/babicouture:latest

# Créer une ECS task definition
# Créer un ECS service
# Configurer ALB (Application Load Balancer)
```

---

## Monitoring & Maintenance

### 1. Monitoring avec Sentry

```bash
# Installer Sentry SDK
pip install sentry-sdk

# Configurer dans settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False
)
```

### 2. Logs & Monitoring

```bash
# Voir les logs en temps réel
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/log/nginx/error.log

# Avec Docker
docker-compose logs -f web
docker-compose logs -f celery

# Statistiques Redis
redis-cli info
```

### 3. Backups automatiques

```bash
# PostgreSQL backup script
cat > /usr/local/bin/backup-babicouture.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U babicouture_user babicouture > /backups/babicouture_$DATE.sql
# Upload to S3 or cloud storage
EOF

# Rendre exécutable
chmod +x /usr/local/bin/backup-babicouture.sh

# Ajouter à crontab pour 3h du matin tous les jours
0 3 * * * /usr/local/bin/backup-babicouture.sh
```

### 4. Health Checks

```bash
# Créer une health check endpoint
# Dans core/urls.py:
path('health/', health_check, name='health_check'),

# Vérifier régulièrement
curl http://localhost:8000/health/

# Avec Monitoring (ex: UptimeRobot)
# Ajouter l'URL comme endpoint à monitorer
```

### 5. Performance Monitoring

```bash
# Avec Django Debug Toolbar (développement uniquement)
pip install django-debug-toolbar

# Avec New Relic (production)
pip install newrelic

# Lancer avec New Relic
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn gateway.wsgi
```

---

## Checklist Post-Deployment

- [ ] Site accessible via HTTPS
- [ ] Admin accessible et fonctionnel
- [ ] Base de données connectée
- [ ] Cache (Redis) fonctionnel
- [ ] Emails fonctionnels
- [ ] Celery workers actifs
- [ ] Logs se créent correctement
- [ ] Backups programmés
- [ ] Monitoring actif
- [ ] Performance acceptable (< 500ms)
- [ ] Aucune erreur 500 dans les logs

---

## Troubleshooting Production

### Problème : Site 500 Error

```bash
# Vérifier les logs
sudo tail -f /var/log/gunicorn/error.log

# Vérifier la base de données
python manage.py dbshell

# Vérifier les migrations
python manage.py showmigrations

# Redémarrer le service
sudo systemctl restart gunicorn
```

### Problème : Lent

```bash
# Vérifier les queries Django
python manage.py shell
from django.db import connection
from django.db import reset_queries
reset_queries()
# Exécuter du code...
print(len(connection.queries))
print(connection.queries)

# Vérifier Redis
redis-cli info stats

# Vérifier la CPU/Mémoire
top
```

### Problème : Base de données pleine

```bash
# Vérifier la taille
psql -U babicouture_user -d babicouture -c "SELECT pg_size_pretty(pg_database_size('babicouture'));"

# Nettoyer les old sessions
python manage.py clearsessions

# Nettoyer les logs
TRUNCATE django_admin_log;
```

---

## Ressources Utiles

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**Dernière mise à jour** : Avril 2026
