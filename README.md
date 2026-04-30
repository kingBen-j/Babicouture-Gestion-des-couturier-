# 🎀 BabiCouture - Plateforme de Couture Numérique

Une plateforme de commerce électronique complète connectant les clients avec les couturiers professionnels, avec un système de gestion des commandes, d'évaluations et de messagerie.

## 📋 Table des matières

- [Architecture Microservices](#architecture-microservices)
- [Installation](#installation)
- [Configuration](#configuration)
- [Structure du Projet](#structure-du-projet)
- [Services](#services)
- [API Endpoints](#api-endpoints)
- [Base de Données](#base-de-données)
- [Authentification](#authentification)
- [Déploiement](#déploiement)
- [Contribution](#contribution)

---

## 🏗️ Architecture Microservices

### Vue d'ensemble

BabiCouture utilise une **architecture microservices** avec les composants suivants :

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Frontend)                         │
│                     (Django Templates)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    API GATEWAY (Port 8000)                       │
│                    gateway/settings.py                           │
│                    gateway/urls.py                               │
└────────┬──────────┬──────────┬──────────┬──────────┬────────────┘
         │          │          │          │          │
    ┌────▼───┬──────▼────┬────▼────┬─────▼────┬────▼────┐
    │ USERS  │ CATALOG   │ ORDERS  │MESSAGING │REVIEWS  │
    │SERVICE │ SERVICE   │SERVICE  │ SERVICE  │SERVICE  │
    │        │           │         │          │         │
    │ Port   │ Port      │ Port    │ Port     │ Port    │
    │ 8001   │ 8002      │ 8003    │ 8004     │ 8005    │
    └────┬───┴──────┬────┴────┬────┴─────┬────┴────┬────┘
         │          │         │          │         │
    ┌────▼──────────▼─────────▼──────────▼─────────▼────┐
    │         PostgreSQL/SQLite Database               │
    │              (Données Centralisées)              │
    └───────────────────────────────────────────────────┘
```

### Microservices

#### 1. **Users Service** (Port 8001)
- **Responsabilité** : Authentification, gestion des profils utilisateurs
- **Modèles** : `User`, `Client`, `Couturier`
- **Endpoints** :
  - `POST /users/register/` - Inscription
  - `POST /users/login/` - Connexion
  - `GET /users/profile/` - Profil utilisateur
  - `PUT /users/profile/update/` - Mise à jour profil

#### 2. **Catalog Service** (Port 8002)
- **Responsabilité** : Gestion des modèles/patrons de couture
- **Modèles** : `Modele`, `Categorie`
- **Endpoints** :
  - `GET /catalog/modeles/` - Liste des modèles
  - `POST /catalog/modeles/` - Créer un modèle
  - `GET /catalog/modeles/{id}/` - Détails du modèle

#### 3. **Orders Service** (Port 8003)
- **Responsabilité** : Gestion complète des commandes
- **Modèles** : `Commande`
- **Endpoints** :
  - `POST /orders/create/` - Créer une commande
  - `GET /orders/{id}/` - Détails de la commande
  - `PUT /orders/{id}/status/` - Modifier le statut
  - `POST /orders/{id}/cancel/` - Annuler une commande

#### 4. **Messaging Service** (Port 8004)
- **Responsabilité** : Communication client-couturier
- **Modèles** : `Message`, `Conversation`
- **Endpoints** :
  - `GET /messages/inbox/` - Boîte de réception
  - `POST /messages/send/` - Envoyer un message
  - `GET /messages/{conversation_id}/` - Historique conversation
  - `DELETE /messages/{id}/` - Supprimer un message

#### 5. **Reviews Service** (Port 8005)
- **Responsabilité** : Évaluations et avis
- **Modèles** : `Evaluation`
- **Endpoints** :
  - `POST /reviews/create/` - Créer une évaluation
  - `GET /reviews/couturier/{id}/` - Avis d'un couturier
  - `GET /reviews/{id}/` - Détails de l'avis
  - `PUT /reviews/{id}/` - Modifier l'avis

#### 6. **Core Service** (Port 8006)
- **Responsabilité** : Pages statiques et tableaux de bord
- **Endpoints** :
  - `GET /` - Accueil
  - `GET /dashboard/client/` - Tableau de bord client
  - `GET /dashboard/tailor/` - Tableau de bord couturier
  - `GET /about/`, `GET /faq/`, `GET /contact/`

---

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)
- Virtual environment (venv ou virtualenv)
- PostgreSQL (recommandé) ou SQLite (développement)

### Étapes d'installation

#### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd BABI-project2
```

#### 2. Créer un environnement virtuel

```bash
# Windows
python -m venv env
env\Scripts\activate

# macOS/Linux
python3 -m venv env
source env/bin/activate
```

#### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

#### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
# Ou pour PostgreSQL :
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=babicouture
# DB_USER=postgres
# DB_PASSWORD=password
# DB_HOST=localhost
# DB_PORT=5432

# Email (optionnel)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### 5. Migrations de base de données

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Créer un superutilisateur (admin)

```bash
python manage.py createsuperuser
```

#### 7. Charger les données initiales (optionnel)

```bash
python manage.py loaddata initial_data
```

---

## ⚙️ Configuration

### Variables d'environnement

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `DEBUG` | Mode debug Django | `True` |
| `SECRET_KEY` | Clé secrète Django | Générée |
| `ALLOWED_HOSTS` | Hôtes autorisés | `localhost,127.0.0.1` |
| `DB_ENGINE` | Type de base de données | `sqlite3` |
| `TIME_ZONE` | Fuseau horaire | `UTC` |

### Paramètres Django importants

Located in `gateway/settings.py`:

```python
# Fuseau horaire
TIME_ZONE = 'Africa/Abidjan'  # À adapter selon votre région

# Fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Fichiers média
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentification
AUTH_PASSWORD_VALIDATORS = [...]
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
```

---

## 📁 Structure du Projet

```
BABI-project2/
├── manage.py                 # Point d'entrée Django
├── requirements.txt          # Dépendances Python
├── README.md                 # Ce fichier
├── db.sqlite3                # Base de données SQLite
│
├── gateway/                  # Configuration centrale (API Gateway)
│   ├── __init__.py
│   ├── settings.py          # Configuration Django
│   ├── urls.py              # URLs principales
│   └── wsgi.py              # Configuration WSGI
│
├── users/                    # Service Utilisateurs
│   ├── models.py            # Modèles Client & Couturier
│   ├── views.py             # Vues (authentication, profils)
│   ├── urls.py              # URLs users
│   ├── forms.py             # Formulaires
│   ├── admin.py             # Configuration admin
│   ├── apps.py
│   ├── tests.py
│   └── migrations/          # Migrations de base de données
│
├── catalog/                  # Service Catalogue
│   ├── models.py            # Modèle Modele
│   ├── views.py             # Vues catalogue
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── migrations/
│
├── orders/                   # Service Commandes
│   ├── models.py            # Modèle Commande
│   ├── views.py             # Gestion des commandes
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── migrations/
│
├── messaging/                # Service Messagerie
│   ├── models.py            # Modèles Message & Conversation
│   ├── views.py             # Gestion des messages
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── migrations/
│
├── reviews/                  # Service Évaluations
│   ├── models.py            # Modèle Evaluation
│   ├── views.py             # Gestion des évaluations
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── migrations/
│
├── core/                     # Service Noyau
│   ├── views.py             # Pages statiques & dashboards
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
│
├── templates/                # Templates HTML (Frontend)
│   └── BabiCouture/
│       ├── base.html        # Template de base
│       ├── index.html       # Page d'accueil
│       ├── login.html
│       ├── register_client.html
│       ├── register_couturier.html
│       ├── client_dashboard.html
│       ├── tailor_dashboard.html
│       └── ...autres templates
│
├── static/                   # Fichiers statiques (CSS, JS)
│   ├── css/
│   │   ├── style.css
│   │   ├── client_dashboard.css
│   │   └── ...
│   └── js/
│       └── ...scripts
│
├── env/                      # Environnement virtuel Python
│   └── Scripts/
│
└── modeles/                  # Stockage des fichiers de modèles
```

---

## 📊 Services Détaillés

### Service Utilisateurs

**Responsabilités :**
- Authentification et autorisation
- Gestion des profils clients
- Gestion des profils couturiers
- Vérification des droits d'accès

**Modèles clés :**

```python
class Client:
    - user (User OneToOne)
    - telephone
    - adresse
    - mesures_par_defaut (JSON)
    - created_at

class Couturier:
    - user (User OneToOne)
    - nom_atelier
    - specialite
    - note_moyenne
    - nombre_avis
    - disponible
    - delai_moyen_livraison
```

### Service Catalogue

**Responsabilités :**
- Gestion des modèles de couture
- Catégorisation des designs
- Affichage des modèles disponibles

**Modèles clés :**

```python
class Modele:
    - titre
    - description
    - categorie
    - prix
    - couturier (ForeignKey)
    - photo
    - difficulte
```

### Service Commandes

**Responsabilités :**
- Création et gestion des commandes
- Suivi des statuts
- Gestion des paiements
- Gestion des délais de livraison

**Statuts possibles :**
- `en_attente` : En attente de confirmation couturier
- `confirmee` : Confirmée par le couturier
- `en_cours` : En cours de réalisation
- `livree` : Livrée au client
- `terminee` : Complétée et évaluée
- `annulee` : Annulée

**Modèle clé :**

```python
class Commande:
    - client (ForeignKey)
    - couturier (ForeignKey)
    - modele (ForeignKey)
    - titre
    - description
    - mesures_client (JSON)
    - prix_final
    - acompte
    - mode_paiement
    - date_livraison_prevue
    - statut
    - photos_client (JSON)
```

### Service Messagerie

**Responsabilités :**
- Communication directe entre clients et couturiers
- Historique des conversations
- Notifications

**Modèles clés :**

```python
class Message:
    - sender (ForeignKey User)
    - recipient (ForeignKey User)
    - contenu
    - photo (optionnel)
    - date_envoi
    - lu

class Conversation:
    - participant1 (ForeignKey User)
    - participant2 (ForeignKey User)
    - dernier_message_date
```

### Service Évaluations

**Responsabilités :**
- Évaluation des couturiers
- Calcul des moyennes
- Gestion des avis clients

**Modèle clé :**

```python
class Evaluation:
    - commande (ForeignKey)
    - couturier (ForeignKey)
    - client (ForeignKey)
    - note (1-5)
    - commentaire
    - qualite_travail
    - respect_delai
    - qualite_communication
```

---

## 🔌 API Endpoints

### Authentication (Users Service)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/users/login/` | Connexion utilisateur |
| POST | `/users/logout/` | Déconnexion |
| POST | `/users/register/` | Inscription nouvelle utilisateur |
| GET | `/users/profile/` | Récupérer le profil connecté |
| PUT | `/users/profile/update/` | Mettre à jour le profil |

### Catalog (Catalog Service)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/catalog/modeles/` | Liste tous les modèles |
| POST | `/catalog/modeles/` | Créer un nouveau modèle (couturier) |
| GET | `/catalog/modeles/<id>/` | Détails d'un modèle |
| PUT | `/catalog/modeles/<id>/` | Modifier un modèle (propriétaire) |
| DELETE | `/catalog/modeles/<id>/` | Supprimer un modèle |

### Orders (Orders Service)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/orders/` | Lister les commandes (utilisateur) |
| POST | `/orders/create/` | Créer une commande |
| GET | `/orders/<id>/` | Détails de la commande |
| PUT | `/orders/<id>/status/` | Modifier le statut |
| POST | `/orders/<id>/cancel/` | Annuler la commande |
| POST | `/orders/<id>/confirm/` | Confirmer la livraison |

### Messaging (Messaging Service)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/messages/inbox/` | Boîte de réception |
| GET | `/messages/sent/` | Messages envoyés |
| POST | `/messages/send/` | Envoyer un message |
| GET | `/messages/<conversation_id>/` | Historique conversation |
| DELETE | `/messages/<id>/` | Supprimer un message |

### Reviews (Reviews Service)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/reviews/couturier/<id>/` | Avis d'un couturier |
| POST | `/reviews/create/` | Créer un avis |
| GET | `/reviews/<id>/` | Détails de l'avis |
| PUT | `/reviews/<id>/` | Modifier l'avis |

---

## 🗄️ Base de Données

### Schéma de données

#### Utilisateurs

```sql
-- Users Django built-in
users_user
├── id (PK)
├── username (UNIQUE)
├── email
├── password
├── first_name
├── last_name
└── date_joined

-- Clients
users_client
├── id (PK)
├── user_id (FK -> users_user) [UNIQUE]
├── telephone
├── adresse
├── ville
├── code_postal
├── mesures_par_defaut (JSON)
├── created_at
└── updated_at

-- Couturiers
users_couturier
├── id (PK)
├── user_id (FK -> users_user) [UNIQUE]
├── nom_atelier
├── specialite
├── description
├── experience
├── note_moyenne
├── nombre_avis
├── disponible
├── delai_moyen_livraison
├── created_at
└── updated_at
```

#### Commandes

```sql
orders_commande
├── id (PK)
├── client_id (FK -> users_client)
├── couturier_id (FK -> users_couturier)
├── modele_id (FK -> catalog_modele) [nullable]
├── titre
├── description
├── mesures_client (JSON)
├── prix_final
├── acompte
├── mode_paiement
├── paiement_effectue
├── date_commande
├── date_livraison_prevue
├── date_livraison_reelle
├── statut
├── satisfait_client
├── created_at
└── updated_at
```

#### Autres

Messages, Évaluations, Modèles... (voir modèles.py de chaque app)

### Requêtes SQL courantes

```sql
-- Commandes d'un client
SELECT * FROM orders_commande WHERE client_id = ?;

-- Moyenne des évaluations d'un couturier
SELECT AVG(note) FROM reviews_evaluation WHERE couturier_id = ?;

-- Commandes en retard
SELECT * FROM orders_commande 
WHERE date_livraison_prevue < NOW() AND statut NOT IN ('terminee', 'annulee');
```

---

## 🔐 Authentification

### Système d'authentification

BabiCouture utilise **Django Authentication System** :

1. **Session-based** : Cookies de session
2. **Token optionnel** : Pour une future API REST

### Décorateurs de vérification

```python
@login_required
def ma_vue(request):
    # Utilisateur doit être connecté
    pass

@require_role('client')
def vue_client_seulement(request):
    # Disponible pour clients uniquement
    pass
```

### Rôles et permissions

| Rôle | Permissions |
|------|-------------|
| **Client** | Créer commandes, envoyer messages, évaluer couturiers |
| **Couturier** | Créer modèles, accepter/refuser commandes, répondre aux messages |
| **Admin** | Accès total au système |

---

## 🚀 Déploiement

### Développement local

```bash
# Terminal 1 - API Gateway
python manage.py runserver 8000

# Ou spécifier un port différent
python manage.py runserver 0.0.0.0:8000
```

Accédez à : `http://localhost:8000`

### Déploiement production

#### Option 1 : Avec Gunicorn + Nginx

```bash
# Installer Gunicorn
pip install gunicorn

# Lancer l'application
gunicorn --workers 4 --bind 0.0.0.0:8000 gateway.wsgi:application
```

**Configuration Nginx :**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
}
```

#### Option 2 : Avec Docker

**Dockerfile :**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "gateway.wsgi:application"]
```

**docker-compose.yml :**

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=babicouture
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Option 3 : Heroku

```bash
# Installation
npm install -g heroku-cli
heroku login

# Créer l'app
heroku create votre-app

# Configurer variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-key

# Déployer
git push heroku main
```

### Checklist de production

- [ ] `DEBUG = False` dans les paramètres
- [ ] `SECRET_KEY` défini correctement
- [ ] `ALLOWED_HOSTS` configuré
- [ ] HTTPS activé
- [ ] Base de données PostgreSQL (pas SQLite)
- [ ] Fichiers statiques collectés (`collectstatic`)
- [ ] Fichiers média sur cloud storage (S3, etc.)
- [ ] Logs configurés
- [ ] Monitoring activé
- [ ] Backup base de données automatique

---

## 🧪 Tests

### Lancer les tests

```bash
# Tous les tests
python manage.py test

# Tests d'une app spécifique
python manage.py test users

# Tests d'une classe
python manage.py test users.tests.ClientTests

# Avec verbosité
python manage.py test --verbosity 2
```

### Couverage de code

```bash
# Installer coverage
pip install coverage

# Générer rapport
coverage run --source='.' manage.py test
coverage report
coverage html  # Génère rapport HTML
```

---

## 🤝 Contribution

### Guidelines

1. Fork le repository
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Code Style

- Suivre PEP 8
- Docstrings pour toutes les fonctions
- Type hints recommandés
- Formatage avec `black`

```bash
pip install black
black .
```

---

## 📝 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

---

## 📧 Support

Pour l'aide et les questions :
- 📧 Email : support@babicouture.com
- 💬 Discord : [Lien Discord]
- 🐛 Issues : GitHub Issues

---

## 🗺️ Roadmap

### V2.0 (À venir)

- [ ] API REST complète (Django REST Framework)
- [ ] Application mobile (React Native)
- [ ] Payment Gateway intégration (Stripe, etc.)
- [ ] Notifications en temps réel (WebSockets)
- [ ] System de recommandation IA
- [ ] Dashboard analytics avancé
- [ ] Multi-langue support
- [ ] Support multi-devises

### V3.0 (Futur)

- [ ] Microservices complètement découplés
- [ ] Message queue (Celery + Redis)
- [ ] GraphQL API
- [ ] PWA mobile-first
- [ ] Blockchain intégration (authentification)

---

**Dernière mise à jour :** Avril 2026

Développé avec ❤️ par l'équipe BabiCouture
# Babicouture-Gestion-des-couturier-
# Babicouture-Gestion-des-couturier-
