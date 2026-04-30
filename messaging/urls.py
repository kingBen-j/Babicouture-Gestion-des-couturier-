from django.urls import path
from . import views

urlpatterns = [
    path('envoyer/', views.envoyer_message, name='envoyer_message'),
    path('envoyer/<int:destinataire_id>/', views.envoyer_message_dest, name='envoyer_message_dest'),
    path('', views.boite_reception, name='boite_reception'),
    path('message/<int:message_id>/', views.lire_message, name='lire_message'),
    path('repondre/<int:message_id>/', views.repondre_message, name='repondre_message'),
    path('supprimer/<int:message_id>/', views.supprimer_message, name='supprimer_message'),
    path('api/marquer-message-lu/<int:message_id>/', views.marquer_message_lu, name='marquer_message_lu'),
]
