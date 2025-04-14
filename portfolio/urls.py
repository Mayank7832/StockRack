from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('delete_stock/<int:stockId>/', views.delete_stock, name='delete_stock'),
    path('add_trade/', views.add_trade, name='add_trade'),
]