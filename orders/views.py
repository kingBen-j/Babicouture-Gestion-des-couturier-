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
from messaging.models import Message
from .forms import CommandeModeleForm, CommandePersonnaliseeForm


@login_required
def passer_commande(request, modele_id):
    """Passer une commande pour un modèle (vue simplifiée pour compatibilité)"""
    return redirect('creer_commande', modele_id=modele_id)


@login_required
def creer_commande(request, modele_id):
    """Créer une commande basée sur un modèle existant"""
    modele = get_object_or_404(Modele, id=modele_id)
    client = get_object_or_404(Client, user=request.user)

    if request.method == 'POST':
        form = CommandeModeleForm(request.POST)
        if form.is_valid():
            prix_final = modele.prix
            description_supp = form.cleaned_data.get('description', '')

            commande = Commande.objects.create(
                client=client,
                couturier=modele.couturier,
                modele=modele,
                titre=f"Commande: {modele.titre}",
                description=f"{modele.description}\n\n{description_supp}",
                prix_propose=modele.prix,
                prix_final=prix_final,
                taille=form.cleaned_data.get('taille', ''),
                couleurs=form.cleaned_data.get('couleurs', ''),
                preferences=form.cleaned_data.get('preferences', ''),
                date_livraison_prevue=form.cleaned_data.get('date_livraison_prevue'),
                statut='en_attente'
            )

            mesures_text = form.cleaned_data.get('mesures', '')
            if mesures_text:
                try:
                    mesures_dict = json.loads(mesures_text) if mesures_text.strip().startswith('{') else {"texte": mesures_text}
                    commande.mesures_client = mesures_dict
                    commande.save()
                except json.JSONDecodeError:
                    commande.mesures_client = {"texte": mesures_text}
                    commande.save()

            Message.objects.create(
                expediteur=request.user,
                destinataire=modele.couturier.user,
                sujet=f"Nouvelle commande: {modele.titre}",
                contenu=(
                    f"Le client {client.user.get_full_name() or client.user.username} a passé une commande "
                    f"pour votre modèle '{modele.titre}'.\n\n"
                    f"Détails:\n"
                    f"- Taille: {commande.taille or 'Non spécifiée'}\n"
                    f"- Couleurs: {commande.couleurs or 'Non spécifiées'}\n"
                    f"- Livraison prévue: {commande.date_livraison_prevue or 'Non spécifiée'}\n\n"
                    f"Description additionnelle: {description_supp}\n\n"
                    f"Vous pouvez gérer cette commande depuis votre tableau de bord."
                )
            )

            messages.success(request, f"Commande créée avec succès ! Le couturier {modele.couturier.user.get_full_name()} a été notifié.")
            return redirect('mes_commandes_client')
    else:
        date_livraison_default = timezone.now().date() + timedelta(days=7)
        form = CommandeModeleForm(initial={
            'date_livraison_prevue': date_livraison_default
        })

    return render(request, 'BabiCouture/commande/creer_modele.html', {
        'form': form,
        'modele': modele,
        'client': client
    })


