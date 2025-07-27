from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('items/', views.items, name='items'),
    path('reports/', views.reports, name='reports'),
    path('pos/', views.pos, name='pos'),
    path('receipt/<int:sale_id>/', views.receipt, name='receipt'),
    path('', include('django.contrib.auth.urls')),  # <-- Add this
]
