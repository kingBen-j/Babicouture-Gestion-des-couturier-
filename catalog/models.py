from django.db import models
from django.utils import timezone


class Modele(models.Model):
    TYPE_CHOICES = [
        ('robe', 'Robe'),
        ('chemise', 'Chemise'),
        ('pantalon', 'Pantalon'),
        ('costume', 'Costume'),
        ('jupe', 'Jupe'),
        ('veste', 'Veste'),
        ('blouse', 'Blouse'),
        ('autre', 'Autre'),
    ]

    NIVEAU_CHOICES = [
        ('facile', 'Facile'),
        ('moyen', 'Moyen'),
        ('difficile', 'Difficile'),
    ]

    couturier = models.ForeignKey(
        'users.Couturier',
        on_delete=models.CASCADE,
        related_name='modeles'
    )
    titre = models.CharField(max_length=100)
    description = models.TextField()
    type_modele = models.CharField(max_length=50, choices=TYPE_CHOICES, default='autre')
    niveau_difficulte = models.CharField(max_length=50, choices=NIVEAU_CHOICES, default='moyen')
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to='modeles/',
        blank=True,
        null=True,
        help_text="Format accepté: JPG, PNG, GIF. Taille max: 5MB"
    )

    visible = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    disponible = models.BooleanField(default=True)
    temps_realisation = models.IntegerField(default=7)
    materiau_recommandé = models.CharField(max_length=100, blank=True, null=True)
    couleurs_disponibles = models.JSONField(default=list, blank=True, null=True)
    vues = models.IntegerField(default=0)
    commandes_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Modèle"
        verbose_name_plural = "Modèles"
        ordering = ['-created_at']

    def __str__(self):
        return self.titre

    def incrementer_vues(self):
        self.vues += 1
        self.save()
