import random
import time
from PaymentHandler.TokenAccountHandler import transfer, get_account_balance, get_token_account_id, transfer_with_fee_payer
import asyncio
import os
from application.models import Wallet
from utils import decrypt

minimum_balance = 0.1
min_wait_time = 0.25
max_wait_time = 0.5

db_name = os.getenv("MONGODB_NAME")
db_host = os.getenv("MONGODB_URI")

def tumble(mesh):
    balance_cache = {}
    #get a random non zero subset of mesh to send to and from
    sending_wallets = random.sample(mesh, random.randint(1, len(mesh)))
    reveiving_wallets = random.sample(mesh, random.randint(1, len(mesh)))
    


    for send_wallet in sending_wallets:
        for receive_wallet in reveiving_wallets:
            if send_wallet == receive_wallet:
                continue
            #TODO update transfer to use keys not just wallet placeholders
            print(send_wallet.id, receive_wallet.id)
            #ensure enough to send
            
            if send_wallet.id not in balance_cache:
                token_key = asyncio.run(get_token_account_id(send_wallet.public_key))
                balance = asyncio.run( get_account_balance(token_key))
                balance_cache[send_wallet.id] = balance
            else:
                balance = balance_cache[send_wallet.id]

            if balance <= minimum_balance:
                print("no balance")
                continue
            print(balance)
            amount = random.randint(0,  int((balance- minimum_balance) * 1_000_000))
            #wait
            time.sleep(random.uniform(min_wait_time, max_wait_time))
            #asyncio.run(transfer(send_wallet, receive_wallet, random.uniform(0,  balance- minimum_balance)))
            send_wallet_key = decrypt(send_wallet.private_key, send_wallet.encryption_nonce, send_wallet.encryption_tag)
            receive_wallet_key = receive_wallet.public_key
            fee_payer_private_key = decrypt(Wallet.objects(id="1").first().private_key, Wallet.objects(id="1").first().encryption_nonce, Wallet.objects(id="1").first().encryption_tag)
            asyncio.run(transfer_with_fee_payer(send_wallet_key, fee_payer_private_key,receive_wallet_key, amount))
            #asyncio.run(transfer(send_wallet_key, receive_wallet_key, 150000))

            balance_cache[send_wallet.id] -= amount / 1_000_000
            time.sleep(15)
            

async def process_mesh(mesh):
    total_liquidity = 0
    new_mesh = []

    for wallet in mesh:
        token_key = await get_token_account_id(wallet.public_key)
        balance = await get_account_balance(token_key)

        # Convert balance to base units for consistent comparison
        balance_base_units = int(balance * 1_000_000)
        
        if balance_base_units > minimum_balance:
            new_mesh.append(wallet)
            total_liquidity += (balance_base_units - minimum_balance)

    return new_mesh, total_liquidity  

def pay(start, end, mesh, amount):
    mesh.remove(start)
    mesh, total_liquidity = asyncio.run(process_mesh(mesh))
    print(f"total_liquidity {total_liquidity} base units")
            
    receive_wallet_key = end.public_key
    if len(mesh) == 0:
        raise ValueError("No wallet above minimum balance")
    
    # total_liquidity is already in base units, no need to multiply
    if total_liquidity < amount:
        raise ValueError(f"The network does not have the liquidity for this payment request, only {total_liquidity} liquid")
    
    total_paid = 0
    while total_paid < amount:
        time.sleep(0.15)
        payment_wallet = random.choice(mesh)
        payment_token_key = asyncio.run(get_token_account_id(payment_wallet.public_key))
        payment_wallet_balance = asyncio.run(get_account_balance(payment_token_key))
        
        # Convert to base units immediately
        payment_wallet_balance_base = int(payment_wallet_balance * 1_000_000)
        
        payment_wallet_key = decrypt(payment_wallet.private_key, payment_wallet.encryption_nonce, payment_wallet.encryption_tag)

        print(f"{payment_wallet.id} has {payment_wallet_balance_base} base units")
        
        # Calculate how much we still need to pay
        remaining = amount - total_paid
        available_tokens = payment_wallet_balance_base - minimum_balance
        max_possible = min(available_tokens, remaining)
        low = min(available_tokens / 3, max_possible)

        payment_tokens = random.uniform(low, max_possible)
        
        # payment is now in base units
        payment = int(payment_tokens)

        fee_payer_private_key = decrypt(
            Wallet.objects(id="1").first().private_key, 
            Wallet.objects(id="1").first().encryption_nonce, 
            Wallet.objects(id="1").first().encryption_tag
        )
        
        print(f"{payment_wallet.id} is paying {end.id} {payment} base units")
        asyncio.run(transfer_with_fee_payer(payment_wallet_key, fee_payer_private_key, receive_wallet_key, payment))
        print("paid")
        
        total_paid += payment
        print(f"Total paid {total_paid}, {amount - total_paid} still left to pay")

        # Check if wallet should be removed
        if payment_wallet_balance_base - payment <= minimum_balance:
            mesh.remove(payment_wallet)


def send_full(sender_id, recipient_id, amount):

    start = Wallet.objects(id=sender_id).first()
    end = Wallet.objects(id=recipient_id).first()

    send_wallet_key = decrypt(start.private_key, start.encryption_nonce, start.encryption_tag)
    

    mesh = Wallet.objects(id__in=["2", "3", "4","5","6","7","8","9","10"])
    hold = random.choice(mesh)

    fee_payer_private_key = decrypt(Wallet.objects(id="1").first().private_key, Wallet.objects(id="1").first().encryption_nonce, Wallet.objects(id="1").first().encryption_tag)
    asyncio.run(transfer_with_fee_payer(send_wallet_key, fee_payer_private_key, hold.public_key, amount))

    pay(hold, end, mesh, amount)


