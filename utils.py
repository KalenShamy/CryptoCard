from Crypto.Cipher import AES
from dotenv import load_dotenv
import os

def decrypt(nonce, ciphertext,tag):
    load_dotenv()
    key = str(os.getenv("AES_KEY"))

    cipher = AES.new(key.encode("utf-8"), AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)

    #verify
    cipher.verify(tag)
    return plaintext


def encrypt(plaintext):
    load_dotenv()
    key = str(os.getenv("AES_KEY"))

    cipher = AES.new(key.encode("utf-8"), AES.MODE_EAX)
    nonce = str(cipher.nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    return(ciphertext, nonce, tag)






