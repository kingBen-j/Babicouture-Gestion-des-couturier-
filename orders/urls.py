from django.urls import path
from . import views

urlpatterns = [
    path('passer/<int:modele_id>/', views.passer_commande, name='passer_commande'),
    path('creer/<int:modele_id>/', views.creer_commande, name='creer_commande'),
    path('custom/', views.creer_commande_custom, name='creer_commande_custom'),
    path('couturier/<int:couturier_id>/', views.creer_commande_couturier, name='creer_commande_couturier'),
    path('mes-commandes/', views.mes_commandes_client, name='mes_commandes_client'),
    path('couturier/', views.commandes_couturier, name='commandes_couturier'),
    path('<int:commande_id>/', views.details_commande, name='details_commande'),
    path('modifier-statut/<int:commande_id>/', views.modifier_statut_commande, name='modifier_statut_commande'),
    path('annuler/<int:commande_id>/', views.annuler_commande, name='annuler_commande'),
    path('confirmer-livraison/<int:commande_id>/', views.confirmer_livraison, name='confirmer_livraison'),
]
