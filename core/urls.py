from django.urls import path
from . import views

urlpatterns = [
    path('loader/', views.loader, name='loader'),
    path('', views.home, name='home'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('couturier/dashboard/', views.tailor_dashboard, name='tailor_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/utilisateurs/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('admin/statistiques/', views.statistiques_detaillees, name='statistiques_detaillees'),
    path('admin/toggle-user/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    path('contact/', views.contact, name='contact'),
    path('a-propos/', views.a_propos, name='a_propos'),
    path('faq/', views.faq, name='faq'),
    path('conditions-utilisation/', views.conditions_utilisation, name='conditions_utilisation'),
    path('politique-confidentialite/', views.politique_confidentialite, name='politique_confidentialite'),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/stats-dashboard/', views.get_stats_dashboard, name='get_stats_dashboard'),
    path('test/', views.test_page, name='test_page'),
    path('clear-messages/', views.clear_messages, name='clear_messages'),
    path('login_view/', views.login_view_redirect, name='login_view'),
]
