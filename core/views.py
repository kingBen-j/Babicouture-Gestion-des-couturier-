from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
import json
from datetime import datetime, timedelta
from users.models import Client, Couturier
from catalog.models import Modele
from orders.models import Commande
from messaging.models import Message, Conversation
from reviews.models import Evaluation

def loader(request):
    return render(request, 'BabiCouture/loader.html')

def home(request):
    # Afficher quelques modèles populaires sur la page d'accueil
    modeles_populaires = Modele.objects.select_related('couturier').annotate(
        nb_commandes=Count('commandes')
    ).order_by('-nb_commandes')[:6]
    
    top_couturiers = Couturier.objects.select_related('user').annotate(
        note_calculee=Avg('evaluations__note'),
        nb_evaluations=Count('evaluations')
    ).filter(note_calculee__isnull=False).order_by('-note_calculee')[:4]
    
    # Modèles récents
    modeles_recents = Modele.objects.select_related('couturier').order_by('-date_creation')[:6]
    
    context = {
        'modeles_populaires': modeles_populaires,
        'top_couturiers': top_couturiers,
        'modeles_recents': modeles_recents,
    }
    return render(request, 'BabiCouture/index.html', context)

@login_required
def client_dashboard(request):
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        messages.error(request, "Profil client introuvable. Veuillez choisir un rôle.")
        return redirect('choose_role')

    # Modèles disponibles (limités pour l'affichage)
    modeles = Modele.objects.select_related('couturier', 'couturier__user').order_by('-date_creation')[:12]
    
    # Commandes du client (limitées à 10 pour l'affichage)
    commandes_affichage = Commande.objects.filter(client=client).select_related(
        'couturier', 'couturier__user', 'modele'
    ).order_by('-date_commande')[:10]
    
    # Statistiques des commandes
    commandes_en_cours = Commande.objects.filter(
        client=client,
        statut__in=['en_attente', 'en_cours', 'confirmee', 'livree']
    ).count()
    
    commandes_terminees = Commande.objects.filter(
        client=client,
        statut='terminee'
    ).count()
    
    # Total dépenses
    total_depenses = Commande.objects.filter(
        client=client,
        statut__in=['terminee', 'livree']
    ).aggregate(total=Sum('prix_final'))['total'] or 0

    # Top couturiers
    top_couturiers = Couturier.objects.select_related('user').annotate(
        note_calculee=Avg('evaluations__note'),
        nb_evaluations=Count('evaluations')
    ).filter(note_calculee__isnull=False).order_by('-note_calculee')[:5]

    # Messages non lus
    messages_non_lus = Message.objects.filter(
        destinataire=request.user, 
        lu=False
    ).count()
    
    # Derniers messages reçus
    derniers_messages = Message.objects.filter(
        destinataire=request.user
    ).select_related('expediteur').order_by('-date_envoi')[:5]

    # Commandes récentes (pour les notifications)
    commandes_recentes = Commande.objects.filter(
        client=client,
        date_commande__gte=timezone.now() - timedelta(days=7)
    ).count()

    context = {
        'client': client,
        'modeles': modeles,
        'commandes': commandes_affichage,
        'commandes_en_cours': commandes_en_cours,
        'commandes_terminees': commandes_terminees,
        'total_depenses': total_depenses,
        'top_couturiers': top_couturiers,
        'messages_non_lus': messages_non_lus,
        'messages_recus': derniers_messages,
        'commandes_recentes': commandes_recentes,
    }

    return render(request, 'BabiCouture/client_dashboard.html', context)

