from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('delete_stock/<int:stockId>/', views.delete_stock, name='delete_stock'),
]