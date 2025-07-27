from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('items/', views.items, name='items'),
    path('reports/', views.reports, name='reports'),  # Only if you create reports view
    path('pos/', views.pos, name='pos'),
    path('receipt/<int:sale_id>/', views.receipt, name='receipt'),
]