def send_one_to_one(sender_id, recipient_id, amount):

    start = Wallet.objects(id=sender_id).first()
    end = Wallet.objects(id=recipient_id).first()

    send_wallet_key = decrypt(start.private_key, start.encryption_nonce, start.encryption_tag)
    print(send_wallet_key)

    fee_payer_private_key = decrypt(Wallet.objects(id="2").first().private_key, Wallet.objects(id="2").first().encryption_nonce, Wallet.objects(id="2").first().encryption_tag)
    print(fee_payer_private_key)

    print(end.public_key)
    asyncio.run(transfer_with_fee_payer(send_wallet_key, fee_payer_private_key, end.public_key, amount))
    
async def diagnose_transfer_accounts(sender_id, recipient_id):
    """Diagnose which account is missing"""
    from solana.rpc.async_api import AsyncClient
    from solders.pubkey import Pubkey
    from solders.keypair import Keypair
    from spl.token.instructions import get_associated_token_address
    
    # REPLACE WITH YOUR ACTUAL TOKEN MINT
    RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"
    TOKEN_MINT = Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo")  # ← REPLACE THIS
    
    rpc = AsyncClient(RPC_ENDPOINT)
    
    # Get wallets
    sender = Wallet.objects(id=sender_id).first()
    recipient = Wallet.objects(id=recipient_id).first()
    fee_payer = Wallet.objects(id="1").first()
    
    # Decrypt keys and decode bytes to string
    sender_key_bytes = decrypt(sender.private_key, sender.encryption_nonce, sender.encryption_tag)
    fee_payer_key_bytes = decrypt(fee_payer.private_key, fee_payer.encryption_nonce, fee_payer.encryption_tag)
    
    # Convert bytes to string
    sender_key = sender_key_bytes.decode('utf-8') if isinstance(sender_key_bytes, bytes) else sender_key_bytes
    fee_payer_key = fee_payer_key_bytes.decode('utf-8') if isinstance(fee_payer_key_bytes, bytes) else fee_payer_key_bytes
    
    sender_keypair = Keypair.from_base58_string(sender_key)
    recipient_pubkey = Pubkey.from_string(recipient.public_key)
    fee_payer_keypair = Keypair.from_base58_string(fee_payer_key)
    
    print("\n=== ACCOUNT DIAGNOSIS ===\n")
    
    # Check 1: Sender wallet
    print(f"1. Sender wallet ({sender_id}): {sender_keypair.pubkey()}")
    sender_wallet_info = await rpc.get_account_info(sender_keypair.pubkey())
    print(f"   Exists: {sender_wallet_info.value is not None}")
    if sender_wallet_info.value:
        print(f"   Has SOL: {sender_wallet_info.value.lamports / 1e9} SOL")
    
    # Check 2: Sender token account
    sender_ata = get_associated_token_address(sender_keypair.pubkey(), TOKEN_MINT)
    print(f"\n2. Sender TOKEN account: {sender_ata}")
    sender_token_info = await rpc.get_account_info(sender_ata)
    print(f"   Exists: {sender_token_info.value is not None}")
    if sender_token_info.value:
        try:
            balance = await rpc.get_token_account_balance(sender_ata)
            print(f"   Token balance: {balance.value.ui_amount}")
        except:
            print(f"   Could not get balance")
    else:
        print(f"   ❌ MISSING! This is likely your problem!")
    
    # Check 3: Recipient wallet
    print(f"\n3. Recipient wallet ({recipient_id}): {recipient_pubkey}")
    recipient_wallet_info = await rpc.get_account_info(recipient_pubkey)
    print(f"   Exists: {recipient_wallet_info.value is not None}")
    
    # Check 4: Recipient token account
    recipient_ata = get_associated_token_address(recipient_pubkey, TOKEN_MINT)
    print(f"\n4. Recipient TOKEN account: {recipient_ata}")
    recipient_token_info = await rpc.get_account_info(recipient_ata)
    print(f"   Exists: {recipient_token_info.value is not None}")
    if not recipient_token_info.value:
        print(f"   ❌ MISSING! This is likely your problem!")
    
    # Check 5: Fee payer wallet
    print(f"\n5. Fee payer wallet (1): {fee_payer_keypair.pubkey()}")
    fee_payer_wallet_info = await rpc.get_account_info(fee_payer_keypair.pubkey())
    print(f"   Exists: {fee_payer_wallet_info.value is not None}")
    if fee_payer_wallet_info.value:
        print(f"   Has SOL: {fee_payer_wallet_info.value.lamports / 1e9} SOL")
    else:
        print(f"   ❌ MISSING! Fee payer doesn't exist!")
    
    # Check 6: Token mint
    print(f"\n6. Token mint: {TOKEN_MINT}")
    mint_info = await rpc.get_account_info(TOKEN_MINT)
    print(f"   Exists: {mint_info.value is not None}")
    if not mint_info.value:
        print(f"   ❌ MISSING! Token mint doesn't exist!")
    
    await rpc.close()
    
    print("\n=== END DIAGNOSIS ===\n")

