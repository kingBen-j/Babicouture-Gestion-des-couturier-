# ⚡ Quick Start Guide - BabiCouture

Le moyen le plus rapide de se lancer avec BabiCouture !

## 5 minutes pour démarrer

### Option 1 : Développement Local (Recommandé pour apprendre)

```bash
# 1. Clone le projet
git clone <url-du-repo>
cd BABI-project2

# 2. Créer l'environnement virtuel
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Initialiser la base de données
python manage.py migrate
python manage.py createsuperuser  # Username: admin, Password: admin

# 5. Lancer le serveur
python manage.py runserver

# 6. Accédez à :
#    http://localhost:8000 (Frontend)
#    http://localhost:8000/admin (Admin)
```

### Option 2 : Docker (Production-ready)

```bash
# 1. Clone le projet
git clone <url-du-repo>
cd BABI-project2

# 2. Copy le fichier d'environnement
cp .env.example .env

# 3. Lancer Docker Compose
docker-compose up -d

# 4. Initialiser la base de données
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# 5. Accédez à :
#    http://localhost (Frontend via Nginx)
#    http://localhost/admin (Admin)
#    http://localhost:5050 (pgAdmin - accès BD)
```

---

## Structure Rapide

```
BABI-project2/
├── users/        ← Authentification & Profils
├── orders/       ← Gestion des Commandes
├── catalog/      ← Modèles de Couture
├── messaging/    ← Messages
├── reviews/      ← Évaluations
├── core/         ← Pages Générales
├── templates/    ← HTML
├── static/       ← CSS/JS
├── gateway/      ← Configuration principale
└── manage.py     ← Point d'entrée
```

---

## Commandes Essentielles

### Django

```bash
# Créer un super utilisateur
python manage.py createsuperuser

# Migrations
python manage.py makemigrations
python manage.py migrate

# Lancer le serveur
python manage.py runserver

# Shell Django
python manage.py shell

# Lancer les tests
python manage.py test
```

### Docker

```bash
# Voir l'état des services
docker-compose ps

# Voir les logs
docker-compose logs -f web

# Exécuter une commande Django
docker-compose exec web python manage.py <commande>

# Arrêter les services
docker-compose down

# Redémarrer
docker-compose restart
```

---

## Structure des Microservices

```
GATEWAY (Port 8000)
├─ Users Service     → /users/
├─ Catalog Service   → /catalog/
├─ Orders Service    → /orders/
├─ Messaging Service → /messages/
├─ Reviews Service   → /reviews/
└─ Core Service      → /
```

---

## Les 5 API clés

### 1. Authentication
```bash
# Login
curl -X POST http://localhost:8000/users/login/

# Logout
curl -X POST http://localhost:8000/users/logout/
```

### 2. Orders
```bash
# Créer une commande
curl -X POST http://localhost:8000/orders/create/

# Voir mes commandes
curl http://localhost:8000/orders/
```

### 3. Catalog
```bash
# Voir les modèles disponibles
curl http://localhost:8000/catalog/modeles/

# Détails d'un modèle
curl http://localhost:8000/catalog/modeles/1/
```

### 4. Messaging
```bash
# Voir les messages
curl http://localhost:8000/messages/inbox/

# Envoyer un message
curl -X POST http://localhost:8000/messages/send/
```

### 5. Reviews
```bash
# Voir les avis d'un couturier
curl http://localhost:8000/reviews/couturier/1/

# Créer un avis
curl -X POST http://localhost:8000/reviews/create/
```

---

## Configuration Rapide

### Fichier .env essentiel

```env
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données (développement)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# (Production - Décommenter)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=babicouture
# DB_USER=postgres
# DB_PASSWORD=password
# DB_HOST=localhost
```

---

## Créer des données de test

```bash
# Lancer le shell Django
python manage.py shell
```

