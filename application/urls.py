from django.urls import path
from . import views

urlpatterns = [
    path('customer', views.customer_index, name='customer_index'),
    path('merchant', views.merchant_index, name='merchant_index'),
    path('add/<str:acct_type>', views.add_account, name='add_account'),
    
    path('card_control/', views.card_control, name='card_control'),
    path('card_details/', views.card_details, name='card_details'),
    path('transaction_history/', views.transaction_history, name='transaction_history'),
    path('fraud/', views.fraud, name='fraud'),
]
