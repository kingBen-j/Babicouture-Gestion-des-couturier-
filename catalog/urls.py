from django.urls import path
from . import views

urlpatterns = [
    path('mes-modeles/', views.mes_modeles, name='mes_modeles'),
    path('modele/creer/', views.creer_modele, name='creer_modele'),
    path('modele/modifier/<int:modele_id>/', views.modifier_modele, name='modifier_modele'),
    path('modele/supprimer/<int:modele_id>/', views.supprimer_modele, name='supprimer_modele'),
    path('boutique/', views.boutique, name='boutique'),
    path('modele/<int:modele_id>/', views.details_modele, name='details_modele'),
    path('couturiers/', views.liste_couturiers, name='liste_couturiers'),
    path('couturier/<int:couturier_id>/', views.details_couturier, name='details_couturier'),
    path('recherche/', views.recherche, name='recherche'),
]
