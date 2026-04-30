from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import json
from users.models import Client, Couturier
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['telephone', 'adresse', 'ville', 'code_postal', 'mesures_par_defaut']
        widgets = {
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: +221 77 123 45 67'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Votre adresse complète'
            }),
            'ville': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Dakar'
            }),
            'code_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 12345'
            }),
            'mesures_par_defaut': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Vos mesures par défaut (format JSON ou texte)'
            }),
        }
    
    def clean_mesures_par_defaut(self):
        mesures = self.cleaned_data.get('mesures_par_defaut')
        if mesures:
            try:
                # Essayer de parser comme JSON
                json.loads(mesures)
                return mesures
            except json.JSONDecodeError:
                # Sinon, convertir en JSON simple
                return json.dumps({"mesures": mesures})
        return "{}"

class CouturierForm(forms.ModelForm):
    class Meta:
        model = Couturier
        fields = ['telephone', 'adresse', 'ville', 'localisation', 'specialite', 
                 'description', 'experience', 'photo', 'disponible', 'delai_moyen_livraison']
        widgets = {
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: +221 77 123 45 67'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Votre adresse d\'atelier'
            }),
            'ville': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Dakar'
            }),
            'localisation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Plateau, Médina...'
            }),
            'specialite': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Robes de mariée, Costumes sur mesure...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez votre expertise et votre style...'
            }),
            'experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre d\'années d\'expérience'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control-file'
            }),
            'delai_moyen_livraison': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Délai moyen en jours'
            }),
        }
