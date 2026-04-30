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

def login_view(request):
    if request.user.is_authenticated:
        # Vérifier le rôle de l'utilisateur connecté
        if Client.objects.filter(user=request.user).exists():
            return redirect('client_dashboard')
        elif Couturier.objects.filter(user=request.user).exists():
            return redirect('tailor_dashboard')
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            if role == 'client':
                if Client.objects.filter(user=user).exists():    
                    return redirect('client_dashboard')
                else:
                    messages.error(request, "Vous n'êtes pas inscrit en tant que client.")
                    logout(request)
            
            elif role == 'tailor':
                if Couturier.objects.filter(user=user).exists():
                    return redirect('tailor_dashboard')
                else:
                    messages.error(request, "Vous n'êtes pas inscrit en tant que couturier.")
                    logout(request)
            
            else:
                messages.error(request, "Veuillez sélectionner un rôle.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'BabiCouture/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def choose_role(request):
    """Permet à un utilisateur de choisir son rôle après inscription"""
    # Vérifier si l'utilisateur a déjà un rôle
    if Client.objects.filter(user=request.user).exists():
        return redirect('client_dashboard')
    elif Couturier.objects.filter(user=request.user).exists():
        return redirect('tailor_dashboard')
    
    if request.method == 'POST':
        role = request.POST.get('role')
        
        if role == 'client':
            Client.objects.create(user=request.user)
            messages.success(request, "Vous êtes maintenant inscrit en tant que client !")
            return redirect('client_dashboard')
        elif role == 'couturier':
            Couturier.objects.create(user=request.user)
            messages.success(request, "Vous êtes maintenant inscrit en tant que couturier !")
            return redirect('tailor_dashboard')
        else:
            messages.error(request, "Veuillez sélectionner un rôle valide.")
    
    return render(request, 'BabiCouture/choose_role.html')

def register_client(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        telephone = request.POST.get('telephone', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        nom = request.POST.get('nom', '').strip()
        
        # Validation
        if not all([username, email, password1, password2]):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return render(request, 'BabiCouture/register_client.html')
        
        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'BabiCouture/register_client.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return render(request, 'BabiCouture/register_client.html')
        
        if User.objects.filter(email=email).exists(): 
            
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'BabiCouture/register_client.html')
        
        try:
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username, 
                password=password1,
                email=email
            )
            user.first_name = prenom
            user.last_name = nom
            user.save()
            
            # Créer le client
            client = Client.objects.create(
                user=user,
                telephone=telephone,
                adresse=adresse
            )
            
            # Connecter l'utilisateur
            login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue sur Babi Couture.")
            return redirect('client_dashboard')
        except Exception as e:
            messages.error(request, f"Erreur lors de l'inscription: {str(e)}")
    
    return render(request, 'BabiCouture/register_client.html')

def register_couturier(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        nom_atelier = request.POST.get('nom_atelier')
        description = request.POST.get('description')
        telephone = request.POST.get('telephone')
        annees_experience = request.POST.get('annees_experience')
        tarif_horaire = request.POST.get('tarif_horaire', 0)
        adresse = request.POST.get('adresse')
        ville = request.POST.get('ville')
        code_postal = request.POST.get('code_postal')
        
        # Validation de base
        if not all([username, email, password1, password2, nom_atelier, description, telephone]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return render(request, 'BabiCouture/register_couturier.html')
        
        if password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'BabiCouture/register_couturier.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
            return render(request, 'BabiCouture/register_couturier.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
            return render(request, 'BabiCouture/register_couturier.html')
        
        try:
            # 1. Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=request.POST.get('prenom', ''),
                last_name=request.POST.get('nom', '')
            )
            
            # 2. Convertir l'expérience en nombre
            experience_value = 0
            if annees_experience == '0-2':
                experience_value = 1
            elif annees_experience == '3-5':
                experience_value = 4
            elif annees_experience == '6-10':
                experience_value = 8
            elif annees_experience == '10+':
                experience_value = 12
            
            # 3. Gérer les spécialités
            specialites_list = request.POST.getlist('specialites')
            autres_specialites = request.POST.get('autres_specialites', '')
            
            specialite_finale = ''
            if specialites_list:
                specialite_finale = ', '.join(specialites_list)
            if autres_specialites:
                if specialite_finale:
                    specialite_finale += f', {autres_specialites}'
                else:
                    specialite_finale = autres_specialites
            
            # 4. Construire la localisation
            localisation_parts = []
            if ville:
                localisation_parts.append(ville)
            if code_postal:
                localisation_parts.append(code_postal)
            if adresse:
                localisation_parts.append(adresse)
            localisation = ', '.join(localisation_parts) if localisation_parts else ''
            
            # 5. Créer le profil couturier
            couturier = Couturier.objects.create(
                user=user,
                nom_atelier=nom_atelier,
                telephone=telephone,
                adresse=adresse or '',
                ville=ville or '',
                localisation=localisation,
                specialite=specialite_finale,
                description=description,
                experience=experience_value,
            )
            
            # 6. Gérer le logo/photo
            if 'logo' in request.FILES:
                couturier.photo = request.FILES['logo']
                couturier.save()
            
           # 7. Connecter l'utilisateur
            user = authenticate(username=username, password=password1)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {nom_atelier} ! Votre compte a été créé avec succès.')
                # 8. REDIRECTION VERS LE DASHBOARD
                return redirect('tailor_dashboard')
            else:
                messages.error(request, 'Erreur lors de la connexion automatique.')
                return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création du compte : {str(e)}')
            return render(request, 'BabiCouture/register_couturier.html')
    
    # GET request - afficher le formulaire
    return render(request, 'BabiCouture/register_couturier.html')

@login_required
def profil_client(request):
    """Modifier le profil client"""
    client = get_object_or_404(Client, user=request.user)
    
    if request.method == 'POST':
        # Validation
        email = request.POST.get('email', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        nom = request.POST.get('nom', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        
        if not email:
            messages.error(request, "L'email est obligatoire.")
            return render(request, 'BabiCouture/profil/client.html', {'client': client})
        
        # Vérifier si l'email est déjà utilisé par un autre utilisateur
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, "Cet email est déjà utilisé par un autre compte.")
            return render(request, 'BabiCouture/profil/client.html', {'client': client})
        
        # Mettre à jour les informations utilisateur
        user = request.user
        user.email = email
        user.first_name = prenom
        user.last_name = nom
        user.save()
        
        # Mettre à jour les informations client
        client.telephone = telephone
        client.adresse = adresse
        client.save()
        
        messages.success(request, "Profil mis à jour avec succès !")
        return redirect('profil_client')
    
    context = {
        'client': client
    }
    return render(request, 'BabiCouture/profil/client.html', context)

@login_required
def profil_couturier(request):
    """Modifier le profil couturier"""
    couturier = get_object_or_404(Couturier, user=request.user)
    
    if request.method == 'POST':
        # Validation
        email = request.POST.get('email', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        nom = request.POST.get('nom', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        specialite = request.POST.get('specialite', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not all([email, telephone, specialite]):
            messages.error(request, "Veuillez remplir tous les champs obligatoires (email, téléphone, spécialité).")
            return render(request, 'BabiCouture/profil/couturier.html', {'couturier': couturier})
        
        # Vérifier si l'email est déjà utilisé par un autre utilisateur
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, "Cet email est déjà utilisé par un autre compte.")
            return render(request, 'BabiCouture/profil/couturier.html', {'couturier': couturier})
        
        # Mettre à jour les informations utilisateur
        user = request.user
        user.email = email
        user.first_name = prenom
        user.last_name = nom
        user.save()
        
        # Mettre à jour les informations couturier
        couturier.telephone = telephone
        couturier.adresse = adresse
        couturier.specialite = specialite
        couturier.description = description
        
        # Gérer l'image de profil
        if 'photo' in request.FILES:
            couturier.photo = request.FILES['photo']
        
        couturier.save()
        
        messages.success(request, "Profil mis à jour avec succès !")
        return redirect('profil_couturier')
    
    context = {
        'couturier': couturier
    }
    return render(request, 'BabiCouture/profil/couturier.html', context)