@login_required
def tailor_dashboard(request):
    try:
        couturier = Couturier.objects.get(user=request.user)
    except Couturier.DoesNotExist:
        messages.error(request, "Profil couturier introuvable. Veuillez choisir un rôle.")
        return redirect('choose_role')

    # Modèles du couturier
    modeles = Modele.objects.filter(couturier=couturier).order_by('-date_creation')[:6]
    
    # Statistiques des commandes
    commandes = Commande.objects.filter(couturier=couturier)
    commandes_total = commandes.count()
    commandes_terminees = commandes.filter(statut='terminee').count()
    commandes_en_cours = commandes.filter(
        statut__in=['en_attente', 'en_cours', 'confirmee', 'livree']
    ).count()
    
    clients_total = Client.objects.filter(
        commandes__couturier=couturier
    ).distinct().count()
    
    # Revenus
    revenus_totaux = commandes.filter(
        statut='terminee'
    ).aggregate(total=Sum('prix_final'))['total'] or 0
    
    # Messages non lus
    messages_non_lus = Message.objects.filter(
        destinataire=request.user, 
        lu=False
    ).count()
    
    # Dernières évaluations
    dernieres_evaluations = Evaluation.objects.filter(
        couturier=couturier
    ).select_related('client__user').order_by('-date_creation')[:3]

    # Commandes en attente
    commandes_attente = Commande.objects.filter(
        couturier=couturier,
        statut='en_attente'
    ).count()

    # Prochaines livraisons
    prochaines_livraisons = Commande.objects.filter(
        couturier=couturier,
        date_livraison_prevue__gte=timezone.now().date(),
        statut__in=['en_cours', 'confirmee']
    ).order_by('date_livraison_prevue')[:5]

    context = {
        'couturier': couturier,
        'modeles': modeles,
        'commandes_total': commandes_total,
        'commandes_terminees': commandes_terminees,
        'commandes_en_cours': commandes_en_cours,
        'clients_total': clients_total,
        'revenus_totaux': revenus_totaux,
        'messages_non_lus': messages_non_lus,
        'dernieres_evaluations': dernieres_evaluations,
        'commandes_attente': commandes_attente,
        'prochaines_livraisons': prochaines_livraisons,
    }

    return render(request, 'BabiCouture/tailor_dashboard.html', context)

@login_required
def admin_dashboard(request):
    """Tableau de bord administrateur"""
    if not request.user.is_superuser:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('home')
    
    # Statistiques générales
    aujourdhui = timezone.now().date()
    hier = aujourdhui - timedelta(days=1)
    semaine_derniere = aujourdhui - timedelta(days=7)
    mois_dernier = aujourdhui - timedelta(days=30)
    
    stats = {
        'clients_total': Client.objects.count(),
        'couturiers_total': Couturier.objects.count(),
        'modeles_total': Modele.objects.count(),
        'commandes_total': Commande.objects.count(),
        'messages_total': Message.objects.count(),
        'evaluations_total': Evaluation.objects.count(),
        
        'nouveaux_clients_jour': Client.objects.filter(
            user__date_joined__date=aujourdhui
        ).count(),
        'nouveaux_couturiers_jour': Couturier.objects.filter(
            user__date_joined__date=aujourdhui
        ).count(),
        'commandes_jour': Commande.objects.filter(
            date_commande__date=aujourdhui
        ).count(),
        'revenus_jour': Commande.objects.filter(
            date_commande__date=aujourdhui,
            statut='terminee'
        ).aggregate(total=Sum('prix_final'))['total'] or 0,
        
        'commandes_semaine': Commande.objects.filter(
            date_commande__date__gte=semaine_derniere
        ).count(),
        'commandes_mois': Commande.objects.filter(
            date_commande__date__gte=mois_dernier
        ).count(),
        'revenus_mois': Commande.objects.filter(
            date_commande__date__gte=mois_dernier,
            statut='terminee'
        ).aggregate(total=Sum('prix_final'))['total'] or 0,
    }
    
    # Dernières activités
    dernieres_commandes = Commande.objects.select_related(
        'client__user', 'couturier__user'
    ).order_by('-date_commande')[:10]
    
    dernieres_evaluations = Evaluation.objects.select_related(
        'client__user', 'couturier__user'
    ).order_by('-date_creation')[:10]
    
    derniers_utilisateurs = User.objects.order_by('-date_joined')[:10]
    
    # Commandes par statut
    commandes_par_statut = {}
    for statut_code, statut_label in Commande.STATUT_CHOICES:
        commandes_par_statut[statut_label] = Commande.objects.filter(statut=statut_code).count()
    
    context = {
        'stats': stats,
        'dernieres_commandes': dernieres_commandes,
        'dernieres_evaluations': dernieres_evaluations,
        'derniers_utilisateurs': derniers_utilisateurs,
        'commandes_par_statut': commandes_par_statut,
    }
    return render(request, 'BabiCouture/admin/dashboard.html', context)

