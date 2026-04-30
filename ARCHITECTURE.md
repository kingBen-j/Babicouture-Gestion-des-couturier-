# 🏗️ Architecture Microservices - BabiCouture

## Vue générale de l'architecture

BabiCouture est conçu comme une **architecture microservices** où chaque fonctionnalité majeure est encapsulée dans son propre service Django app, communiquant à travers une **API Gateway centralisée**.

---

## 📐 Diagramme de l'Architecture

```
                    ┌─────────────────────────┐
                    │   Frontend (Templates)  │
                    │   Client-Side Logic     │
                    └───────────┬─────────────┘
                                │ HTTP Requests
                    ┌───────────▼─────────────┐
                    │   API GATEWAY (8000)    │
                    │  gateway/settings.py    │
                    │   Django URLConf        │
                    └───┬───┬───┬───┬───┬──────┘
                        │   │   │   │   │
        ┌───────────────┼───┼───┼───┼───┼───────────────┐
        │               │   │   │   │   │               │
   ┌────▼────┐   ┌──────▼──┐ │ ┌─▼───┬┴──┐   ┌────▼────┐
   │  USERS  │   │ CATALOG │ │ │ORDERS MESSAGING       │REVIEWS│
   │ Service │   │ Service │ │ │Service Service       │Service│
   ├─────────┤   ├────────┤ │ ├─────┬──┐           ├────────┤
   │ Port:   │   │ Port:  │ │ │Port:│  │Port: 8004 │Port:   │
   │ 8001    │   │ 8002   │ │ │8003 │  │           │ 8005   │
   └────┬────┘   └───┬────┘ │ └──┬──┬──┘           └────┬───┘
        │            │      │    │  │                   │
        └────────────┼──────┼────┼──┼───────────────────┘
                     │      │    │  │
          ┌──────────┴──────┴────┴──┴───────────┐
          │    PostgreSQL Database Server       │
          │    (Données centralisées)           │
          │                                     │
          │  - Users & Profiles                 │
          │  - Orders & Tracking                │
          │  - Messages & Conversations         │
          │  - Reviews & Evaluations            │
          │  - Catalog & Models                 │
          └─────────────────────────────────────┘
```

---

## 🔄 Flux de Communication

### Exemple 1 : Créer une Commande

```
Client               Gateway              Orders          Database
  │                    │                  Service            │
  ├─ POST /orders/ ──→ │                    │                │
  │                    ├─ Valider auth ────→│                │
  │                    │                    │                │
  │                    │◄─ Validation OK ───┤                │
  │                    ├─ Créer Commande ──→│                │
  │                    │                    ├─ INSERT ──────→│
  │                    │                    │◄─ ID commande ─┤
  │                    │◄─ 201 Created ────│                │
  │◄─ JSON réponse ───┤                    │                │
  │  {id, status, ...} │                    │                │
```

### Exemple 2 : Envoyer un Message

```
Client               Gateway           Messaging         Database
  │                    │                Service             │
  ├─ POST /messages/ ─→ │                  │                │
  │                    ├─ Auth + Validation│                │
  │                    ├─ Créer Message ──→│                │
  │                    │                   ├─ INSERT ──────→│
  │                    │                   ├─ Trigger Notif │
  │                    │                   │                │
  │                    │◄─ 200 OK ────────┤                │
  │◄─ {"status": "ok"}─┤                   │                │
```

---

## 📦 Structure des Services

### 1. Users Service (8001)

**Fichiers clés :**
- `users/models.py` : Modèles Client & Couturier
- `users/views.py` : Logique authentification & profils
- `users/forms.py` : Validation formulaires
- `users/urls.py` : Routes service

**Responsabilités :**
- Inscription/Connexion
- Gestion des profils
- Vérification des droits
- Récupération des données utilisateur

**Base de données :**

```
USER (Django Built-in)
├─ id, username, email, password
├─ first_name, last_name
└─ date_joined, is_active

CLIENT
├─ user_id (OneToOne)
├─ telephone, adresse, ville
├─ mesures_par_defaut (JSON)
└─ timestamps

COUTURIER
├─ user_id (OneToOne)
├─ nom_atelier, specialite
├─ note_moyenne, nombre_avis
├─ disponible, delai_moyen_livraison
└─ timestamps
```

