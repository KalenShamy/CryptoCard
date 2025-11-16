from Crypto.Cipher import AES
from dotenv import load_dotenv
import os
from application.models import Wallet
import mongoengine as me
import csv
keys_path = "../keys.csv"

load_dotenv()

db_name = os.getenv("MONGODB_NAME")
db_host = os.getenv("MONGODB_URI")

me.connect(db_name, host=db_host)

def decrypt(ciphertext, nonce,tag):
    key = str(os.getenv("AES_KEY"))

    cipher = AES.new(key.encode("utf-8"), AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)

    #verify
    cipher.verify(tag)
    return plaintext


def encrypt(plaintext):
    key = str(os.getenv("AES_KEY"))

    plaintext = plaintext.encode("utf-8")
    cipher = AES.new(key.encode("utf-8"), AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    return(ciphertext, nonce, tag)


def add_wallet_to_db(id, private_key, public_key,nonce,tag):
    wallet = Wallet(id=id,private_key =private_key, public_key=public_key, encryption_nonce=nonce, encryption_tag=tag)
    wallet.save()






