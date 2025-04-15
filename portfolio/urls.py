from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('delete_stock/<int:stockId>/', views.delete_stock, name='delete_stock'),
    path('transactions', views.trasaction_view, name='transactions'),
    path("delete-transaction/<int:transaction_id>/", views.delete_transaction, name="delete_transaction"),
    path('add_trade/', views.add_trade, name='add_trade'),
]