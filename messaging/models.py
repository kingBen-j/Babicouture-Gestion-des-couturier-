from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Message(models.Model):
    TYPE_CHOICES = [
        ('general', 'Général'),
        ('commande', 'Commande'),
        ('question', 'Question'),
        ('urgence', 'Urgence'),
    ]

    expediteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages_envoyes'
    )
    destinataire = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages_recus'
    )
    type_message = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    sujet = models.CharField(max_length=200, default="Message")
    contenu = models.TextField()
    piece_jointe = models.FileField(upload_to='messages/pieces_jointes/', blank=True, null=True)

    lu = models.BooleanField(default=False)
    date_lu = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)

    reponse_a = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reponses'
    )

    date_envoi = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.expediteur.username} → {self.destinataire.username}: {self.sujet}"

    def marquer_comme_lu(self):
        if not self.lu:
            self.lu = True
            self.date_lu = timezone.now()
            self.save()


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    sujet = models.CharField(max_length=200, blank=True, null=True)
    type_conversation = models.CharField(max_length=50, default='general')

    commande = models.ForeignKey(
        'orders.Commande',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations'
    )

    dernier_message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dernier_message_conversation'
    )

    archive = models.BooleanField(default=False)
    notifications_activees = models.BooleanField(default=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ['-date_modification']

    def __str__(self):
        parts = list(self.participants.all()[:3])
        participants = ", ".join([p.username for p in parts])
        if self.participants.count() > 3:
            participants += "..."
        return f"Conversation: {participants}"

    def nombre_messages_non_lus(self, utilisateur):
        return self.message_set.filter(
            destinataire=utilisateur,
            lu=False
        ).count()
