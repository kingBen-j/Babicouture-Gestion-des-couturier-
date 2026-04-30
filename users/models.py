from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Client(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='client_profile'
    )
    telephone = models.CharField(max_length=15, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    code_postal = models.CharField(max_length=10, blank=True, null=True)
    mesures_par_defaut = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"Client - {self.user.username}"


class Couturier(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='couturier_profile'
    )
    nom_atelier = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    localisation = models.CharField(max_length=255, blank=True, null=True)
    specialite = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    experience = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='couturiers/', blank=True, null=True)
    note_moyenne = models.FloatField(default=0.0)
    nombre_avis = models.IntegerField(default=0)
    disponible = models.BooleanField(default=True)
    delai_moyen_livraison = models.IntegerField(default=7)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Couturier"
        verbose_name_plural = "Couturiers"

    def __str__(self):
        return self.nom_atelier or f"Couturier - {self.user.username}"

    def calculer_note_moyenne(self):
        evaluations = self.evaluations.all()
        if evaluations.exists():
            moyenne = evaluations.aggregate(models.Avg('note'))['note__avg']
            self.note_moyenne = moyenne or 0.0
            self.nombre_avis = evaluations.count()
            self.save()