@login_required
def creer_commande_custom(request):
    """Créer une commande personnalisée (sans modèle)"""
    client = get_object_or_404(Client, user=request.user)
    couturiers = Couturier.objects.annotate(
        note_calculee=Avg('evaluations__note'),
        nb_evaluations=Count('evaluations')
    ).filter(note_calculee__isnull=False).order_by('-note_calculee')

    if request.method == 'POST':
        form = CommandePersonnaliseeForm(request.POST, request.FILES)

        if form.is_valid():
            couturier = form.cleaned_data['couturier']
            titre = form.cleaned_data['titre']
            description = form.cleaned_data['description']

            commande = Commande.objects.create(
                client=client,
                couturier=couturier,
                titre=titre,
                description=description,
                preferences=form.cleaned_data.get('preferences', ''),
                taille=form.cleaned_data.get('taille', ''),
                couleurs=form.cleaned_data.get('couleurs', ''),
                prix_propose=form.cleaned_data.get('prix_propose', 0),
                date_livraison_prevue=form.cleaned_data.get('date_livraison_prevue'),
                statut='en_attente'
            )

            mesures_text = form.cleaned_data.get('mesures', '')
            if mesures_text:
                try:
                    mesures_dict = json.loads(mesures_text) if mesures_text.strip().startswith('{') else {"texte": mesures_text}
                    commande.mesures_client = mesures_dict
                    commande.save()
                except json.JSONDecodeError:
                    commande.mesures_client = {"texte": mesures_text}
                    commande.save()

            if 'images_reference' in request.FILES:
                commande.images_reference = request.FILES['images_reference'].name
                commande.save()

            Message.objects.create(
                expediteur=request.user,
                destinataire=couturier.user,
                sujet=f"Nouvelle commande personnalisée: {titre}",
                contenu=(
                    f"Le client {client.user.get_full_name() or client.user.username} a passé une commande personnalisée.\n\n"
                    f"Titre: {titre}\nDescription: {description}\n\n"
                    f"Détails:\n"
                    f"- Prix proposé: {commande.prix_propose or 'À négocier'}\n"
                    f"- Taille: {commande.taille or 'Non spécifiée'}\n"
                    f"- Couleurs: {commande.couleurs or 'Non spécifiées'}\n"
                    f"- Livraison prévue: {commande.date_livraison_prevue or 'Non spécifiée'}\n\n"
                    f"Préférences: {commande.preferences or 'Aucune préférence spécifique'}\n\n"
                    f"Vous pouvez gérer cette commande depuis votre tableau de bord."
                )
            )

            messages.success(request, f"Commande personnalisée '{titre}' créée avec succès ! Le couturier {couturier.user.get_full_name()} a été notifié.")
            return redirect('mes_commandes_client')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        date_livraison_default = timezone.now().date() + timedelta(days=10)
        form = CommandePersonnaliseeForm(initial={
            'date_livraison_prevue': date_livraison_default
        })

    return render(request, 'BabiCouture/creer_custom.html', {
        'form': form,
        'couturiers': couturiers,
        'client': client
    })


@login_required
def creer_commande_couturier(request, couturier_id):
    """Créer une commande avec un couturier spécifique"""
    couturier = get_object_or_404(Couturier, id=couturier_id)
    client = get_object_or_404(Client, user=request.user)

    if request.method == 'POST':
        form = CommandePersonnaliseeForm(request.POST)
        if form.is_valid():
            commande = Commande.objects.create(
                client=client,
                couturier=couturier,
                titre=form.cleaned_data['titre'],
                description=form.cleaned_data['description'],
                preferences=form.cleaned_data.get('preferences', ''),
                taille=form.cleaned_data.get('taille', ''),
                couleurs=form.cleaned_data.get('couleurs', ''),
                prix_propose=form.cleaned_data.get('prix_propose', 0),
                date_livraison_prevue=form.cleaned_data.get('date_livraison_prevue'),
                statut='en_attente'
            )

            mesures_text = form.cleaned_data.get('mesures', '')
            if mesures_text:
                try:
                    mesures_dict = json.loads(mesures_text) if mesures_text.strip().startswith('{') else {"texte": mesures_text}
                    commande.mesures_client = mesures_dict
                    commande.save()
                except json.JSONDecodeError:
                    commande.mesures_client = {"texte": mesures_text}
                    commande.save()

            Message.objects.create(
                expediteur=request.user,
                destinataire=couturier.user,
                sujet="Nouvelle commande personnalisée",
                contenu=(
                    f"Le client {client.user.get_full_name() or client.user.username} a passé une commande.\n\n"
                    f"Titre: {commande.titre}\nDescription: {commande.description}\n\n"
                    f"Détails:\n"
                    f"- Prix proposé: {commande.prix_propose or 'À négocier'}\n"
                    f"- Taille: {commande.taille or 'Non spécifiée'}\n"
                    f"- Livraison prévue: {commande.date_livraison_prevue or 'Non spécifiée'}"
                )
            )

            messages.success(request, f"Commande créée avec succès pour le couturier {couturier.user.get_full_name()} !")
            return redirect('mes_commandes_client')
    else:
        date_livraison_default = timezone.now().date() + timedelta(days=10)
        form = CommandePersonnaliseeForm(initial={
            'couturier': couturier,
            'date_livraison_prevue': date_livraison_default
        })

    return render(request, 'BabiCouture/commande/creer_couturier.html', {
        'form': form,
        'couturier': couturier,
        'client': client
    })