---

### 2. Catalog Service (8002)

**Fichiers clés :**
- `catalog/models.py` : Modèle Modele (patterns)
- `catalog/views.py` : Affichage & gestion modèles
- `catalog/urls.py` : Routes

**Responsabilités :**
- Créer/modifier des modèles de couture
- Afficher les modèles disponibles
- Gérer les catégories
- Filtrer par prix, difficulté, etc.

**Base de données :**

```
MODELE
├─ id, titre, description
├─ couturier_id (FK)
├─ categorie, prix
├─ photo (ImageField)
├─ difficulte, durée_moyenne
└─ timestamps
```

---

### 3. Orders Service (8003)

**Fichiers clés :**
- `orders/models.py` : Modèle Commande
- `orders/views.py` : Gestion complète commandes
- `orders/urls.py` : Routes

**Responsabilités :**
- Créer des commandes
- Suivre les statuts
- Gérer les paiements
- Calculer les délais
- Signaler les retards

**Base de données :**

```
COMMANDE
├─ id, client_id (FK), couturier_id (FK)
├─ modele_id (FK, nullable)
├─ titre, description
├─ mesures_client (JSON)
├─ prix_final, acompte
├─ mode_paiement, paiement_effectue
├─ date_commande, date_livraison_prevue
├─ date_livraison_reelle
├─ statut (en_attente|confirmee|en_cours|livree|...)
├─ satisfait_client, commentaire_final
└─ timestamps
```

**Statuts & Transitions :**

```
en_attente ──→ confirmee ──→ en_cours ──→ livree ──→ terminee
   ↓                                           ↑
   └───────────────── annulee ────────────────┘
```

---

### 4. Messaging Service (8004)

**Fichiers clés :**
- `messaging/models.py` : Message & Conversation
- `messaging/views.py` : Gestion messages
- `messaging/urls.py` : Routes

**Responsabilités :**
- Envoyer/recevoir messages
- Gérer les conversations
- Marquer comme lu/non-lu
- Supprimer messages

**Base de données :**

```
MESSAGE
├─ id, sender_id (FK), recipient_id (FK)
├─ contenu, photo (optional)
├─ date_envoi
├─ lu, date_lecture
└─ conversation_id (FK)

CONVERSATION
├─ id, participant1_id (FK)
├─ participant2_id (FK)
├─ dernier_message_date
└─ created_at
```

---

### 5. Reviews Service (8005)

**Fichiers clés :**
- `reviews/models.py` : Modèle Evaluation
- `reviews/views.py` : Gestion évaluations
- `reviews/urls.py` : Routes

**Responsabilités :**
- Créer/modifier évaluations
- Calculer moyennes
- Afficher avis couturier
- Gérer réponses couturier

**Base de données :**

```
EVALUATION
├─ id, commande_id (FK, OneToOne)
├─ couturier_id (FK), client_id (FK)
├─ note (1-5), commentaire
├─ qualite_travail, respect_delai
├─ qualite_communication
├─ reponse_couturier, date_reponse
└─ timestamps
```

---

### 6. Core Service (8006)

**Fichiers clés :**
- `core/views.py` : Pages générales
- `core/urls.py` : Routes

**Responsabilités :**
- Accueil & pages statiques
- Tableaux de bord (client & couturier)
- À propos, FAQ, Contact
- Redirection vers services

---

## 🔗 Communication Inter-Services

### Approche actuelle : Appels Direct

```python
# Dans orders/views.py
from users.models import Client, Couturier

def create_order(request):
    client = Client.objects.get(user=request.user)
    couturier = Couturier.objects.get(id=request.POST['couturier_id'])
    order = Commande.objects.create(
        client=client,
        couturier=couturier,
        ...
    )
```

### Approche future : API REST

```python
# Service Gateway appelle les services via HTTP
import requests

response = requests.get(
    'http://localhost:8001/api/users/profile/',
    headers={'Authorization': f'Bearer {token}'}
)
user_data = response.json()
```

---

## 🗄️ Schéma de Base de Données Complet

