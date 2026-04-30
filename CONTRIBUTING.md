# 🤝 Guide de Contribution - BabiCouture

Merci de votre intérêt pour contribuer à BabiCouture ! Ce guide explique comment participer au projet.

## Table des matières

- [Avant de commencer](#avant-de-commencer)
- [Workflow de contribution](#workflow-de-contribution)
- [Standards de code](#standards-de-code)
- [Conventions de commit](#conventions-de-commit)
- [Soumettre une Pull Request](#soumettre-une-pull-request)
- [Signaler un bug](#signaler-un-bug)
- [Suggérer une amélioration](#suggérer-une-amélioration)

---

## Avant de commencer

### 1. Fork le repository

Allez sur [GitHub](https://github.com) et cliquez sur "Fork" en haut à droite.

### 2. Clonez votre fork

```bash
git clone https://github.com/votre-username/BABI-project2.git
cd BABI-project2
```

### 3. Ajoutez le repository original comme remote

```bash
git remote add upstream https://github.com/original-repo/BABI-project2.git
```

### 4. Créez une branche de feature

```bash
git checkout -b feature/ma-super-fonctionnalite
```

---

## Workflow de contribution

### Cycle de développement

```
1. Update local main
   └─ git fetch upstream
   └─ git checkout main
   └─ git merge upstream/main

2. Create feature branch
   └─ git checkout -b feature/xyz

3. Make changes
   └─ Edit files
   └─ Run tests
   └─ Commit changes

4. Push to your fork
   └─ git push origin feature/xyz

5. Create Pull Request
   └─ On GitHub, click "Create Pull Request"

6. Review & Merge
   └─ Maintainers review
   └─ Address feedback
   └─ Merge to main
```

### Exemple détaillé

```bash
# 1. Mettre à jour votre branche locale
git fetch upstream
git checkout main
git merge upstream/main

# 2. Créer une branche de feature
git checkout -b feature/add-payment-gateway

# 3. Faire les modifications
# ... éditer les fichiers ...

# 4. Vérifier que tout fonctionne
python manage.py test
python manage.py runserver

# 5. Commiter les changements
git add .
git commit -m "feat: add Stripe payment integration"

# 6. Pousser vers votre fork
git push origin feature/add-payment-gateway

# 7. Allez sur GitHub et créez une Pull Request
```

---

## Standards de code

### Style Python (PEP 8)

```python
# ✅ BON
def create_order(user, product_id, quantity=1):
    """Create a new order for the user."""
    order = Order.objects.create(
        user=user,
        product_id=product_id,
        quantity=quantity
    )
    return order

# ❌ MAUVAIS
def CreateOrder(user,product_id,quantity=1):
    order = Order.objects.create(user=user, product_id=product_id, quantity=quantity)
    return order
```

### Formatage avec Black

```bash
# Installer Black
pip install black

# Formater tous les fichiers
black .

# Formater un fichier spécifique
black users/views.py
```

### Linting avec Flake8

```bash
# Installer Flake8
pip install flake8

# Checker tous les fichiers
flake8 .

# Ignorer les avertissements non critiques
flake8 . --exclude=migrations,venv
```

### Type Hints (recommandé)

```python
# ✅ BON
from typing import Optional, List
from django.db.models import QuerySet

def get_couturier_orders(couturier_id: int) -> QuerySet:
    """Get all orders for a couturier."""
    return Order.objects.filter(couturier_id=couturier_id)

def process_order(order: Order) -> Optional[str]:
    """Process an order and return a transaction ID."""
    if order.status == 'pending':
        return generate_transaction_id()
    return None

# ❌ MAUVAIS
def get_couturier_orders(couturier_id):
    return Order.objects.filter(couturier_id=couturier_id)
```

### Docstrings

```python
# ✅ BON - Google Style
def calculate_order_total(order: Order) -> Decimal:
    """Calculate the total price for an order.
    
    Args:
        order: The Order instance to calculate total for.
        
    Returns:
        The total price as a Decimal.
        
    Raises:
        ValueError: If order has no items.
    """
    if not order.items.exists():
        raise ValueError("Order must have at least one item")
    
    return sum(item.price * item.quantity for item in order.items.all())

# ❌ MAUVAIS
def calculate_order_total(order):
    # calculate total
    return total
```

### Tests

Chaque fonctionnalité doit avoir des tests :

```python
# tests.py
from django.test import TestCase
from users.models import Client, Couturier
from django.contrib.auth.models import User

class ClientCreationTest(TestCase):
    """Test client creation and profile."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_client_creation(self):
        """Test that a client can be created."""
        client = Client.objects.create(user=self.user)
        self.assertEqual(client.user, self.user)
    
    def test_client_measurements(self):
        """Test that measurements are stored correctly."""
        measurements = {'poitrine': 95, 'taille': 80}
        client = Client.objects.create(
            user=self.user,
            mesures_par_defaut=measurements
        )
        self.assertEqual(client.mesures_par_defaut, measurements)
```

Lancer les tests :

```bash
# Tous les tests
python manage.py test

# Tests d'une app spécifique
python manage.py test users

# Avec couverture de code
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Commentaires

```python
# ✅ BON - Explique le "pourquoi"
# Délai de livraison augmenté de 2 jours avant le Jour de l'An
# car beaucoup de couturiers sont en vacances
if order.date_livraison_prevue.month == 12 and order.date_livraison_prevue.day >= 20:
    order.date_livraison_prevue += timedelta(days=2)

# ❌ MAUVAIS - État obvious du code
# Ajouter 2 jours à la date de livraison
order.date_livraison_prevue += timedelta(days=2)
```

---

## Conventions de commit

### Format des messages

```
<type>: <subject>

<body>

<footer>
```

### Types de commit

- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Mise à jour de documentation
- `style`: Changements de formatage (pas de logique)
- `refactor`: Refactorisation de code
- `perf`: Optimisation de performance
- `test`: Ajout de tests
- `chore`: Changements de build, dépendances, etc.

### Exemples

```bash
# ✅ BON
git commit -m "feat: add payment gateway integration

- Implement Stripe API integration
- Add payment processing views
- Update order model with payment fields

Closes #123"

# ✅ BON
git commit -m "fix: resolve order status update race condition

The issue occurred when two requests updated the same order
simultaneously. Added database-level transaction lock."

# ❌ MAUVAIS
git commit -m "Fixed stuff"
git commit -m "updates"
git commit -m "changes to several things"
```

### Squashing commits

Avant de soumettre une PR, squash les commits :

```bash
# Interactif rebase des 3 derniers commits
git rebase -i HEAD~3

# Marquer les commits à squash avec 's'
# s = squash - combine ce commit avec le précédent
# pick 1234567 First commit
# s 234567a Second commit to squash
# s 345678b Third commit to squash

# Sauvegarder et fermer l'éditeur
# Git combinera les commits

# Force push vers votre branche
git push -f origin feature/ma-feature
```

---

## Soumettre une Pull Request

### Avant de soumettre

```bash
# 1. Mettre à jour avec la branche principale
git fetch upstream
git rebase upstream/main

# 2. Lancer les tests
python manage.py test

# 3. Formater le code
black .

# 4. Vérifier la qualité
flake8 .

# 5. Commit final
git push -f origin feature/ma-feature
```

### Template de Pull Request

```markdown
## Description
Décrivez brièvement votre changement (2-3 phrases).

## Type de changement
- [ ] Bug fix
- [ ] Nouvelle fonctionnalité
- [ ] Breaking change
- [ ] Mise à jour de documentation

## Related Issues
Fixes #123
Related to #456

## Changements clés
- Changement 1
- Changement 2
- Changement 3

## Tests
- [ ] Tests ajoutés/modifiés
- [ ] Tests unitaires passent
- [ ] Testé localement
- [ ] N/A

## Screenshots (si applicable)
[Ajouter des screenshots ou GIFs]

## Checklist
- [ ] Le code suit les standards du projet
- [ ] La documentation est mise à jour
- [ ] Les messages de commit sont clairs
- [ ] Pas de breaking changes
```

### Après avoir soumis

1. **Attendez la review** - Les mainteneurs vont examiner votre code
2. **Répondez aux commentaires** - Faites les modifications demandées
3. **Push les changements** - Les mises à jour s'ajoutent automatiquement à la PR
4. **Attendez l'approbation** - Une fois approuvée, elle sera mergée

---

## Signaler un bug

### Template de bug report

```markdown
## Description du bug
[Description claire et concise du bug]

## Étapes pour reproduire
1. Aller à '[page/section]'
2. Cliquer sur '[élément]'
3. Observer '[comportement attendu]'

## Comportement attendu
[Décrire ce qui devrait se passer]

## Comportement réel
[Décrire ce qui se passe réellement]

## Captures d'écran
[Si applicable]

## Informations environnement
- OS: [ex: Windows 10]
- Python: [ex: 3.10]
- Django: [ex: 4.2]

## Logs/Erreurs
```
[Coller les erreurs pertinentes]
```

## Information supplémentaire
[Tout ce qui pourrait aider à debugger]
```

### Exemple

```markdown
## Description du bug
Les commandes ne s'affichent pas dans le dashboard du couturier.

## Étapes pour reproduire
1. Connectez-vous en tant que couturier
2. Allez sur le dashboard
3. Cliquez sur "Mes commandes"

## Comportement attendu
Les commandes assignées au couturier s'affichent dans une liste.

## Comportement réel
La page affiche "Aucune commande" même si des commandes ont été créées.

## Logs
```
AttributeError: 'NoneType' object has no attribute 'commandes_recues'
  File "core/views.py", line 45, in tailor_dashboard
    orders = couturier.commandes_recues.all()
```

## Environment
- OS: Windows 10
- Python 3.10
- Django 4.2
```

---

## Suggérer une amélioration

### Template de feature request

```markdown
## Description
[Décrivez l'amélioration que vous suggérez]

## Motivation
[Expliquez le contexte et pourquoi cette fonctionnalité serait utile]

## Solution proposée
[Décrivez votre idée de solution]

## Alternatives considérées
[Décrivez les alternatives que vous avez envisagées]

## Contexte supplémentaire
[Toute autre information pertinente]
```

---

## Directives générales

### À faire ✅

- Écrire du code clair et lisible
- Ajouter des tests pour vos changements
- Mettre à jour la documentation
- Commiter régulièrement
- Utiliser des messages de commit descriptifs
- Respecter le code style du projet
- Demander de l'aide si vous êtes bloqué

### À ne pas faire ❌

- Ne pas committer du code non-testé
- Ne pas committer des secrets/API keys
- Ne pas mercer votre propre PR
- Ne pas ignorer les commentaires de review
- Ne pas faire des changements sans rapport dans une PR

---

## Structure du projet

```
BABI-project2/
├── users/               # Service Utilisateurs
├── orders/              # Service Commandes  
├── catalog/             # Service Catalogue
├── messaging/           # Service Messagerie
├── reviews/             # Service Évaluations
├── core/                # Service Noyau
├── templates/           # Templates HTML
├── static/              # Fichiers statiques
├── tests/               # Tests
└── gateway/             # Configuration principale
```

### Avant de modifier un service

1. Lisez la documentation du service dans [ARCHITECTURE.md](ARCHITECTURE.md)
2. Comprenez les modèles et relations
3. Regardez les tests existants
4. Respectez le pattern de code existant

---

## Besoin d'aide ?

- 💬 Posez une question sur la page d'issue
- 📖 Consultez la [documentation](README.md)
- 🐛 Cherchez les issues existantes

---

## Merci pour votre contribution ! 🙌

Chaque contribution nous aide à rendre BabiCouture meilleur.

**Happy coding! 🚀**

---

Dernière mise à jour : Avril 2026