@login_required
def gestion_utilisateurs(request):
    """Gestion des utilisateurs pour l'admin"""
    if not request.user.is_superuser:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('home')
    
    users = User.objects.select_related('client', 'couturier').all()
    
    # Filtres
    role = request.GET.get('role')
    if role == 'client':
        users = users.filter(client__isnull=False)
    elif role == 'couturier':
        users = users.filter(couturier__isnull=False)
    elif role == 'admin':
        users = users.filter(is_superuser=True)
    
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = 20
    total_users = users.count()
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    users_page = users[start_idx:end_idx]
    
    context = {
        'users': users_page,
        'role_filter': role,
        'search_query': search_query or '',
        'page': page,
        'total_pages': (total_users + per_page - 1) // per_page,
    }
    return render(request, 'BabiCouture/admin/gestion_utilisateurs.html', context)

@login_required
def statistiques_detaillees(request):
    """Statistiques détaillées pour l'admin"""
    if not request.user.is_superuser:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('home')
    
    # Période
    periode = request.GET.get('periode', 'mois')
    aujourdhui = timezone.now().date()
    
    if periode == 'jour':
        date_debut = aujourdhui
    elif periode == 'semaine':
        date_debut = aujourdhui - timedelta(days=7)
    elif periode == 'mois':
        date_debut = aujourdhui - timedelta(days=30)
    else:  # année
        date_debut = aujourdhui - timedelta(days=365)
    
    # Commandes par statut
    commandes_par_statut = {}
    for statut_code, statut_label in Commande.STATUT_CHOICES:
        count = Commande.objects.filter(
            statut=statut_code,
            date_commande__date__gte=date_debut
        ).count()
        commandes_par_statut[statut_label] = count
    
    # Évaluations par note
    evaluations_par_note = {}
    for i in range(1, 6):
        count = Evaluation.objects.filter(
            note=i,
            date_creation__date__gte=date_debut
        ).count()
        evaluations_par_note[f"{i} étoile{'s' if i > 1 else ''}"] = count
    
    # Couturiers les plus actifs
    couturiers_actifs = Couturier.objects.annotate(
        nb_commandes=Count('commandes'),
        revenus_totaux=Sum('commandes__prix_final', filter=Q(commandes__statut='terminee'))
    ).order_by('-nb_commandes')[:10]
    
    # Clients les plus actifs
    clients_actifs = Client.objects.annotate(
        nb_commandes=Count('commandes'),
        depenses_totales=Sum('commandes__prix_final', filter=Q(commandes__statut__in=['terminee', 'livree']))
    ).order_by('-nb_commandes')[:10]
    
    # Évolution des inscriptions
    jours = 30 if periode == 'mois' else 7 if periode == 'semaine' else 365
    inscriptions_journalieres = []
    for i in range(jours):
        date = aujourdhui - timedelta(days=i)
        nb_clients = Client.objects.filter(user__date_joined__date=date).count()
        nb_couturiers = Couturier.objects.filter(user__date_joined__date=date).count()
        inscriptions_journalieres.append({
            'date': date.strftime('%d/%m'),
            'clients': nb_clients,
            'couturiers': nb_couturiers,
        })
    
    context = {
        'periode': periode,
        'commandes_par_statut': commandes_par_statut,
        'evaluations_par_note': evaluations_par_note,
        'couturiers_actifs': couturiers_actifs,
        'clients_actifs': clients_actifs,
        'inscriptions_journalieres': reversed(inscriptions_journalieres),
    }
    return render(request, 'BabiCouture/statistiques.html', context)

