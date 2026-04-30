from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import json
from users.models import Couturier
from orders.models import Commande


class CommandeModeleForm(forms.Form):
    """Formulaire pour commander un modèle existant"""

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent',
            'placeholder': 'Ajoutez des détails spécifiques pour votre commande...',
            'rows': 4
        })
    )

    mesures = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent',
            'placeholder': 'Vos mesures personnelles:\n• Taille: ...\n• Tour de poitrine: ...\n• Tour de taille: ...\n• Tour de hanches: ...',
            'rows': 5
        })
    )

    taille = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent',
            'placeholder': 'Ex: M, 38, 1.70m'
        })
    )

    couleurs = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent',
            'placeholder': 'Ex: Bleu roi, Or, Blanc'
        })
    )

    preferences = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent',
            'placeholder': 'Préférences particulières (tissu, style, accessoires...)',
            'rows': 3
        })
    )

    date_livraison_prevue = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent',
            'type': 'date'
        })
    )

    prix_propose = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent',
            'placeholder': 'Prix proposé (facultatif)'
        })
    )


class CommandePersonnaliseeForm(forms.Form):
    """Formulaire pour une commande personnalisée"""

    couturier = forms.ModelChoiceField(
        queryset=Couturier.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent'
        }),
        required=True
    )

    titre = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent',
            'placeholder': 'Ex: Costume de mariage sur mesure'
        }),
        required=True
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent',
            'placeholder': 'Décrivez en détail ce que vous souhaitez...',
            'rows': 5
        }),
        required=True
    )

    type_article = forms.ChoiceField(
        choices=[
            ('robe', 'Robe'),
            ('chemise', 'Chemise'),
            ('pantalon', 'Pantalon'),
            ('costume', 'Costume'),
            ('jupe', 'Jupe'),
            ('veste', 'Veste'),
            ('blouse', 'Blouse'),
            ('autre', 'Autre'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent'
        }),
        required=True
    )

    mesures = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent',
            'placeholder': 'Vos mesures détaillées...',
            'rows': 5
        })
    )

    taille = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent',
            'placeholder': 'Taille générale'
        })
    )

    couleurs = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent',
            'placeholder': 'Couleurs souhaitées'
        })
    )

    preferences = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent',
            'placeholder': 'Préférences (tissu, style, détails...)',
            'rows': 3
        })
    )

    prix_propose = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent',
            'placeholder': 'Budget estimé (facultatif)'
        })
    )

    date_livraison_prevue = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent',
            'type': 'date'
        })
    )

    photos_reference = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent'
        })
    )


class CommandeAdminForm(forms.ModelForm):
    """Formulaire pour administrer une commande (couturier/admin)"""

    class Meta:
        model = Commande
        fields = ['statut', 'prix_final', 'date_livraison_prevue', 'date_livraison_reelle',
                  'acompte', 'mode_paiement', 'paiement_effectue', 'notes_internes',
                  'priorite', 'photos_couturier']

        widgets = {
            'statut': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prix_final': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '100'
            }),
            'date_livraison_prevue': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_livraison_reelle': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'acompte': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '100'
            }),
            'mode_paiement': forms.Select(attrs={
                'class': 'form-control'
            }),
            'paiement_effectue': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes_internes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'priorite': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5
            }),
            'photos_couturier': forms.FileInput(attrs={
                'class': 'form-control-file'
            }),
        }