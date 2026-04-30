from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import json
from reviews.models import Evaluation
class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['note', 'commentaire', 'qualite_travail', 'respect_delais', 
                 'communication', 'rapport_qualite_prix']
        
        widgets = {
            'note': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 5,
                'step': 0.5,
                'placeholder': 'Note globale (0-5)'
            }),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Votre avis détaillé...'
            }),
            'qualite_travail': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 5,
                'placeholder': 'Qualité du travail (0-5)'
            }),
            'respect_delais': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 5,
                'placeholder': 'Respect des délais (0-5)'
            }),
            'communication': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 5,
                'placeholder': 'Communication (0-5)'
            }),
            'rapport_qualite_prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 5,
                'placeholder': 'Rapport qualité/prix (0-5)'
            })
        }
