from django.shortcuts import render

from .models import *

# Create your views here.
def index(request):
    return render(request, 'index.jekyll', {
                    "cards": [
                        {id: 1},
                        {id: 2}]
                })

def card_control(request):
    return render(request, 'button_templates/card_control.jekyll', {
                })

def fraud(request):
    return render(request, 'button_templates/fraud.jekyll', {
                    "fraud_alerts": [
                        {"date": "2025-01-15",
                         "location": "france",
                         "amount": 1000000
                        }
                    ]
                })

def transaction_history(request):
    return render(request, 'button_templates/transaction_history.jekyll', {
        "history": [
            {
                "retailer": "Costco",
                "date": "2025-01-15",
                "amount": 125.99
            },
            {
                "retailer": "Walmart",
                "date": "2025-01-12",
                "amount": 48.20
            }
                    ]
                })

def card_details(request):
    return render(request, 'button_templates/card_details.jekyll', {
        "public_key": "publicklicklickKEYYY",
        "private_key": "privatttteeeee"
                })