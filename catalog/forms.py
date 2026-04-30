from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import json
from catalog.models import Modele
from users.models import Couturier
class ModeleForm(forms.ModelForm):
    class Meta:
        model = Modele
        fields = ['titre', 'description', 'type_modele', 'niveau_difficulte', 
                 'prix', 'image', 'temps_realisation', 'materiau_recommandé']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Robe de soirée élégante'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez votre modèle en détail...'
            }),
            'type_modele': forms.Select(attrs={
                'class': 'form-control'
            }),
            'niveau_difficulte': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '100',
                'placeholder': 'Prix en XOF'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control-file'
            }),
            'temps_realisation': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jours nécessaires'
            }),
            'materiau_recommandé': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Coton, Soie, Wax...'
            }),
        }

class RechercheCouturierForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom, spécialité, localisation...'
        })
    )
    
    specialite = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Spécialité'
        })
    )
    
    ville = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ville'
        })
    )
    
    note_min = forms.FloatField(
        required=False,
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Note minimum',
            'step': 0.5
        })
    )
    
    disponible = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    tri = forms.ChoiceField(
        choices=[
            ('note', 'Meilleures notes'),
            ('experience', 'Plus d\'expérience'),
            ('recent', 'Plus récents'),
        ],
        required=False,
        initial='note',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

class RechercheModeleForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Titre, description...'
        })
    )
    
    type_modele = forms.ChoiceField(
        choices=[('', 'Tous types')] + [
            ('robe', 'Robe'),
            ('chemise', 'Chemise'),
            ('pantalon', 'Pantalon'),
            ('costume', 'Costume'),
            ('jupe', 'Jupe'),
            ('veste', 'Veste'),
            ('blouse', 'Blouse'),
            ('autre', 'Autre'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    prix_min = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prix minimum',
            'step': '1000'
        })
    )
    
    prix_max = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prix maximum',
            'step': '1000'
        })
    )
    
    tri = forms.ChoiceField(
        choices=[
            ('recent', 'Plus récents'),
            ('prix_croissant', 'Prix croissant'),
            ('prix_decroissant', 'Prix décroissant'),
            ('popularite', 'Plus populaires'),
        ],
        required=False,
        initial='recent',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
