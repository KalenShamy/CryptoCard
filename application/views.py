from django.http import JsonResponse
from django.shortcuts import render
import json
from asgiref.sync import async_to_sync
from solders.pubkey import Pubkey
from PaymentHandler.TokenAccountHandler import get_account_balance, get_token_account_id

from .models import *

# Create your views here.
#" /add/merchant"
#" /add/customer"
def add_account(request, acct_type):
    if request.method != "POST":
        return JsonResponse({"error": request.method + " not allowed here"}, status=400)
    
    if acct_type == "customer":
        card_number = request.POST.get("card_number")
        if 'cards' in request.session:
            request.session['cards'] += [card_number]
        else:
            request.session['cards'] = [card_number]
        return JsonResponse({"status": "success"}, status=200)
    else: # merchant
        account_number = request.POST.get("account_number")
        if 'merchants' in request.session:
            request.session['merchants'] += [account_number]
        else:
            request.session['merchants'] = [account_number]
        return JsonResponse({"status": "success"}, status=200)


def merchant_index(request):
    merchants = request.session.get('merchants', [])
    merchants_data = []
    print(merchants)
    for merchant in merchants:
        data = Merchant.objects(account_number=merchant).first()
        payment_token_key = async_to_sync(get_token_account_id)(data.public_key)
        payment_wallet_balance = async_to_sync(get_account_balance)(payment_token_key)
        merchants_data.append({
            "index": len(merchants_data),
            "account_number": data.account_number,
            "balance": payment_wallet_balance,
            "public_key": data.public_key,
            "private_key": data.private_key,
        })
    print(merchants_data)
    return render(request, 'merchant.jekyll', {"accts": merchants_data})

def customer_index(request):
    cards = request.session.get('cards', [])
    cards_data = []

    for card in cards:
        data = Client.objects(card_number=card).first()
        payment_token_key = async_to_sync(get_token_account_id)(data.public_key)
        payment_wallet_balance = async_to_sync(get_account_balance)(payment_token_key)
        cards_data.append({
            "index": len(cards_data),
            "card_number": data.card_number,
            "balance": payment_wallet_balance,
            "public_key": data.public_key,
            "private_key": data.private_key,
        })
    print(cards_data)
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