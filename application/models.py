from django.db import models
from mongoengine import Document, StringField, IntField, BooleanField, DateTimeField, ListField, ReferenceField, FloatField

# Create your models here.
class Wallet(Document):
    meta = {
        'allow_inheritance': True
    }
    id = StringField(required=True, primary_key=True)
    account_number = StringField(required=True)
    balance = IntField(required=True)  # in cents

class Client(Wallet):
    username = StringField(required=True)
    card_number = StringField(required=True)
    security_hash = StringField(required=True)

class Merchant(Wallet):
    name = StringField(required=True)

class Intermediary(Wallet):
    pending_queue = ListField(IntField(), required=True)