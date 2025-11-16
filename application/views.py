from django.http import JsonResponse
from django.shortcuts import render
import json
from asgiref.sync import async_to_sync

from PaymentHandler.TokenAccountHandler import get_account_balance

from .models import *

# Create your views here.
#" /add/merchant"
#" /add/customer"
def add_account(request, acct_type):
    if request.method != "POST":
        return JsonResponse({"error": request.method + " not allowed here"}, status=400)
    
    if acct_type == "customer":
        card_number = request.POST.get("card_number")
        if request.session['cards'] != None:
            request.session['cards'].append(card_number)
        else:
            request.session['cards'] = [card_number]
        request.session.modified = True
        return JsonResponse({"status": "success"}, status=200)
    else: # merchant
        account_number = request.POST.get("account_number")
        if request.session['merchants'] != None:
            request.session['merchants'].append(account_number)
        else:
            request.session['merchants'] = [account_number]
        request.session.modified = True
        return JsonResponse({"status": "success"}, status=200)


async def merchant_index(request):
    merchants = request.session.get('merchants', [])
    merchants_data = []

    for merchant in merchants:
        data = Merchant.objects(account_number=merchant).first()
        merchants_data.append({
            "account_number": data.account_number,
            "balance": async_to_sync(get_account_balance)(data.public_key),
            "public_key": data.public_key,
            "private_key": data.private_key,
        })
    return render(request, 'merchant.jekyll', {"accts": merchants_data})

def customer_index(request):
    cards = request.session.get('cards', [])
    cards_data = [{
        "index": 0,
        "card_number": "0000 0000 0000 0000",
        "balance": 10.67,
        "public_key": "publicklicklickKEYYY",
    },
    {
        "index": 1,
        "card_number": "6700 0000 0000 0000",
        "balance": 67.67,
        "public_key": "publicklicklickKEYYY",
    }]

    for card in cards:
        data = Client.objects(card_number=card).first()
        cards_data.append({
            "index": cards_data.length,
            "card_number": data.card_number,
            "balance": async_to_sync(get_account_balance)(data.public_key),
            "public_key": data.public_key,
            "private_key": data.private_key,
        })

    return render(request, 'index.jekyll', {"cards": cards_data})

def card_control(request):
    return 200, json.dumps({})

def fraud(request):
    return 200, json.dumps({
        "fraud_alerts": [
            {"date": "2025-01-15",
                "location": "france",
                "amount": 1000000
            }
        ]
    })

def transaction_history(request):
    return 200, json.dumps({
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