# 🚀 Guide d'Installation - BabiCouture

Suivez ce guide étape par étape pour installer et configurer BabiCouture.

## Table des matières

- [Prérequis](#prérequis)
- [Installation Locale](#installation-locale)
- [Installation avec Docker](#installation-avec-docker)
- [Configuration](#configuration)
- [Vérification](#vérification)
- [Résolution des problèmes](#résolution-des-problèmes)

---

## Prérequis

### Windows / macOS / Linux

Assurez-vous d'avoir installé :

- **Python 3.8+** : [python.org](https://www.python.org/downloads/)
  - Vérifier : `python --version`
- **pip** (gestionnaire de paquets Python)
  - Vérifier : `pip --version`
- **Git** : [git-scm.com](https://git-scm.com/)
  - Vérifier : `git --version`

### Optionnel mais recommandé

- **Docker** : [docker.com](https://www.docker.com/)
- **Docker Compose** : [docs.docker.com/compose](https://docs.docker.com/compose/install/)
- **PostgreSQL** : [postgresql.org](https://www.postgresql.org/download/)

---

## Installation Locale

### 1. Cloner le projet

```bash
git clone <url-du-repository>
cd BABI-project2
```

### 2. Créer un environnement virtuel

**Windows :**

```cmd
python -m venv env
env\Scripts\activate
```

**macOS / Linux :**

```bash
python3 -m venv env
source env/bin/activate
```

Vous devriez voir `(env)` au début de votre ligne de commande.

### 3. Mettre à jour pip

```bash
pip install --upgrade pip
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

**⏱️ Temps estimé :** 3-5 minutes

Vous verrez des messages comme :

```
Successfully installed Django-4.2.8
Successfully installed djangorestframework-3.14.0
...
```

### 5. Créer le fichier `.env`

Copier `.env.example` vers `.env` :

**Windows :**

```cmd
copy .env.example .env
```

**macOS / Linux :**

```bash
cp .env.example .env
```

Éditer `.env` et adapter les valeurs (gardez les valeurs par défaut pour le développement) :

```env
DEBUG=True
SECRET_KEY=django-insecure-pmjayra0oq1lap6-_&_0ct5k9akyui!1%1!qtez3lsma%o8!$p
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### 6. Créer la base de données

```bash
python manage.py makemigrations
python manage.py migrate
```

**Output :**

```
Operations to perform:
  Apply all migrations: admin, auth, catalog, core, messaging, orders, reviews, sessions, users
...
Running migrations:
  Applying admin.0001_initial... OK
  ...
```

### 7. Créer un compte administrateur

```bash
python manage.py createsuperuser
```

Suivez les prompts :

```
Username: admin
Email address: admin@example.com
Password: ••••••••••
Password (again): ••••••••••
Superuser created successfully.
```

### 8. Créer des données de test (optionnel)

```bash
python manage.py shell
```

```python
from users.models import Client, Couturier
from django.contrib.auth.models import User

# Créer un utilisateur client
user_client = User.objects.create_user(
    username='john',
    email='john@example.com',
    password='password123',
    first_name='John',
    last_name='Doe'
)
Client.objects.create(user=user_client)

# Créer un utilisateur couturier
user_tailor = User.objects.create_user(
    username='marie',
    email='marie@example.com',
    password='password123',
    first_name='Marie',
    last_name='Diallo'
)
Couturier.objects.create(
    user=user_tailor,
    nom_atelier="Atelier de Luxe",
    specialite="Robes de soirée"
)

exit()
```

### 9. Lancer le serveur

```bash
python manage.py runserver
```

**Output :**

```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### 10. Accéder à l'application

- **Frontend** : http://localhost:8000
- **Admin** : http://localhost:8000/admin (utilisateur : admin)

---

## Installation avec Docker

### 1. Prérequis Docker

Vérifiez que Docker et Docker Compose sont installés :

```bash
docker --version
docker-compose --version
```

### 2. Cloner le projet

```bash
git clone <url-du-repository>
cd BABI-project2
```

### 3. Créer le fichier `.env`

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Adapter les valeurs pour PostgreSQL :

```env
DEBUG=False
SECRET_KEY=your-secure-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=babicouture
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/0
```

### 4. Build et lancer les conteneurs

```bash
docker-compose up -d
```

**Attendez 30-60 secondes** pour que tous les services démarrent.

### 5. Vérifier le statut

```bash
docker-compose ps
```

Vous devriez voir :

```
NAME                    STATUS
babicouture_db          Up (healthy)
babicouture_redis       Up (healthy)
babicouture_web         Up
babicouture_celery      Up
babicouture_nginx       Up
```

### 6. Créer un superutilisateur

```bash
docker-compose exec web python manage.py createsuperuser
```

### 7. Charger les données initiales (optionnel)

```bash
docker-compose exec web python manage.py loaddata initial_data
```

### 8. Accéder à l'application

- **Frontend** : http://localhost (via Nginx)
- **Admin** : http://localhost/admin
- **pgAdmin** : http://localhost:5050 (gérer la BD)

### Commandes Docker utiles

```bash
# Voir les logs
docker-compose logs -f web

# Exécuter des commandes Django
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py shell

# Arrêter les services
docker-compose down

# Supprimer les volumes (données)
docker-compose down -v

# Reconstruire les images
docker-compose build --no-cache
```

---

## Configuration

### Configuration d'Email (optionnel)

#### Avec Gmail

1. Activer 2FA et créer un [mot de passe d'application](https://myaccount.google.com/apppasswords)

2. Éditer `.env` :

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

3. Tester dans Django shell :

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test message.',
    'your-email@gmail.com',
    ['recipient@example.com'],
    fail_silently=False,
)
```

### Configuration de Base de Données PostgreSQL

1. Installer PostgreSQL

2. Créer une base de données et utilisateur :

```sql
CREATE DATABASE babicouture;
CREATE USER babicouture_user WITH PASSWORD 'password';
ALTER ROLE babicouture_user SET client_encoding TO 'utf8';
ALTER ROLE babicouture_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE babicouture_user SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE babicouture TO babicouture_user;
```

3. Éditer `.env` :

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=babicouture
DB_USER=babicouture_user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

4. Installer le driver PostgreSQL :

```bash
pip install psycopg2-binary
```

5. Lancer les migrations :

```bash
python manage.py migrate
```

---

## Vérification

### Vérifier que tout fonctionne

#### 1. Tests unitaires

```bash
python manage.py test
```

**Attendez 1-2 minutes :**

```
Creating test database for alias 'default'...
...
Ran 15 tests in 2.345s

OK
```

#### 2. Tests spécifiques

```bash
# Tests du service Users
python manage.py test users

# Tests du service Orders
python manage.py test orders

# Avec verbosité
python manage.py test --verbosity=2
```

#### 3. Vérifier la base de données

```bash
python manage.py dbshell
```

```sql
-- Voir les tables
\dt

-- Voir les utilisateurs
SELECT * FROM auth_user;

-- Sortir
\q
```

### Vérifier les endpoints

#### Accueil

```bash
curl http://localhost:8000/
```

#### Login admin

```bash
curl -X POST http://localhost:8000/users/login/ \
  -d "username=admin&password=admin_password"
```

#### Lister les couturiers

```bash
curl http://localhost:8000/users/couturiers/
```

---

## Résolution des Problèmes

### Erreur : "No module named 'django'"

**Solution :**

```bash
# Vérifier l'environnement virtuel est activé
# Windows: env\Scripts\activate
# macOS/Linux: source env/bin/activate

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur : "database is locked"

**Solution :**

```bash
# Supprimer la base de données et la recréer
rm db.sqlite3

# Ou si vous utilisez PostgreSQL, redémarrer le service
```

### Erreur : "No such table: auth_user"

**Solution :**

```bash
python manage.py migrate
```

### Erreur : "SECRET_KEY not found"

**Solution :**

```bash
# Créer le fichier .env
cp .env.example .env

# Ou définir la variable d'environnement
export SECRET_KEY="your-secret-key"
```

### Erreur : "Port 8000 already in use"

**Solution :**

```bash
# Utiliser un autre port
python manage.py runserver 8001

# Ou tuer le processus existant
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### Erreur Docker : "Cannot connect to database"

**Solution :**

```bash
# Attendre que la base de données soit prête
docker-compose logs db

# Redémarrer les services
docker-compose down
docker-compose up -d

# Vérifier la connexion
docker-compose exec web python manage.py dbshell
```

### Page blanche ou erreur 500

**Solution :**

```bash
# Vérifier les logs
python manage.py runserver --verbosity=2

# Ou avec Docker
docker-compose logs -f web

# Aller dans Django shell et tester
python manage.py shell
```

---

## ✅ Checklist d'Installation

- [ ] Python 3.8+ installé
- [ ] Environnement virtuel créé
- [ ] Dépendances installées
- [ ] `.env` créé et configuré
- [ ] Migrations appliquées
- [ ] Superutilisateur créé
- [ ] Serveur lancé avec succès
- [ ] Page d'accueil accessible
- [ ] Admin accessible
- [ ] Tests passent

---

## Prochaines étapes

1. Consulter [README.md](README.md) pour la vue d'ensemble
2. Consulter [ARCHITECTURE.md](ARCHITECTURE.md) pour comprendre la structure
3. Consulter [API_DOCUMENTATION.md](API_DOCUMENTATION.md) pour les endpoints
4. Lire [CONTRIBUTING.md](CONTRIBUTING.md) pour contribuer

---

## Besoin d'aide ?

- 📖 Consultez la [documentation Django](https://docs.djangoproject.com/)
- 🐛 Ouvrez une issue sur GitHub
- 💬 Contactez le support

**Bonne installation ! 🎉**

---

Dernière mise à jour : Avril 2026
