from django.db import models


class Evaluation(models.Model):
    couturier = models.ForeignKey(
        'users.Couturier',
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    client = models.ForeignKey(
        'users.Client',
        on_delete=models.CASCADE,
        related_name='evaluations_donnees'
    )
    commande = models.ForeignKey(
        'orders.Commande',
        on_delete=models.CASCADE,
        related_name='evaluations',
        null=True,
        blank=True
    )

    note = models.FloatField()
    commentaire = models.TextField(blank=True, null=True)

    qualite_travail = models.IntegerField(default=0)
    respect_delais = models.IntegerField(default=0)
    communication = models.IntegerField(default=0)
    rapport_qualite_prix = models.IntegerField(default=0)

    photos = models.JSONField(default=list, blank=True, null=True)

    visible = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
        ordering = ['-date_creation']
        unique_together = ['couturier', 'client', 'commande']

    def __str__(self):
        return f"Évaluation {self.note}/5 - {self.couturier.user.username}"

    def note_moyenne_details(self):
        notes = [
            self.qualite_travail,
            self.respect_delais,
            self.communication,
            self.rapport_qualite_prix
        ]
        notes_valides = [n for n in notes if n > 0]
        if notes_valides:
            return sum(notes_valides) / len(notes_valides)
        return self.note
