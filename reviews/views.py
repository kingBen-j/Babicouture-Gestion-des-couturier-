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
from orders.models import Commande
from reviews.models import Evaluation

@login_required
def evaluer_couturier(request, couturier_id):
    """Évaluer un couturier"""
    couturier = get_object_or_404(Couturier, id=couturier_id)
    client = get_object_or_404(Client, user=request.user)
    
    # Vérifier si le client a déjà commandé chez ce couturier
    has_ordered = Commande.objects.filter(
        client=client,
        couturier=couturier,
        statut='terminee'
    ).exists()
    
    if not has_ordered:
        messages.error(request, "Vous devez avoir terminé une commande avec ce couturier pour le noter.")
        return redirect('client_dashboard')
    
    # Vérifier si l'utilisateur a déjà évalué ce couturier
    existing_evaluation = Evaluation.objects.filter(
        couturier=couturier,
        client=client
    ).first()
    
    if request.method == 'POST':
        note = request.POST.get('note')
        commentaire = request.POST.get('commentaire', '').strip()
        
        if not note:
            messages.error(request, "Veuillez donner une note.")
            return render(request, 'BabiCouture/evaluation/evaluer_couturier.html', {
                'couturier': couturier,
                'existing_evaluation': existing_evaluation
            })
        
        try:
            note = float(note)
            if 1 <= note <= 5:
                if existing_evaluation:
                    # Mettre à jour l'évaluation existante
                    existing_evaluation.note = note
                    existing_evaluation.commentaire = commentaire
                    existing_evaluation.save()
                    action = "mise à jour"
                else:
                    # Créer une nouvelle évaluation
                    Evaluation.objects.create(
                        couturier=couturier,
                        client=client,
                        note=note,
                        commentaire=commentaire
                    )
                    action = "enregistrée"
                
                # Mettre à jour la note moyenne du couturier
                evaluations = Evaluation.objects.filter(couturier=couturier)
                moyenne = evaluations.aggregate(Avg('note'))['note__avg']
                couturier.note_moyenne = moyenne if moyenne else 0
                couturier.nombre_avis = evaluations.count()
                couturier.save()
                
                # Envoyer une notification au couturier
                if not existing_evaluation:  # Seulement pour les nouvelles évaluations
                    Message.objects.create(
                        expediteur=request.user,
                        destinataire=couturier.user,
                        sujet=f"Nouvelle évaluation: {note}/5",
                        contenu=f"Le client {client.user.get_full_name() or client.user.username} vous a évalué avec {note}/5 étoiles.\n\n"
                               f"Commentaire: {commentaire or 'Aucun commentaire'}"
                    )
                
                messages.success(request, f"Évaluation {action} avec succès !")
                return redirect('client_dashboard')
            else:
                messages.error(request, "La note doit être entre 1 et 5.")
        except ValueError:
            messages.error(request, "Note invalide.")
    
    context = {
        'couturier': couturier,
        'existing_evaluation': existing_evaluation
    }
    return render(request, 'BabiCouture/evaluation.html', context)

@login_required
def mes_evaluations(request):
    """Voir les évaluations reçues (pour couturier)"""
    couturier = get_object_or_404(Couturier, user=request.user)
    
    # Récupérer les évaluations
    evaluations = Evaluation.objects.filter(
        couturier=couturier
    ).select_related('client__user').order_by('-date_creation')
    
    # Filtres
    note_filter = request.GET.get('note')
    if note_filter:
        try:
            evaluations = evaluations.filter(note=int(note_filter))
        except ValueError:
            pass
    
    search_query = request.GET.get('search', '')
    if search_query:
        evaluations = evaluations.filter(
            Q(commentaire__icontains=search_query) |
            Q(client__user__username__icontains=search_query) |
            Q(client__user__first_name__icontains=search_query) |
            Q(client__user__last_name__icontains=search_query)
        )
    
    # Calculer les statistiques
    stats = {
        'total': evaluations.count(),
        'moyenne': evaluations.aggregate(Avg('note'))['note__avg'] or 0,
        'par_note': {
            5: evaluations.filter(note=5).count(),
            4: evaluations.filter(note=4).count(),
            3: evaluations.filter(note=3).count(),
            2: evaluations.filter(note=2).count(),
            1: evaluations.filter(note=1).count(),
        }
    }
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = 10
    total_evaluations = evaluations.count()
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    evaluations_page = evaluations[start_idx:end_idx]
    
    context = {
        'couturier': couturier,
        'evaluations': evaluations_page,
        'stats': stats,
        'search_query': search_query,
        'note_filter': note_filter,
        'page': page,
        'total_pages': (total_evaluations + per_page - 1) // per_page,
    }
    return render(request, 'BabiCouture/mes_evaluations.html', context)

@login_required
def repondre_evaluation(request, evaluation_id):
    """Répondre à une évaluation (pour couturier)"""
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    couturier = get_object_or_404(Couturier, user=request.user)
    
    # Vérifier que l'évaluation concerne bien ce couturier
    if evaluation.couturier != couturier:
        messages.error(request, "Cette évaluation ne vous concerne pas.")
        return redirect('mes_evaluations')
    
    if request.method == 'POST':
        reponse = request.POST.get('reponse', '').strip()
        
        if not reponse:
            messages.error(request, "La réponse ne peut pas être vide.")
            return render(request, 'BabiCouture/evaluation/repondre.html', {
                'evaluation': evaluation
            })
        
        # Mettre à jour la réponse
        evaluation.reponse = reponse
        evaluation.date_reponse = timezone.now()
        evaluation.save()
        
        # Envoyer une notification au client
        Message.objects.create(
            expediteur=request.user,
            destinataire=evaluation.client.user,
            sujet=f"Réponse à votre évaluation",
            contenu=f"Le couturier {couturier.user.get_full_name() or couturier.user.username} a répondu à votre évaluation:\n\n"
                   f"Votre commentaire: {evaluation.commentaire or 'Aucun commentaire'}\n"
                   f"Votre note: {evaluation.note}/5\n\n"
                   f"Réponse du couturier: {reponse}"
        )
        
        messages.success(request, "Réponse envoyée avec succès !")
        return redirect('mes_evaluations')
    
    return render(request, 'BabiCouture/evaluation/repondre.html', {
        'evaluation': evaluation
    })
