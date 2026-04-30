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
from messaging.models import Message, Conversation

@login_required
def envoyer_message(request, destinataire_id=None):
    """Envoyer un message à un autre utilisateur"""
    
    if request.method == 'POST':
        # Si on a un destinataire_id dans l'URL
        if destinataire_id:
            destinataire = get_object_or_404(User, id=destinataire_id)
        else:
            # Sinon, on cherche par username
            destinataire_username = request.POST.get('destinataire')
            if destinataire_username:
                try:
                    destinataire = User.objects.get(username=destinataire_username)
                except User.DoesNotExist:
                    messages.error(request, "Destinataire introuvable.")
                    return redirect('envoyer_message')
            else:
                messages.error(request, "Veuillez spécifier un destinataire.")
                return redirect('envoyer_message')
        
        sujet = request.POST.get('sujet', 'Nouveau message').strip()
        contenu = request.POST.get('contenu', '').strip()
        
        if not contenu:
            messages.error(request, "Le message ne peut pas être vide.")
            return redirect('envoyer_message')
        
        if destinataire == request.user:
            messages.error(request, "Vous ne pouvez pas vous envoyer un message à vous-même.")
            return redirect('envoyer_message')
        
        # Créer le message
        message = Message.objects.create(
            expediteur=request.user,
            destinataire=destinataire,
            sujet=sujet,
            contenu=contenu
        )
        
        messages.success(request, f"Message envoyé à {destinataire.get_full_name() or destinataire.username} !")
        return redirect('boite_reception')
    
    # Si GET ou erreur, préparer le contexte
    destinataire = None
    if destinataire_id:
        destinataire = get_object_or_404(User, id=destinataire_id)
    
    # Suggestions de destinataires (clients pour couturiers et vice-versa)
    suggestions = []
    if hasattr(request.user, 'client'):
        # Si c'est un client, suggérer les couturiers avec qui il a commandé
        couturiers_ids = Commande.objects.filter(
            client=request.user.client
        ).values_list('couturier__user_id', flat=True).distinct()
        suggestions = User.objects.filter(id__in=couturiers_ids).exclude(id=request.user.id)
    elif hasattr(request.user, 'couturier'):
        # Si c'est un couturier, suggérer les clients qui ont commandé chez lui
        clients_ids = Commande.objects.filter(
            couturier=request.user.couturier
        ).values_list('client__user_id', flat=True).distinct()
        suggestions = User.objects.filter(id__in=clients_ids).exclude(id=request.user.id)
    
    context = {
        'destinataire': destinataire,
        'suggestions': suggestions,
    }
    return render(request, 'BabiCouture/envoyer_message.html', context)

@login_required
def boite_reception(request):
    """Boîte de réception de l'utilisateur"""
    # Messages reçus
    messages_recus = Message.objects.filter(
        destinataire=request.user
    ).select_related('expediteur').order_by('-date_envoi')
    
    # Messages envoyés
    messages_envoyes = Message.objects.filter(
        expediteur=request.user
    ).select_related('destinataire').order_by('-date_envoi')
    
    # Marquer les messages non lus comme lus (seulement ceux qu'on affiche)
    messages_recus.filter(lu=False).update(lu=True)
    
    # Filtres
    type_message = request.GET.get('type', 'recus')
    search_query = request.GET.get('search', '')
    
    if search_query:
        if type_message == 'recus':
            messages_recus = messages_recus.filter(
                Q(sujet__icontains=search_query) |
                Q(contenu__icontains=search_query) |
                Q(expediteur__username__icontains=search_query)
            )
        else:
            messages_envoyes = messages_envoyes.filter(
                Q(sujet__icontains=search_query) |
                Q(contenu__icontains=search_query) |
                Q(destinataire__username__icontains=search_query)
            )
    
    # Pagination simple
    page = int(request.GET.get('page', 1))
    per_page = 20
    
    if type_message == 'recus':
        total_messages = messages_recus.count()
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        messages_page = messages_recus[start_idx:end_idx]
    else:
        total_messages = messages_envoyes.count()
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        messages_page = messages_envoyes[start_idx:end_idx]
    
    context = {
        'messages_recus': messages_recus[:per_page] if type_message == 'recus' else [],
        'messages_envoyes': messages_envoyes[:per_page] if type_message == 'envoyes' else [],
        'messages_page': messages_page,
        'type_message': type_message,
        'search_query': search_query,
        'page': page,
        'total_pages': (total_messages + per_page - 1) // per_page,
    }
    return render(request, 'BabiCouture/boite_reception.html', context)