```python
# Copier-coller dans le shell :

from users.models import Client, Couturier
from django.contrib.auth.models import User

# Créer un client
user_client = User.objects.create_user(
    username='client1',
    email='client@test.com',
    password='password123'
)
Client.objects.create(user=user_client)

# Créer un couturier
user_tailor = User.objects.create_user(
    username='tailor1',
    email='tailor@test.com',
    password='password123'
)
Couturier.objects.create(
    user=user_tailor,
    nom_atelier="Mon Atelier",
    specialite="Robes de soirée"
)

print("✅ Données créées !")
```

---

## Erreurs courantes

| Erreur | Solution |
|--------|----------|
| "No module named 'django'" | `pip install -r requirements.txt` |
| "Port 8000 already in use" | `python manage.py runserver 8001` |
| "No such table" | `python manage.py migrate` |
| "AttributeError" | Vérifiez les imports et migrations |
| "Connection refused" | Vérifiez que la BD est en cours d'exécution |

---

## Points d'entrée du Projet

### Frontend
- **Accueil** : http://localhost:8000/
- **Login** : http://localhost:8000/users/login/
- **Admin** : http://localhost:8000/admin/

### Services
- **Users** : http://localhost:8000/users/
- **Catalog** : http://localhost:8000/catalog/
- **Orders** : http://localhost:8000/orders/
- **Messages** : http://localhost:8000/messages/
- **Reviews** : http://localhost:8000/reviews/

---

## Prochaines Étapes

1. **Lire** [README.md](README.md) - Vue d'ensemble complète
2. **Comprendre** [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture détaillée
3. **Découvrir** [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Tous les endpoints
4. **Installer** [INSTALLATION.md](INSTALLATION.md) - Instructions complètes
5. **Contribuer** [CONTRIBUTING.md](CONTRIBUTING.md) - Comment aider

---

## Tech Stack Rapide

- **Backend** : Django 4.2
- **Database** : PostgreSQL / SQLite
- **Cache** : Redis
- **Task Queue** : Celery
- **Frontend** : Django Templates + Bootstrap
- **Server** : Gunicorn + Nginx

---

## Besoin d'aide?

| Question | Où trouver |
|----------|-----------|
| Architecture ? | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Installation ? | [INSTALLATION.md](INSTALLATION.md) |
| APIs ? | [API_DOCUMENTATION.md](API_DOCUMENTATION.md) |
| Déploiement ? | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Contribuer ? | [CONTRIBUTING.md](CONTRIBUTING.md) |

---

## Commandes Pratiques

```bash
# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# Exécuter les tests
python manage.py test

# Formatter le code
black .

# Vérifier la qualité
flake8 .

# Générer un rapport de couverture
coverage run --source='.' manage.py test
coverage report
coverage html  # Ouvre en HTML

# Nettoyer les fichiers Python
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name '*.pyc' -delete
```

---

## Statut du Projet

✅ **Microservices** - 6 services indépendants
✅ **Documentation** - Complète et détaillée
✅ **Tests** - Framework en place
✅ **Docker** - Production-ready
✅ **Database** - Schema optimisé
✅ **Security** - Best practices

---

## Pour le Développement

```bash
# Terminal 1 - Serveur Django
python manage.py runserver

# Terminal 2 - Tail des logs
tail -f logs.log

# Terminal 3 - Shell Django
python manage.py shell

# Terminal 4 - Tests en continu
pytest-watch
```

---

## Performance

```bash
# Profiler les requêtes
python manage.py shell
>>> from django.db import connection
>>> from django.db import reset_queries
>>> reset_queries()
>>> # Votre code...
>>> print(len(connection.queries))
>>> for q in connection.queries:
...     print(q)
```

---

## 🎉 C'est parti !

```bash
# 3 commandes pour démarrer :
python -m venv env && source env/bin/activate
pip install -r requirements.txt
python manage.py migrate && python manage.py runserver
```

**Accédez à http://localhost:8000 et commencez ! 🚀**

---

**Version** : 1.0  
**Dernière mise à jour** : Avril 2026
