from django.urls import path
from . import views

urlpatterns = [
    path('couturier/<int:couturier_id>/', views.evaluer_couturier, name='evaluer_couturier'),
    path('mes-evaluations/', views.mes_evaluations, name='mes_evaluations'),
    path('repondre/<int:evaluation_id>/', views.repondre_evaluation, name='repondre_evaluation'),
]
