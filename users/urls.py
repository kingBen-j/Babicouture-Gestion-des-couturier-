from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('choose-role/', views.choose_role, name='choose_role'),
    path('register/client/', views.register_client, name='register_client'),
    path('register/couturier/', views.register_couturier, name='register_couturier'),
    path('profil/client/', views.profil_client, name='profil_client'),
    path('profil/couturier/', views.profil_couturier, name='profil_couturier'),
]
