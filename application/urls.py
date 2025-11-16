from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    path('card_control/', views.card_control, name='card_control'),
    path('card_details/', views.card_details, name='card_details'),
    path('transaction_history/', views.transaction_history, name='transaction_history'),
    path('fraud/', views.fraud, name='fraud'),
]
