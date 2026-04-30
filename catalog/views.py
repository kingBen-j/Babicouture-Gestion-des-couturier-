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

@login_required
def mes_modeles(request):
    try:
        couturier = Couturier.objects.get(user=request.user)
    except Couturier.DoesNotExist:
        messages.error(request, "Aucun compte couturier associé.")
        return redirect('home')

    if request.method == 'POST':
        form = ModeleForm(request.POST, request.FILES)
        if form.is_valid():
            modele = form.save(commit=False)
            modele.couturier = couturier
            modele.save()
            messages.success(request, "Modèle ajouté avec succès.")
            return redirect('mes_modeles')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ModeleForm()

    modeles = Modele.objects.filter(couturier=couturier).order_by('-date_creation')

    # Statistiques pour les modèles
    stats_modeles = {
        'total': modeles.count(),
        'avec_photos': modeles.exclude(image__exact='').count(),
        'avec_prix': modeles.exclude(prix__isnull=True).count(),
    }

    context = {
        'form': form,
        'modeles': modeles,
        'couturier': couturier,
        'stats_modeles': stats_modeles,
    }

    return render(request, 'BabiCouture/modele.html', context)

def boutique(request):
    """Page boutique avec tous les modèles"""
    modeles = Modele.objects.select_related('couturier', 'couturier__user').order_by('-date_creation')
    
    # Filtres
    couturier_id = request.GET.get('couturier')
    if couturier_id:
        modeles = modeles.filter(couturier_id=couturier_id)
    
    categorie = request.GET.get('categorie')
    if categorie:
        modeles = modeles.filter(categorie=categorie)
    
    # Prix min/max
    prix_min = request.GET.get('prix_min')
    prix_max = request.GET.get('prix_max')
    if prix_min:
        try:
            modeles = modeles.filter(prix__gte=float(prix_min))
        except ValueError:
            pass
    if prix_max:
        try:
            modeles = modeles.filter(prix__lte=float(prix_max))
        except ValueError:
            pass
    
    # Recherche
    search_query = request.GET.get('q')
    if search_query:
        modeles = modeles.filter(
            Q(titre__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(couturier__user__username__icontains=search_query) |
            Q(couturier__user__first_name__icontains=search_query) |
            Q(couturier__user__last_name__icontains=search_query)
        )
    
    # Couturiers pour le filtre
    couturiers = Couturier.objects.select_related('user').all()
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = 12
    total_modeles = modeles.count()
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    modeles_page = modeles[start_idx:end_idx]
    
    context = {
        'modeles': modeles_page,
        'couturiers': couturiers,
        'categories': Modele.TYPE_CHOICES,
        'search_query': search_query or '',
        'page': page,
        'total_pages': (total_modeles + per_page - 1) // per_page,
        'filtres': {
            'couturier': couturier_id,
            'categorie': categorie,
            'prix_min': prix_min,
            'prix_max': prix_max,
        }
    }
    return render(request, 'BabiCouture/boutique.html', context)

def details_modele(request, modele_id):
    """Détails d'un modèle"""
    modele = get_object_or_404(Modele.objects.select_related('couturier', 'couturier__user'), id=modele_id)
    
    # Modèles similaires (même catégorie ou même couturier)
    modeles_similaires = Modele.objects.filter(
        Q(categorie=modele.categorie) | Q(couturier=modele.couturier)
    ).exclude(id=modele_id).distinct().order_by('-date_creation')[:4]
    
    # Évaluations du couturier
    evaluations_couturier = Evaluation.objects.filter(
        couturier=modele.couturier
    ).select_related('client__user').order_by('-date_creation')[:5]
    
    # Statistiques du modèle
    stats_modele = {
        'nb_commandes': Commande.objects.filter(modele=modele).count(),
        'note_couturier': modele.couturier.note_moyenne or 0,
        'nb_avis_couturier': modele.couturier.nombre_avis or 0,
    }
    
    context = {
        'modele': modele,
        'modeles_similaires': modeles_similaires,
        'evaluations_couturier': evaluations_couturier,
        'stats_modele': stats_modele,
    }
    return render(request, 'BabiCouture/modele/details.html', context)

def liste_couturiers(request):
    """Liste de tous les couturiers"""
    couturiers = Couturier.objects.select_related('user').annotate(
        note_calculee=Avg('evaluations__note'),
        nb_evaluations=Count('evaluations'),
        nb_modeles=Count('modeles')
    ).order_by('-note_calculee')
    
    # Filtres
    specialite = request.GET.get('specialite')
    if specialite:
        couturiers = couturiers.filter(specialite__icontains=specialite)
    
    note_min = request.GET.get('note_min')
    if note_min:
        try:
            couturiers = couturiers.filter(note_calculee__gte=float(note_min))
        except ValueError:
            pass
    
    ville = request.GET.get('ville')
    if ville:
        couturiers = couturiers.filter(adresse__icontains=ville)
    
    # Recherche
    search_query = request.GET.get('q')
    if search_query:
        couturiers = couturiers.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialite__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Liste des spécialités disponibles
    specialites = Couturier.objects.exclude(specialite='').values_list('specialite', flat=True).distinct()
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = 12
    total_couturiers = couturiers.count()
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    couturiers_page = couturiers[start_idx:end_idx]
    
    context = {
        'couturiers': couturiers_page,
        'specialites': specialites,
        'search_query': search_query or '',
        'page': page,
        'total_pages': (total_couturiers + per_page - 1) // per_page,
        'filtres': {
            'specialite': specialite,
            'note_min': note_min,
            'ville': ville,
        }
    }
    return render(request, 'BabiCouture/couturier/liste.html', context)

def details_couturier(request, couturier_id):
    """Détails d'un couturier"""
    couturier = get_object_or_404(Couturier.objects.select_related('user'), id=couturier_id)
    
    # Modèles du couturier
    modeles = Modele.objects.filter(couturier=couturier).order_by('-date_creation')[:8]
    
    # Évaluations
    evaluations = Evaluation.objects.filter(
        couturier=couturier
    ).select_related('client__user').order_by('-date_creation')[:10]
    
    # Statistiques
    stats = {
        'modeles_total': Modele.objects.filter(couturier=couturier).count(),
        'commandes_terminees': Commande.objects.filter(couturier=couturier, statut='terminee').count(),
        'note_moyenne': couturier.note_moyenne or 0,
        'nb_evaluations': couturier.nombre_avis or 0,
        'clients_total': Client.objects.filter(commande__couturier=couturier).distinct().count(),
    }
    
    # Note par étoile
    note_par_etoile = {}
    for i in range(1, 6):
        note_par_etoile[i] = Evaluation.objects.filter(couturier=couturier, note=i).count()
    
    context = {
        'couturier': couturier,
        'modeles': modeles,
        'evaluations': evaluations,
        'stats': stats,
        'note_par_etoile': note_par_etoile,
    }
    return render(request, 'BabiCouture/couturier/details.html', context)

def recherche(request):
    """Page de recherche unifiée"""
    query = request.GET.get('q', '').strip()
    type_recherche = request.GET.get('type', 'tout')
    
    results = {
        'modeles': Modele.objects.none(),
        'couturiers': Couturier.objects.none(),
    }
    
    if query:
        if type_recherche in ['tout', 'modeles']:
            results['modeles'] = Modele.objects.select_related('couturier', 'couturier__user').filter(
                Q(titre__icontains=query) |
                Q(description__icontains=query) |
                Q(categorie__icontains=query) |
                Q(couturier__user__username__icontains=query) |
                Q(couturier__user__first_name__icontains=query) |
                Q(couturier__user__last_name__icontains=query)
            ).order_by('-date_creation')
        
        if type_recherche in ['tout', 'couturiers']:
            results['couturiers'] = Couturier.objects.select_related('user').filter(
                Q(user__username__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(specialite__icontains=query) |
                Q(description__icontains=query) |
                Q(adresse__icontains=query)
            ).order_by('-note_moyenne')
    
    # Limiter les résultats
    results['modeles'] = results['modeles'][:8]
    results['couturiers'] = results['couturiers'][:6]
    
    context = {
        'query': query,
        'type_recherche': type_recherche,
        'results': results,
        'count_modeles': results['modeles'].count(),
        'count_couturiers': results['couturiers'].count(),
    }
    return render(request, 'BabiCouture/recherche.html', context)

def rechercher_couturiers(request):
    """Recherche avancée de couturiers"""
    # Cette fonction est redondante avec liste_couturiers, on peut rediriger
    return redirect('liste_couturiers')

def rechercher_modeles(request):
    """Recherche avancée de modèles"""
    # Cette fonction est redondante avec boutique, on peut rediriger
    return redirect('boutique')

@login_required
def creer_modele(request):
    """Créer un nouveau modèle"""
    couturier = get_object_or_404(Couturier, user=request.user)
    
    if request.method == 'POST':
        form = ModeleForm(request.POST, request.FILES)
        if form.is_valid():
            modele = form.save(commit=False)
            modele.couturier = couturier
            modele.save()
            messages.success(request, "Modèle créé avec succès !")
            return redirect('mes_modeles')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ModeleForm()
    
    return render(request, 'BabiCouture/modele/creer.html', {
        'form': form,
        'couturier': couturier
    })

@login_required
def modifier_modele(request, modele_id):
    """Modifier un modèle existant"""
    modele = get_object_or_404(Modele, id=modele_id)
    couturier = get_object_or_404(Couturier, user=request.user)
    
    # Vérifier que le couturier est propriétaire du modèle
    if modele.couturier != couturier:
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce modèle.")
        return redirect('mes_modeles')
    
    if request.method == 'POST':
        form = ModeleForm(request.POST, request.FILES, instance=modele)
        if form.is_valid():
            form.save()
            messages.success(request, "Modèle modifié avec succès !")
            return redirect('mes_modeles')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ModeleForm(instance=modele)
    
    return render(request, 'BabiCouture/modele/modifier.html', {
        'form': form,
        'modele': modele,
        'couturier': couturier
    })

@login_required
def supprimer_modele(request, modele_id):
    """Supprimer un modèle"""
    modele = get_object_or_404(Modele, id=modele_id)
    couturier = get_object_or_404(Couturier, user=request.user)
    
    # Vérifier que le couturier est propriétaire du modèle
    if modele.couturier != couturier:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer ce modèle.")
        return redirect('mes_modeles')
    
    if request.method == 'POST':
        titre = modele.titre
        modele.delete()
        messages.success(request, f"Modèle '{titre}' supprimé avec succès !")
        return redirect('mes_modeles')
    
    return render(request, 'BabiCouture/modele/supprimer.html', {
        'modele': modele,
        'couturier': couturier
    })
