from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import json
from messaging.models import Message
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['destinataire', 'type_message', 'sujet', 'contenu', 'piece_jointe', 'important']
        widgets = {
            'destinataire': forms.Select(attrs={
                'class': 'form-control'
            }),
            'type_message': forms.Select(attrs={
                'class': 'form-control'
            }),
            'sujet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sujet du message'
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Votre message...'
            }),
            'piece_jointe': forms.FileInput(attrs={
                'class': 'form-control-file'
            }),
            'important': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class RepondreMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['contenu', 'piece_jointe']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Votre réponse...'
            }),
            'piece_jointe': forms.FileInput(attrs={
                'class': 'form-control-file'
            }),
        }
