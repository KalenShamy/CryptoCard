from mongoengine import Document, StringField, IntField, BooleanField, DateTimeField, ListField, ReferenceField, FloatField, BinaryField

# Create your models here.
class Wallet(Document):
    meta = {
        'allow_inheritance': True
    }
    id = StringField(required=True, primary_key=True)
    private_key = BinaryField(required=True)
    public_key = StringField(required=True)
    encryption_nonce = BinaryField(required=True)
    encryption_tag = BinaryField(required=True)

class Mesh(Wallet):
    pass

class Account(Document):
    meta = {
        'allow_inheritance': True
    }

class Client(Account):
    card_number = IntField(required=True)

class Merchant(Account):
    account_number = IntField(required=True)