```
DATABASE BABICOUTURE
│
├─ auth_user (Django)
│  ├─ id, username, email, password_hash
│  ├─ first_name, last_name
│  ├─ is_staff, is_active, is_superuser
│  └─ date_joined
│
├─ users_client
│  ├─ id, user_id (U), telephone, adresse
│  ├─ ville, code_postal
│  ├─ mesures_par_defaut (JSON)
│  └─ created_at, updated_at
│
├─ users_couturier
│  ├─ id, user_id (U), nom_atelier, telephone
│  ├─ adresse, ville, localisation, specialite
│  ├─ description, experience, photo
│  ├─ note_moyenne, nombre_avis
│  ├─ disponible, delai_moyen_livraison
│  └─ created_at, updated_at
│
├─ catalog_modele
│  ├─ id, couturier_id (FK), titre, description
│  ├─ categorie, prix, photo
│  ├─ difficulte, durée_moyenne
│  └─ created_at, updated_at
│
├─ orders_commande
│  ├─ id, client_id (FK), couturier_id (FK)
│  ├─ modele_id (FK, nullable), titre, description
│  ├─ mesures_client (JSON), taille, couleurs
│  ├─ preferences, prix_proposed, prix_final
│  ├─ acompte, mode_paiement, paiement_effectue
│  ├─ date_commande, date_debut
│  ├─ date_livraison_prevue, date_livraison_reelle
│  ├─ statut (enum), priorite
│  ├─ photos_client (JSON), photos_couturier (JSON)
│  ├─ satisfait_client, commentaire_final
│  └─ created_at, updated_at
│
├─ messaging_message
│  ├─ id, sender_id (FK), recipient_id (FK)
│  ├─ contenu, photo (nullable)
│  ├─ date_envoi, lu, date_lecture
│  ├─ conversation_id (FK)
│  └─ created_at
│
├─ messaging_conversation
│  ├─ id, participant1_id (FK), participant2_id (FK)
│  ├─ dernier_message_date, created_at
│  └─ updated_at
│
└─ reviews_evaluation
   ├─ id, commande_id (FK, U), couturier_id (FK)
   ├─ client_id (FK), note (1-5)
   ├─ commentaire, qualite_travail
   ├─ respect_delai, qualite_communication
   ├─ reponse_couturier, date_reponse
   └─ created_at, updated_at
```

**Légende :**
- `(U)` = Unique (OneToOne)
- `(FK)` = Foreign Key (Many-to-One)

---

## 🔐 Authentification & Autorisation

### 1. Django Session Authentication

```python
# Login flow
authenticate(username, password) → User object
login(request, user) → Store session cookie
request.user.is_authenticated → Check login status
```

### 2. Permission Checking

```python
# Basé sur les modèles Client/Couturier
client = Client.objects.filter(user=request.user).exists()
couturier = Couturier.objects.filter(user=request.user).exists()
```

### 3. Décorateurs personnalisés

```python
from functools import wraps
from django.shortcuts import redirect

def require_role(role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if role == 'client' and Client.objects.filter(user=request.user).exists():
                return view_func(request, *args, **kwargs)
            elif role == 'couturier' and Couturier.objects.filter(user=request.user).exists():
                return view_func(request, *args, **kwargs)
            return redirect('choose_role')
        return wrapper
    return decorator

# Utilisation
@require_role('client')
def vue_client_seulement(request):
    pass
```

---

## 🚀 Déploiement en Production

### Architecture de déploiement recommandée

```
Internet
   │
   ├─ Cloudflare CDN (Cache + DDoS Protection)
   │
   └─ Nginx (Load Balancer)
      │
      ├─ Gunicorn Worker 1 (Django 8001)
      ├─ Gunicorn Worker 2 (Django 8002)
      └─ Gunicorn Worker N (Django ...N)
         │
         └─ PostgreSQL (Database)
            └─ Backup automatique S3
```

### Fichiers de déploiement

#### .env (Ne pas committer !)

```env
# Django
DEBUG=False
SECRET_KEY=your-long-random-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=babicouture
DB_USER=postgres
DB_PASSWORD=secure-password-here
DB_HOST=db.example.com
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password

# AWS S3 (pour fichiers média)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=babicouture-media

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### Docker Compose

```yaml
version: '3.8'

