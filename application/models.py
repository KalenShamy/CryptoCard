from mongoengine import Document, StringField, IntField, BooleanField, DateTimeField, ListField, ReferenceField, FloatField

# Create your models here.
class Wallet(Document):
    meta = {
        'allow_inheritance': True
    }
    id = StringField(required=True, primary_key=True)
    private_key = StringField(required=True)
    public_key = StringField(required=True)

class Mesh(Wallet):
    pass

class Account(Wallet):
    meta = {
        'allow_inheritance': True
    },
    username = StringField(required=True)
    password_hash = StringField(required=True)

class Client(Account):
    username = StringField(required=True)

class Merchant(Account):
    name = StringField(required=True)
    balance = IntField(required=True, default=0) # 