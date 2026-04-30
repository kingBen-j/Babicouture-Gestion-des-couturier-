from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # home, static pages, dashboards
    path('users/', include('users.urls')),
    path('catalog/', include('catalog.urls')),
    path('orders/', include('orders.urls')),
    path('messaging/', include('messaging.urls')),
    path('reviews/', include('reviews.urls')),
]