@login_required
def mes_commandes_client(request):
    """Voir toutes les commandes du client"""
    client = get_object_or_404(Client, user=request.user)

    commandes = Commande.objects.filter(client=client).select_related(
        'couturier', 'couturier__user', 'modele'
    ).order_by('-date_commande')

    statut = request.GET.get('statut')
    if statut:
        commandes = commandes.filter(statut=statut)

    search_query = request.GET.get('search', '')
    if search_query:
        commandes = commandes.filter(
            Q(titre__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(couturier__user__username__icontains=search_query)
        )

    page = int(request.GET.get('page', 1))
    per_page = 10
    total_commandes = commandes.count()
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    commandes_page = commandes[start_idx:end_idx]

    stats = {
        'total': total_commandes,
        'en_attente': commandes.filter(statut='en_attente').count(),
        'en_cours': commandes.filter(statut='en_cours').count(),
        'confirmee': commandes.filter(statut='confirmee').count(),
        'livree': commandes.filter(statut='livree').count(),
        'terminee': commandes.filter(statut='terminee').count(),
        'annulee': commandes.filter(statut='annulee').count(),
    }

    context = {
        'client': client,
        'commandes': commandes_page,
        'stats': stats,
        'search_query': search_query,
        'statut_filtre': statut,
        'page': page,
        'total_pages': (total_commandes + per_page - 1) // per_page,
    }
    return render(request, 'BabiCouture/mes_commandes.html', context)


@login_required
def commandes_couturier(request):
    """Voir toutes les commandes reçues par le couturier"""
    couturier = get_object_or_404(Couturier, user=request.user)

    commandes = Commande.objects.filter(couturier=couturier).select_related(
        'client', 'client__user', 'modele'
    ).order_by('-date_commande')

    statut = request.GET.get('statut')
    if statut:
        commandes = commandes.filter(statut=statut)

    search_query = request.GET.get('search', '')
    if search_query:
        commandes = commandes.filter(
            Q(titre__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(client__user__username__icontains=search_query)
        )

    page = int(request.GET.get('page', 1))
    per_page = 15
    total_commandes = commandes.count()
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    commandes_page = commandes[start_idx:end_idx]

    stats = {
        'total': total_commandes,
        'en_attente': commandes.filter(statut='en_attente').count(),
        'en_cours': commandes.filter(statut='en_cours').count(),
        'confirmee': commandes.filter(statut='confirmee').count(),
        'livree': commandes.filter(statut='livree').count(),
        'terminee': commandes.filter(statut='terminee').count(),
        'annulee': commandes.filter(statut='annulee').count(),
    }

    revenus_totaux = Commande.objects.filter(
        couturier=couturier,
        statut='terminee'
    ).aggregate(total=Sum('prix_final'))['total'] or 0

    context = {
        'couturier': couturier,
        'commandes': commandes_page,
        'stats': stats,
        'revenus_totaux': revenus_totaux,
        'search_query': search_query,
        'statut_filtre': statut,
        'page': page,
        'total_pages': (total_commandes + per_page - 1) // per_page,
    }
    return render(request, 'BabiCouture/commandes.html', context)


@login_required
def details_commande(request, commande_id):
    """Voir les détails d'une commande spécifique"""
    commande = get_object_or_404(Commande.objects.select_related(
        'client', 'client__user', 'couturier', 'couturier__user', 'modele'
    ), id=commande_id)

    user = request.user
    if not (user == commande.client.user or user == commande.couturier.user):
        messages.error(request, "Vous n'avez pas accès à cette commande.")
        return redirect('home')

    messages_commande = Message.objects.filter(
        Q(expediteur=commande.client.user, destinataire=commande.couturier.user) |
        Q(expediteur=commande.couturier.user, destinataire=commande.client.user)
    ).filter(
        Q(sujet__icontains=f"#{commande.id}") | Q(sujet__icontains=commande.titre)
    ).order_by('date_envoi')[:10]

    context = {
        'commande': commande,
        'is_client': user == commande.client.user,
        'is_couturier': user == commande.couturier.user,
        'messages_commande': messages_commande,
    }
    return render(request, 'BabiCouture/commande/details.html', context)


@login_required
def modifier_statut_commande(request, commande_id):
    """Modifier le statut d'une commande (pour couturier)"""
    commande = get_object_or_404(Commande, id=commande_id)
    couturier = get_object_or_404(Couturier, user=request.user)

    if commande.couturier != couturier:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette commande.")
        return redirect('commandes_couturier')

    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        prix_final = request.POST.get('prix_final', '').strip()
        commentaire = request.POST.get('commentaire', '').strip()

        if nouveau_statut not in dict(Commande.STATUT_CHOICES).keys():
            messages.error(request, "Statut invalide.")
            return redirect('modifier_statut_commande', commande_id=commande_id)

        ancien_statut = commande.statut
        commande.statut = nouveau_statut

        if prix_final:
            try:
                commande.prix_final = float(prix_final)
            except ValueError:
                messages.error(request, "Prix invalide.")
                return redirect('modifier_statut_commande', commande_id=commande_id)

        if nouveau_statut == 'livree' and ancien_statut != 'livree':
            commande.date_livraison_reelle = timezone.now().date()

        commande.save()

        Message.objects.create(
            expediteur=request.user,
            destinataire=commande.client.user,
            sujet=f"Mise à jour commande #{commande.id}: {commande.get_statut_display()}",
            contenu=(
                f"Le statut de votre commande #{commande.id} '{commande.titre}' a été mis à jour:\n\n"
                f"- Ancien statut: {commande.get_statut_display_for(ancien_statut)}\n"
                f"- Nouveau statut: {commande.get_statut_display()}\n"
                f"- Prix final: {commande.prix_final} FCFA\n\n"
                f"Commentaire du couturier: {commentaire or 'Aucun commentaire'}"
            )
        )

        messages.success(request, f"Statut de la commande #{commande.id} mis à jour avec succès.")
        return redirect('details_commande', commande_id=commande_id)

    context = {
        'commande': commande,
        'statuts': Commande.STATUT_CHOICES
    }
    return render(request, 'BabiCouture/commande/modifier_statut.html', context)


@login_required
def annuler_commande(request, commande_id):
    """Annuler une commande (pour client)"""
    commande = get_object_or_404(Commande, id=commande_id)
    client = get_object_or_404(Client, user=request.user)

    if commande.client != client:
        messages.error(request, "Vous n'êtes pas autorisé à annuler cette commande.")
        return redirect('mes_commandes_client')

    if commande.statut not in ['en_attente', 'confirmee']:
        messages.error(request, "Cette commande ne peut plus être annulée car elle est déjà en cours de traitement.")
        return redirect('mes_commandes_client')

    if request.method == 'POST':
        raison = request.POST.get('raison', '').strip()
        if not raison:
            messages.error(request, "Veuillez indiquer une raison pour l'annulation.")
            return render(request, 'BabiCouture/commande/annuler.html', {'commande': commande})

        ancien_statut = commande.statut
        commande.statut = 'annulee'
        commande.raison_annulation = raison
        commande.save()

        Message.objects.create(
            expediteur=request.user,
            destinataire=commande.couturier.user,
            sujet=f"Commande #{commande.id} annulée par le client",
            contenu=(
                f"La commande #{commande.id} '{commande.titre}' a été annulée par le client "
                f"{client.user.get_full_name() or client.user.username}.\n\n"
                f"Raison: {raison}\n"
                f"Ancien statut: {commande.get_statut_display_for(ancien_statut)}\n"
                f"Date d'annulation: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
            )
        )

        messages.success(request, f"Commande #{commande.id} annulée avec succès.")
        return redirect('mes_commandes_client')

    return render(request, 'BabiCouture/commande/annuler.html', {'commande': commande})


@login_required
def confirmer_livraison(request, commande_id):
    """Confirmer la livraison et terminer la commande"""
    commande = get_object_or_404(Commande, id=commande_id)

    if request.user != commande.client.user:
        messages.error(request, "Vous ne pouvez pas confirmer cette livraison.")
        return redirect('mes_commandes_client')

    if commande.statut != 'livree':
        messages.error(request, "Cette commande n'est pas encore marquée comme livrée par le couturier.")
        return redirect('mes_commandes_client')

    if request.method == 'POST':
        commande.statut = 'terminee'
        commande.save()

        Message.objects.create(
            expediteur=request.user,
            destinataire=commande.couturier.user,
            sujet=f"Commande #{commande.id} confirmée et terminée",
            contenu=(
                f"Le client {commande.client.user.get_full_name() or commande.client.user.username} "
                f"a confirmé la réception et marqué la commande #{commande.id} comme terminée.\n\n"
                f"Vous pouvez maintenant être évalué par le client."
            )
        )

        messages.success(request, "Livraison confirmée ! La commande est maintenant terminée. Vous pouvez évaluer le couturier.")
        return redirect('evaluer_couturier', couturier_id=commande.couturier.id)

    return render(request, 'BabiCouture/commande/confirmer_livraison.html', {
        'commande': commande
    })