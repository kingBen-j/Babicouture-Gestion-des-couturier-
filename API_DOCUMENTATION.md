# 📚 Documentation Complète des APIs - BabiCouture

## Table des matières

- [Authentication](#authentication)
- [Users API](#users-api)
- [Catalog API](#catalog-api)
- [Orders API](#orders-api)
- [Messaging API](#messaging-api)
- [Reviews API](#reviews-api)
- [Conventions & Erreurs](#conventions--erreurs)

---

## Authentication

### Register (Créer un compte)

**Endpoint :** `POST /users/register/`

**Body :**

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password1": "SecurePassword123!",
  "password2": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created) :**

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "message": "Utilisateur créé avec succès"
}
```

---

### Choose Role (Sélectionner le rôle)

**Endpoint :** `POST /users/choose-role/`

**Requête :** Authentifiée + POST

**Body :**

```json
{
  "role": "client"  // ou "couturier"
}
```

**Response (200 OK) :**

```json
{
  "role": "client",
  "message": "Rôle défini avec succès",
  "redirect_url": "/dashboard/client/"
}
```

---

### Login (Connexion)

**Endpoint :** `POST /users/login/`

**Body :**

```json
{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

**Response (200 OK) :**

```json
{
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "client",
  "message": "Connexion réussie"
}
```

---

### Logout (Déconnexion)

**Endpoint :** `POST /users/logout/`

**Authentification :** Requise

**Response (200 OK) :**

```json
{
  "message": "Déconnecté avec succès"
}
```

---

## Users API

### Get Profile (Récupérer le profil)

**Endpoint :** `GET /users/profile/`

**Authentification :** Requise

**Response (200 OK) :**

```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "profile": {
    "role": "client",
    "telephone": "+33123456789",
    "adresse": "123 Rue de Paris",
    "ville": "Abidjan",
    "code_postal": "01",
    "mesures_par_defaut": {
      "poitrine": 95,
      "taille": 80,
      "hanches": 100,
      "longueur_bras": 65
    }
  }
}
```

---

### Update Profile (Mettre à jour le profil)

**Endpoint :** `PUT /users/profile/update/`

**Authentification :** Requise

**Body (Client) :**

```json
{
  "telephone": "+33123456789",
  "adresse": "456 Boulevard Clemenceau",
  "ville": "Abidjan",
  "code_postal": "02",
  "mesures_par_defaut": {
    "poitrine": 95,
    "taille": 80,
    "hanches": 100,
    "longueur_bras": 65,
    "longueur_total": 160
  }
}
```

**Body (Couturier) :**

```json
{
  "nom_atelier": "Atelier de Luxe",
  "specialite": "Robes de soirée",
  "description": "Spécialiste des vêtements traditionnels",
  "experience": 15,
  "telephone": "+33123456789",
  "adresse": "789 Rue Marchand",
  "ville": "Abidjan",
  "localisation": "Plateau",
  "disponible": true,
  "delai_moyen_livraison": 7
}
```

**Response (200 OK) :**

```json
{
  "message": "Profil mis à jour avec succès",
  "profile": {...}
}
```

---

### Get All Couturiers (Lister les couturiers)

**Endpoint :** `GET /users/couturiers/`

**Authentification :** Non requise

**Query Parameters :**

```
?search=atelier
?ville=Abidjan
?specialite=robes
?min_rating=4
?ordering=-note_moyenne
?page=1&limit=10
```

**Response (200 OK) :**

```json
{
  "count": 42,
  "next": "/users/couturiers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 5,
      "nom_atelier": "Atelier de Luxe",
      "specialite": "Robes de soirée",
      "description": "...",
      "experience": 15,
      "note_moyenne": 4.8,
      "nombre_avis": 127,
      "disponible": true,
      "delai_moyen_livraison": 7,
      "photo": "https://...",
      "ville": "Abidjan"
    },
    {...}
  ]
}
```

---

### Get Couturier Detail (Détails d'un couturier)

**Endpoint :** `GET /users/couturiers/{id}/`

**Authentification :** Non requise

**Response (200 OK) :**

```json
{
  "id": 5,
  "nom_atelier": "Atelier de Luxe",
  "user": {
    "id": 5,
    "first_name": "Marie",
    "last_name": "Diallo"
  },
  "specialite": "Robes de soirée",
  "description": "Spécialiste des vêtements traditionnels et modernes",
  "experience": 15,
  "telephone": "+33123456789",
  "adresse": "789 Rue Marchand",
  "ville": "Abidjan",
  "localisation": "Plateau",
  "note_moyenne": 4.8,
  "nombre_avis": 127,
  "disponible": true,
  "delai_moyen_livraison": 7,
  "photo": "https://...",
  "modeles_count": 23,
  "evaluations": [
    {
      "id": 1,
      "note": 5,
      "commentaire": "Excellent travail !",
      "client_name": "John D.",
      "date": "2024-03-15"
    },
    {...}
  ]
}
```

---

## Catalog API

### Get All Models (Lister les modèles)

**Endpoint :** `GET /catalog/modeles/`

**Authentification :** Non requise

**Query Parameters :**

```
?search=robe
?categorie=soiree
?prix_min=50000
?prix_max=500000
?couturier_id=5
?ordering=-prix
?page=1&limit=12
```

**Response (200 OK) :**

```json
{
  "count": 87,
  "next": "/catalog/modeles/?page=2",
  "results": [
    {
      "id": 1,
      "titre": "Robe de Soirée Classique",
      "description": "Magnifique robe pour les occasions spéciales",
      "categorie": "soiree",
      "prix": 250000,
      "couturier": {
        "id": 5,
        "nom_atelier": "Atelier de Luxe",
        "note_moyenne": 4.8
      },
      "photo": "https://...",
      "difficulte": "moyen",
      "durée_moyenne": 14,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {...}
  ]
}
```

---

### Get Model Detail (Détails d'un modèle)

**Endpoint :** `GET /catalog/modeles/{id}/`

**Authentification :** Non requise

**Response (200 OK) :**

```json
{
  "id": 1,
  "titre": "Robe de Soirée Classique",
  "description": "Magnifique robe pour les occasions spéciales. Disponible en plusieurs couleurs.",
  "categorie": "soiree",
  "prix": 250000,
  "couturier": {
    "id": 5,
    "nom_atelier": "Atelier de Luxe",
    "note_moyenne": 4.8,
    "numero": "+33123456789"
  },
  "photo": "https://...",
  "photos_additionnelles": ["https://...", "https://..."],
  "difficulte": "moyen",
  "durée_moyenne": 14,
  "materials": ["coton", "soie"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-03-10T15:45:00Z",
  "commandes_count": 23
}
```

---

### Create Model (Créer un modèle - Couturier)

**Endpoint :** `POST /catalog/modeles/`

**Authentification :** Requise (Couturier)

**Body :**

```json
{
  "titre": "Robe de Soirée Classique",
  "description": "Magnifique robe pour les occasions spéciales",
  "categorie": "soiree",
  "prix": 250000,
  "photo": "file_upload",
  "difficulte": "moyen",
  "durée_moyenne": 14,
  "materials": ["coton", "soie"]
}
```

**Response (201 Created) :**

```json
{
  "id": 1,
  "titre": "Robe de Soirée Classique",
  "message": "Modèle créé avec succès",
  "url": "/catalog/modeles/1/"
}
```

---

### Update Model (Modifier un modèle)

**Endpoint :** `PUT /catalog/modeles/{id}/`

**Authentification :** Requise (Propriétaire ou Admin)

**Body :**

```json
{
  "titre": "Robe de Soirée Luxe",
  "prix": 300000,
  "description": "Description mise à jour"
}
```

**Response (200 OK) :**

```json
{
  "message": "Modèle mis à jour avec succès",
  "modele": {...}
}
```

---

### Delete Model (Supprimer un modèle)

**Endpoint :** `DELETE /catalog/modeles/{id}/`

**Authentification :** Requise (Propriétaire ou Admin)

**Response (204 No Content)** ou **(200 OK) :**

```json
{
  "message": "Modèle supprimé avec succès"
}
```

---

## Orders API

### Create Order (Créer une commande)

**Endpoint :** `POST /orders/create/`

**Authentification :** Requise (Client)

**Body - Option 1 : Basée sur un modèle :**

```json
{
  "modele_id": 1,
  "couturier_id": 5,
  "mesures_client": {
    "poitrine": 95,
    "taille": 80,
    "hanches": 100,
    "longueur_bras": 65
  },
  "couleurs": "bleu marine",
  "preferences": "Ajouter des broderies dorées",
  "mode_paiement": "mobile_money",
  "acompte": 125000
}
```

**Body - Option 2 : Commande personnalisée :**

```json
{
  "titre": "Robe personnalisée",
  "description": "Je voudrais une robe rouge avec des détails brodés",
  "couturier_id": 5,
  "mesures_client": {
    "poitrine": 95,
    "taille": 80,
    "hanches": 100
  },
  "prix_propose": 400000,
  "mode_paiement": "carte"
}
```

**Response (201 Created) :**

```json
{
  "id": 42,
  "titre": "Robe personnalisée",
  "couturier": "Marie Diallo",
  "statut": "en_attente",
  "date_commande": "2024-04-01T14:30:00Z",
  "message": "Commande créée et notification envoyée au couturier",
  "url": "/orders/42/"
}
```

---

### Get Orders (Lister ses commandes)

**Endpoint :** `GET /orders/`

**Authentification :** Requise

**Query Parameters :**

```
?statut=en_attente
?ordering=-date_commande
?page=1&limit=10
```

**Response (200 OK) :**

```json
{
  "count": 8,
  "results": [
    {
      "id": 42,
      "titre": "Robe personnalisée",
      "couturier": "Marie Diallo",
      "statut": "en_attente",
      "date_commande": "2024-04-01T14:30:00Z",
      "date_livraison_prevue": "2024-04-15",
      "prix_final": 250000,
      "en_retard": false
    },
    {...}
  ]
}
```

---

### Get Order Detail (Détails de la commande)

**Endpoint :** `GET /orders/{id}/`

**Authentification :** Requise (Propriétaire ou Couturier assigné)

**Response (200 OK) :**

```json
{
  "id": 42,
  "client": {
    "id": 1,
    "nom": "John Doe"
  },
  "couturier": {
    "id": 5,
    "nom_atelier": "Atelier de Luxe",
    "numero": "+33123456789"
  },
  "titre": "Robe personnalisée",
  "description": "Description de la commande",
  "mesures_client": {
    "poitrine": 95,
    "taille": 80,
    "hanches": 100
  },
  "couleurs": "bleu marine",
  "preferences": "Ajouter des broderies dorées",
  "prix_final": 250000,
  "acompte": 125000,
  "restant_a_payer": 125000,
  "paiement_effectue": true,
  "mode_paiement": "mobile_money",
  "statut": "en_cours",
  "date_commande": "2024-04-01T14:30:00Z",
  "date_debut": "2024-04-02T10:00:00Z",
  "date_livraison_prevue": "2024-04-15",
  "date_livraison_reelle": null,
  "photos_client": [],
  "photos_couturier": ["https://...", "https://..."],
  "historique_statuts": [
    {
      "ancien_statut": "en_attente",
      "nouveau_statut": "confirmee",
      "date": "2024-04-02T08:00:00Z",
      "par": "couturier"
    },
    {...}
  ],
  "en_retard": false
}
```

---

### Update Order Status (Modifier le statut)

**Endpoint :** `PUT /orders/{id}/status/`

**Authentification :** Requise (Couturier assigné ou Admin)

**Body :**

```json
{
  "statut": "en_cours",
  "notes_internes": "Commencé aujourd'hui"
}
```

**Response (200 OK) :**

```json
{
  "message": "Statut mis à jour avec succès",
  "ancien_statut": "confirmee",
  "nouveau_statut": "en_cours",
  "commande": {...}
}
```

---

### Confirm Delivery (Confirmer la livraison)

**Endpoint :** `POST /orders/{id}/confirm-delivery/`

**Authentification :** Requise (Couturier)

**Body (optionnel) :**

```json
{
  "notes": "Livraison complétée avec succès"
}
```

**Response (200 OK) :**

```json
{
  "message": "Livraison confirmée",
  "statut": "livree",
  "date_livraison_reelle": "2024-04-14"
}
```

---

### Confirm Receipt (Confirmer la réception)

**Endpoint :** `POST /orders/{id}/confirm-receipt/`

**Authentification :** Requise (Client)

**Body :**

```json
{
  "satisfait_client": true,
  "commentaire_final": "Très satisfait du travail !"
}
```

**Response (200 OK) :**

```json
{
  "message": "Réception confirmée",
  "statut": "terminee",
  "satisfait_client": true,
  "redirect_to_review": "/reviews/create/?commande=42"
}
```

---

### Cancel Order (Annuler une commande)

**Endpoint :** `POST /orders/{id}/cancel/`

**Authentification :** Requise (Client ou Couturier)

**Body :**

```json
{
  "raison": "J'ai trouvé un autre couturier",
  "remboursement": true
}
```

**Response (200 OK) :**

```json
{
  "message": "Commande annulée",
  "statut": "annulee",
  "remboursement": "Remboursement de 125000 initialisé"
}
```

---

## Messaging API

### Get Inbox (Boîte de réception)

**Endpoint :** `GET /messages/inbox/`

**Authentification :** Requise

**Query Parameters :**

```
?search=marie
?ordering=-date_envoi
?page=1&limit=20
```

**Response (200 OK) :**

```json
{
  "count": 15,
  "results": [
    {
      "conversation_id": 1,
      "avec": {
        "id": 5,
        "nom": "Marie Diallo",
        "photo": "https://..."
      },
      "dernier_message": "Oui, je peux commencer demain",
      "date_dernier": "2024-04-10T14:30:00Z",
      "non_lus": 2,
      "messages_count": 8
    },
    {...}
  ]
}
```

---

### Get Conversation (Historique conversation)

**Endpoint :** `GET /messages/conversation/{id}/`

**Authentification :** Requise

**Query Parameters :**

```
?ordering=-date_envoi
?page=1&limit=30
```

**Response (200 OK) :**

```json
{
  "conversation_id": 1,
  "participants": [
    {"id": 1, "nom": "John Doe"},
    {"id": 5, "nom": "Marie Diallo"}
  ],
  "messages": [
    {
      "id": 1,
      "sender": "Marie Diallo",
      "contenu": "Bonjour, intéressé par mes services?",
      "date_envoi": "2024-04-08T10:00:00Z",
      "lu": true
    },
    {
      "id": 2,
      "sender": "John Doe",
      "contenu": "Oui, j'ai besoin d'une robe pour un mariage",
      "date_envoi": "2024-04-08T10:05:00Z",
      "lu": true
    },
    {...}
  ]
}
```

---

### Send Message (Envoyer un message)

**Endpoint :** `POST /messages/send/`

**Authentification :** Requise

**Body :**

```json
{
  "recipient_id": 5,
  "contenu": "Avez-vous des disponibilités pour une commande rapide?",
  "photo": "file_upload" (optionnel)
}
```

**Response (201 Created) :**

```json
{
  "id": 42,
  "message": "Message envoyé avec succès",
  "conversation_id": 1,
  "date_envoi": "2024-04-10T15:30:00Z"
}
```

---

### Mark as Read (Marquer comme lu)

**Endpoint :** `POST /messages/{id}/mark-as-read/`

**Authentification :** Requise

**Response (200 OK) :**

```json
{
  "message": "Message marqué comme lu",
  "date_lecture": "2024-04-10T15:35:00Z"
}
```

---

### Delete Message (Supprimer un message)

**Endpoint :** `DELETE /messages/{id}/`

**Authentification :** Requise (Sender)

**Response (204 No Content)** ou **(200 OK) :**

```json
{
  "message": "Message supprimé avec succès"
}
```

---

## Reviews API

### Create Review (Créer une évaluation)

**Endpoint :** `POST /reviews/create/`

**Authentification :** Requise (Client)

**Body :**

```json
{
  "commande_id": 42,
  "note": 5,
  "commentaire": "Excellent travail, je recommande vivement!",
  "qualite_travail": 5,
  "respect_delai": 4,
  "qualite_communication": 5
}
```

**Response (201 Created) :**

```json
{
  "id": 1,
  "couturier": "Marie Diallo",
  "message": "Évaluation créée avec succès",
  "note_moyenne_couturier": 4.8,
  "nombre_avis_couturier": 12
}
```

---

### Get Couturier Reviews (Avis d'un couturier)

**Endpoint :** `GET /reviews/couturier/{id}/`

**Authentification :** Non requise

**Query Parameters :**

```
?ordering=-date_creation
?note=5
?page=1&limit=10
```

**Response (200 OK) :**

```json
{
  "couturier": {
    "id": 5,
    "nom_atelier": "Atelier de Luxe",
    "note_moyenne": 4.8,
    "nombre_avis": 27
  },
  "evaluations": [
    {
      "id": 1,
      "client": "John D.",
      "note": 5,
      "commentaire": "Excellent travail!",
      "qualite_travail": 5,
      "respect_delai": 4,
      "qualite_communication": 5,
      "reponse_couturier": "Merci beaucoup!",
      "date_reponse": "2024-04-09T10:00:00Z",
      "date_creation": "2024-04-08T14:30:00Z"
    },
    {...}
  ]
}
```

---

### Get Review Detail (Détails d'une évaluation)

**Endpoint :** `GET /reviews/{id}/`

**Authentification :** Non requise

**Response (200 OK) :**

```json
{
  "id": 1,
  "commande_id": 42,
  "client": {
    "id": 1,
    "nom": "John Doe"
  },
  "couturier": {
    "id": 5,
    "nom_atelier": "Atelier de Luxe"
  },
  "note": 5,
  "commentaire": "Excellent travail!",
  "qualite_travail": 5,
  "respect_delai": 4,
  "qualite_communication": 5,
  "reponse_couturier": "Merci beaucoup!",
  "date_reponse": "2024-04-09T10:00:00Z",
  "date_creation": "2024-04-08T14:30:00Z"
}
```

---

### Respond to Review (Répondre à un avis)

**Endpoint :** `PUT /reviews/{id}/respond/`

**Authentification :** Requise (Couturier propriétaire)

**Body :**

```json
{
  "reponse_couturier": "Merci pour votre retour positif! C'était un plaisir de travailler avec vous."
}
```

**Response (200 OK) :**

```json
{
  "message": "Réponse ajoutée avec succès",
  "reponse_couturier": "Merci pour votre retour positif! C'était un plaisir de travailler avec vous.",
  "date_reponse": "2024-04-09T10:00:00Z"
}
```

---

### Update Review (Modifier une évaluation)

**Endpoint :** `PUT /reviews/{id}/`

**Authentification :** Requise (Client propriétaire)

**Body :**

```json
{
  "note": 4,
  "commentaire": "Très bon travail, mais la livraison a été un peu tardive"
}
```

**Response (200 OK) :**

```json
{
  "message": "Évaluation mise à jour avec succès",
  "review": {...}
}
```

---

## Conventions & Erreurs

### Codes HTTP

| Code | Signification |
|------|---------------|
| **200** | OK - Succès |
| **201** | Created - Ressource créée |
| **204** | No Content - Suppression réussie |
| **400** | Bad Request - Données invalides |
| **401** | Unauthorized - Non authentifié |
| **403** | Forbidden - Non autorisé |
| **404** | Not Found - Ressource non trouvée |
| **500** | Server Error - Erreur serveur |

---

### Format d'erreur

```json
{
  "error": "Validation Error",
  "message": "Les données fournies sont invalides",
  "details": {
    "email": ["Email invalide"],
    "telephone": ["Ce champ ne peut pas être vide"]
  }
}
```

---

### Authentification

**Header requis :**

```
Authorization: Bearer <token>
```

ou **Cookie de session Django** (localStorage)

---

### Pagination

Toutes les listes répondent avec :

```json
{
  "count": 100,
  "next": "/?page=2",
  "previous": null,
  "results": [...]
}
```

---

### Dates & Heures

Format ISO 8601 :

```
"2024-04-10T15:30:00Z"
```

---

### Statuts Commande

- `en_attente` → Attente de confirmation couturier
- `confirmee` → Confirmée, prête à commencer
- `en_cours` → En cours de réalisation
- `livree` → Livrée au client
- `terminee` → Complétée et évaluée
- `annulee` → Annulée

---

**Dernière mise à jour :** Avril 2026

Pour plus d'aide, consultez le [README.md](README.md) ou [ARCHITECTURE.md](ARCHITECTURE.md)