@login_required
def lire_message(request, message_id):
    """Lire un message spécifique"""
    message = get_object_or_404(Message.objects.select_related('expediteur', 'destinataire'), id=message_id)
    
    # Vérifier que l'utilisateur est autorisé à voir ce message
    if message.destinataire != request.user and message.expediteur != request.user:
        messages.error(request, "Accès non autorisé.")
        return redirect('boite_reception')
    
    # Marquer comme lu si c'est le destinataire
    if message.destinataire == request.user and not message.lu:
        message.lu = True
        message.save()
    
    context = {
        'message': message,
        'is_destinataire': message.destinataire == request.user,
        'is_expediteur': message.expediteur == request.user,
    }
    return render(request, 'BabiCouture/lire_message.html', context)

@login_required
def repondre_message(request, message_id):
    """Répondre à un message"""
    message_original = get_object_or_404(Message.objects.select_related('expediteur'), id=message_id)
    
    # Vérifier que l'utilisateur est le destinataire
    if message_original.destinataire != request.user:
        messages.error(request, "Vous ne pouvez répondre qu'aux messages qui vous sont adressés.")
        return redirect('boite_reception')
    
    if request.method == 'POST':
        contenu = request.POST.get('contenu', '').strip()
        
        if not contenu:
            messages.error(request, "Le message ne peut pas être vide.")
            return render(request, 'BabiCouture/repondre_message.html', {
                'message_original': message_original
            })
        
        # Créer la réponse
        reponse = Message.objects.create(
            expediteur=request.user,
            destinataire=message_original.expediteur,
            sujet=f"Re: {message_original.sujet}",
            contenu=contenu
        )
        
        messages.success(request, "Réponse envoyée avec succès !")
        return redirect('lire_message', message_id=reponse.id)
    
    context = {
        'message_original': message_original
    }
    return render(request, 'BabiCouture/messagerie/repondre_message.html', context)

@login_required
def envoyer_message_dest(request, destinataire_id):
    """Envoyer un message à un destinataire spécifique"""
    return envoyer_message(request, destinataire_id)

@login_required
def supprimer_message(request, message_id):
    """Supprimer un message"""
    message = get_object_or_404(Message, id=message_id)
    
    # Vérifier que l'utilisateur est autorisé à supprimer ce message
    if message.expediteur != request.user and message.destinataire != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer ce message.")
        return redirect('boite_reception')
    
    if request.method == 'POST':
        # Marquer comme supprimé pour l'utilisateur
        if message.expediteur == request.user:
            message.supprime_expediteur = True
        if message.destinataire == request.user:
            message.supprime_destinataire = True
        
        # Si les deux ont supprimé, supprimer définitivement
        if message.supprime_expediteur and message.supprime_destinataire:
            message.delete()
            messages.success(request, "Message définitivement supprimé.")
        else:
            message.save()
            messages.success(request, "Message supprimé de votre boîte.")
        
        return redirect('boite_reception')
    
    return render(request, 'BabiCouture/supprimer_message.html', {
        'message': message
    })

@login_required
def marquer_message_lu(request, message_id):
    """Marquer un message comme lu (AJAX)"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        message = get_object_or_404(Message, id=message_id, destinataire=request.user)
        message.lu = True
        message.save()
        return JsonResponse({'status': 'success', 'message_id': message_id})
    return JsonResponse({'status': 'error', 'message': 'Requête invalide'}, status=400)