@login_required
def toggle_user_active(request, user_id):
    """Activer/désactiver un utilisateur"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    return JsonResponse({
        'success': True,
        'is_active': user.is_active,
        'message': f"Utilisateur {'activé' if user.is_active else 'désactivé'} avec succès."
    })

def page_404(request, exception):
    """Page d'erreur 404 personnalisée"""
    return render(request, 'BabiCouture/404.html', status=404)

def page_500(request):
    """Page d'erreur 500 personnalisée"""
    return render(request, 'BabiCouture/500.html', status=500)

def conditions_utilisation(request):
    """Page des conditions d'utilisation"""
    return render(request, 'BabiCouture/info/conditions_utilisation.html')

def politique_confidentialite(request):
    """Page de politique de confidentialité"""
    return render(request, 'BabiCouture/info/politique_confidentialite.html')

def contact(request):
    """Page de contact"""
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        email = request.POST.get('email', '').strip()
        sujet = request.POST.get('sujet', '').strip()
        message = request.POST.get('message', '').strip()
        
        if not all([nom, email, sujet, message]):
            messages.error(request, "Veuillez remplir tous les champs.")
            return render(request, 'BabiCouture/info/contact.html')
        
        # Enregistrer le message de contact
        # Note: Vous pourriez créer un modèle ContactMessage pour cela
        # Pour l'instant, on envoie un message aux administrateurs
        admin_users = User.objects.filter(is_superuser=True, is_active=True)
        for admin in admin_users:
            Message.objects.create(
                expediteur=None,  # Ou créer un utilisateur "contact"
                destinataire=admin,
                sujet=f"[CONTACT] {sujet}",
                contenu=f"Message de contact:\n\n"
                       f"Nom: {nom}\n"
                       f"Email: {email}\n"
                       f"Sujet: {sujet}\n\n"
                       f"Message:\n{message}"
            )
        
        messages.success(request, "Votre message a été envoyé. Nous vous répondrons bientôt !")
        return redirect('contact')
    
    return render(request, 'BabiCouture/info/contact.html')

def a_propos(request):
    """Page À propos"""
    stats = {
        'couturiers': Couturier.objects.count(),
        'modeles': Modele.objects.count(),
        'commandes_terminees': Commande.objects.filter(statut='terminee').count(),
        'clients': Client.objects.count(),
    }
    
    return render(request, 'BabiCouture/info/a_propos.html', {'stats': stats})

def faq(request):
    """Page FAQ"""
    faqs = [
        {
            'question': 'Comment passer une commande ?',
            'reponse': 'Pour passer une commande, rendez-vous sur la page d\'un modèle qui vous intéresse et cliquez sur "Commander". Vous pouvez également créer une commande personnalisée en choisissant directement un couturier.'
        },
        {
            'question': 'Comment contacter un couturier ?',
            'reponse': 'Vous pouvez contacter un couturier en allant sur son profil et en cliquant sur "Contacter" ou en utilisant le système de messagerie intégré depuis votre tableau de bord.'
        },
        {
            'question': 'Comment évaluer un couturier ?',
            'reponse': 'Pour évaluer un couturier, vous devez avoir terminé au moins une commande avec lui. Ensuite, allez sur son profil et cliquez sur "Noter" ou utilisez le lien depuis vos commandes terminées.'
        },
        {
            'question': 'Quels sont les modes de paiement acceptés ?',
            'reponse': 'Les modes de paiement sont convenus directement entre le client et le couturier. Nous vous recommandons d\'utiliser des moyens sécurisés comme Orange Money, Wave, ou les transferts bancaires.'
        },
        {
            'question': 'Combien de temps prend la confection d\'un vêtement ?',
            'reponse': 'Le délai dépend du type de vêtement, de la complexité et du couturier. En général, il faut compter entre 3 et 14 jours. Le délai est indiqué lors de la commande et confirmé par le couturier.'
        },
        {
            'question': 'Que faire en cas de problème avec une commande ?',
            'reponse': 'En cas de problème, contactez d\'abord le couturier via la messagerie. Si le problème persiste, vous pouvez signaler la commande depuis la page de détails de la commande.'
        },
        {
            'question': 'Comment devenir couturier sur Babi Couture ?',
            'reponse': 'Pour devenir couturier, créez un compte et choisissez le rôle "Couturier" lors de l\'inscription. Vous devrez fournir vos informations professionnelles et une photo de profil.'
        },
        {
            'question': 'Puis-je annuler une commande ?',
            'reponse': 'Vous pouvez annuler une commande tant qu\'elle n\'est pas en cours de confection. Les commandes avec le statut "en attente" ou "confirmée" peuvent être annulées depuis la page de détails de la commande.'
        }
    ]
    
    context = {
        'faqs': faqs
    }
    return render(request, 'BabiCouture/info/faq.html', context)