services:
  # Base de données PostgreSQL
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis (Cache & Task Queue)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Django Application
  web:
    build: .
    command: gunicorn --workers 4 --bind 0.0.0.0:8000 gateway.wsgi:application
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DB_ENGINE=${DB_ENGINE}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./staticfiles:/app/staticfiles
      - ./media:/app/media

  # Celery Worker (Tâches asynchrones)
  celery:
    build: .
    command: celery -A gateway worker -l info
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
      - web

  # Celery Beat (Tâches planifiées)
  celery-beat:
    build: .
    command: celery -A gateway beat -l info
    environment:
      - DEBUG=${DEBUG}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  # Nginx (Reverse Proxy)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./staticfiles:/staticfiles:ro
      - ./media:/media:ro
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
```

---

## 🔄 Flux d'une Commande Complète

```
1. Client crée commande
   ├─ POST /orders/create/
   ├─ Validation des données
   └─ Création Commande(statut=en_attente)

2. Notification couturier
   ├─ Celery task: notify_tailor()
   └─ Email + Dashboard notification

3. Couturier confirme/refuse
   ├─ PUT /orders/{id}/status/
   ├─ Transition vers confirmee/annulee
   └─ Notification client

4. Couturier lance la réalisation
   ├─ PUT /orders/{id}/status/
   ├─ date_debut = now()
   └─ Statut → en_cours

5. Couturier livraison
   ├─ POST /orders/{id}/confirm-delivery/
   ├─ date_livraison_reelle = now()
   └─ Statut → livree

6. Client confirme réception
   ├─ POST /orders/{id}/confirm-receipt/
   ├─ satisfait_client = True/False
   └─ Statut → terminee

7. Client évalue couturier
   ├─ POST /reviews/create/
   ├─ Note + commentaire
   ├─ Mise à jour note_moyenne couturier
   └─ Notification couturier

8. Couturier peut répondre
   ├─ PUT /reviews/{id}/respond/
   └─ Avis final visible aux autres clients
```

---

## 📊 Métriques & Analytics

### Requêtes utiles pour analytics

```sql
-- Revenue par mois
SELECT 
    DATE_TRUNC('month', date_commande),
    SUM(prix_final) as revenue,
    COUNT(*) as order_count
FROM orders_commande
WHERE statut IN ('terminee', 'livree')
GROUP BY DATE_TRUNC('month', date_commande);

-- Top couturiers
SELECT 
    c.id, c.nom_atelier,
    COUNT(cm.id) as order_count,
    AVG(e.note) as avg_rating,
    COUNT(DISTINCT cm.client_id) as unique_clients
FROM users_couturier c
LEFT JOIN orders_commande cm ON c.id = cm.couturier_id
LEFT JOIN reviews_evaluation e ON c.id = e.couturier_id
GROUP BY c.id
ORDER BY avg_rating DESC
LIMIT 10;

-- Temps moyen de réalisation
SELECT 
    couturier_id,
    AVG(EXTRACT(DAY FROM date_livraison_reelle - date_debut)) as avg_days
FROM orders_commande
WHERE date_debut IS NOT NULL AND date_livraison_reelle IS NOT NULL
GROUP BY couturier_id;
```

---

## 🎯 Bonnes Pratiques

1. **Validation** : Toujours valider au niveau du formulaire ET du modèle
2. **Sécurité** : Utiliser `@login_required` et `@require_role()` sur toutes les vues sensibles
3. **Performance** : Utiliser `select_related()` et `prefetch_related()` pour les requêtes
4. **Cache** : Mettre en cache les données fréquemment accédées
5. **Logging** : Logger les actions importantes (création, suppression, paiements)
6. **Tests** : Couvrir les modèles, vues et formulaires
7. **Documentation** : Documenter les APIs complexes
8. **Secrets** : Ne jamais committer `.env` ou clés d'API

---

## 🚀 Prochaines Étapes

1. Implémenter REST API avec Django REST Framework
2. Ajouter Celery pour tâches asynchrones
3. Intégrer payment gateway (Stripe)
4. Implémenter WebSockets pour notifications temps réel
5. Créer mobile app (React Native)
6. Migrer vers microservices complètement découplés

---

Dernière mise à jour: Avril 2026
