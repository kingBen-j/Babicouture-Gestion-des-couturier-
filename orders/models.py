from django.db import models
from django.utils import timezone


class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]

    MODE_PAIEMENT_CHOICES = [
        ('especes', 'Espèces'),
        ('mobile_money', 'Mobile Money'),
        ('carte', 'Carte bancaire'),
        ('virement', 'Virement bancaire'),
        ('autre', 'Autre'),
    ]

    client = models.ForeignKey(
        'users.Client',
        on_delete=models.CASCADE,
        related_name='commandes'
    )
    couturier = models.ForeignKey(
        'users.Couturier',
        on_delete=models.CASCADE,
        related_name='commandes_recues'
    )
    modele = models.ForeignKey(
        'catalog.Modele',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commandes'
    )

    titre = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    mesures_client = models.JSONField(default=dict, blank=True, null=True)
    taille = models.CharField(max_length=20, blank=True, null=True)
    couleurs = models.CharField(max_length=200, blank=True, null=True)
    preferences = models.TextField(blank=True, null=True)

    prix_propose = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    acompte = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mode_paiement = models.CharField(max_length=50, choices=MODE_PAIEMENT_CHOICES, blank=True, null=True)
    paiement_effectue = models.BooleanField(default=False)

    date_commande = models.DateTimeField(default=timezone.now)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_livraison_prevue = models.DateField(null=True, blank=True)
    date_livraison_reelle = models.DateField(null=True, blank=True)

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    priorite = models.IntegerField(default=1)
    notes_internes = models.TextField(blank=True, null=True)
    raison_annulation = models.TextField(blank=True, null=True)

    photos_client = models.JSONField(default=list, blank=True, null=True)
    photos_couturier = models.JSONField(default=list, blank=True, null=True)

    satisfait_client = models.BooleanField(null=True, blank=True)
    commentaire_final = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_commande']

    def __str__(self):
        if self.titre:
            return f"Commande #{self.id} - {self.titre}"
        elif self.modele:
            return f"Commande #{self.id} - {self.modele.titre}"
        else:
            return f"Commande #{self.id}"

    def calculer_prix_final(self):
        if self.modele and not self.prix_final:
            self.prix_final = self.modele.prix
            self.save()
        return self.prix_final

    def est_en_retard(self):
        if self.date_livraison_prevue and self.statut not in ['terminee', 'annulee']:
            return timezone.now().date() > self.date_livraison_prevue
        return False

    def duree_realisation(self):
        if self.date_debut and self.date_livraison_reelle:
            return (self.date_livraison_reelle - self.date_debut.date()).days
        return None