@login_required
def get_notifications(request):
    """Récupérer les notifications (AJAX)"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        messages_non_lus = Message.objects.filter(
            destinataire=request.user,
            lu=False
        ).count()
        
        # Commandes en attente pour les couturiers
        commandes_attente = 0
        if hasattr(request.user, 'couturier'):
            commandes_attente = Commande.objects.filter(
                couturier=request.user.couturier,
                statut='en_attente'
            ).count()
        
        # Commandes avec mise à jour pour les clients
        commandes_mises_a_jour = 0
        if hasattr(request.user, 'client'):
            # Commandes dont le statut a changé récemment (24h)
            recent = timezone.now() - timedelta(hours=24)
            commandes_mises_a_jour = Commande.objects.filter(
                client=request.user.client,
                date_modification__gte=recent
            ).exclude(statut='terminee').count()
        
        return JsonResponse({
            'success': True,
            'messages_non_lus': messages_non_lus,
            'commandes_attente': commandes_attente,
            'commandes_mises_a_jour': commandes_mises_a_jour,
            'total_notifications': messages_non_lus + commandes_attente + commandes_mises_a_jour,
        })
    return JsonResponse({'success': False, 'error': 'Requête invalide'}, status=400)

@login_required
def get_stats_dashboard(request):
    """Récupérer les statistiques pour le dashboard (AJAX)"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        stats = {}
        
        if hasattr(request.user, 'client'):
            client = request.user.client
            stats['commandes_en_cours'] = Commande.objects.filter(
                client=client,
                statut__in=['en_attente', 'en_cours', 'confirmee', 'livree']
            ).count()
            stats['total_depenses'] = Commande.objects.filter(
                client=client,
                statut__in=['terminee', 'livree']
            ).aggregate(total=Sum('prix_final'))['total'] or 0
        
        elif hasattr(request.user, 'couturier'):
            couturier = request.user.couturier
            stats['commandes_en_cours'] = Commande.objects.filter(
                couturier=couturier,
                statut__in=['en_attente', 'en_cours', 'confirmee', 'livree']
            ).count()
            stats['revenus_totaux'] = Commande.objects.filter(
                couturier=couturier,
                statut='terminee'
            ).aggregate(total=Sum('prix_final'))['total'] or 0
        
        return JsonResponse({'success': True, 'stats': stats})
    
    return JsonResponse({'success': False, 'error': 'Requête invalide'}, status=400)

def test_page(request):
    """Page de test pour le développement"""
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('home')
    
    context = {
        'user': request.user,
        'is_client': hasattr(request.user, 'client'),
        'is_couturier': hasattr(request.user, 'couturier'),
        'is_admin': request.user.is_superuser,
    }
    return render(request, 'BabiCouture/test.html', context)

def clear_messages(request):
    """Effacer tous les messages flash (développement seulement)"""
    if not request.user.is_superuser:
        return redirect('home')
    
    storage = messages.get_messages(request)
    storage.used = True  # Marquer tous les messages comme lus
    
    return JsonResponse({'success': True, 'message': 'Messages flash effacés'})

def login_view_redirect(request):
    """Redirection pour compatibilité avec les anciens templates"""
    return redirect('login')