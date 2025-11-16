import asyncio
from solana.rpc.async_api import AsyncClient, Transaction
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from spl.token.client import Token
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from spl.token.instructions import transfer_checked, TransferCheckedParams
from spl.token.constants import TOKEN_2022_PROGRAM_ID
import base58

def str_to_byte_array(privateKey: str):

    byte_array = []

    for i in privateKey:
        byte_array.append(ord(i.encode("utf-8")))

    return byte_array

async def get_account_balance(tokenAccountKey: Pubkey):

    rpc = AsyncClient("https://api.mainnet-beta.solana.com")

    # Use a real token account address from mainnet
    token_account_address = tokenAccountKey

    async with rpc:
        try:
            balance = await rpc.get_token_account_balance(token_account_address)
            return(int(balance.value.amount)/1000000)
        except Exception as e:
            print(f"Error getting token balance: {e}")
            print("This might be because the account doesn't exist or isn't a token account")

async def transfer(sender_private_key: str, recipient_pubkey_str: str, amount):

    rpc = AsyncClient("https://api.mainnet-beta.solana.com")

    sender = Keypair.from_bytes(base58.b58decode(sender_private_key))
    recipient_pubkey = Pubkey.from_string(recipient_pubkey_str)
    mint_address = Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo")

    # token_client = Token(AsyncClient, mint_address, TOKEN_2022_PROGRAM_ID, sender)

    # sender_token_account = get_associated_token_address(sender.pubkey(), mint_address, TOKEN_2022_PROGRAM_ID)
    # recipient_token_account = get_associated_token_address(recipient_pubkey, mint_address, TOKEN_2022_PROGRAM_ID)

    # tx_result = token_client.transfer(
    #     source=sender_token_account,
    #     dest=recipient_token_account,
    #     owner=sender,
    #     amount=amount
    # )

    # print(tx_result)
    
    async with rpc:    
        sender_token_account = get_associated_token_address(sender.pubkey(), mint_address, TOKEN_2022_PROGRAM_ID)
        recipient_token_account = get_associated_token_address(recipient_pubkey, mint_address, TOKEN_2022_PROGRAM_ID)

        # check if recipient ATA exists
        instructions = []
        account_info = await rpc.get_account_info(recipient_token_account)

        if account_info.value is None:
            # create the recipient's ATA if it doesn't exist
            create_ata_ix = create_associated_token_account(
                payer=sender.pubkey(),
                owner=recipient_pubkey,
                mint=mint_address,
                token_program_id=TOKEN_2022_PROGRAM_ID
            )
            instructions.append(create_ata_ix)

        transfer_instruction = transfer_checked(
                TransferCheckedParams (
                amount = amount,
                decimals = 6,
                dest = recipient_token_account,
                mint = mint_address,
                owner = sender.pubkey(),
                program_id = TOKEN_2022_PROGRAM_ID,
                source = sender_token_account
            )
        )
        instructions.append(transfer_instruction)

        recent_blockhash = await rpc.get_latest_blockhash()

        message = MessageV0.try_compile(
            payer=sender.pubkey(),
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=recent_blockhash.value.blockhash,
        )

        transaction = VersionedTransaction(message, [sender]) ###

        result = await rpc.send_transaction(transaction) # !!!
        print(f"Transaction signature: {result.value}")
    
async def transfer_with_fee_payer(
    sender_private_key: str, 
    fee_payer_private_key: str,
    recipient_pubkey_str: str, 
    amount: int
):

    rpc = AsyncClient("https://api.mainnet-beta.solana.com")
    
    sender = Keypair.from_bytes(base58.b58decode(sender_private_key))
    fee_payer = Keypair.from_bytes(base58.b58decode(fee_payer_private_key))  # New
    recipient_pubkey = Pubkey.from_string(recipient_pubkey_str)
    mint_address = Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo")
    
    async with rpc:    
        sender_token_account = get_associated_token_address(
            sender.pubkey(), mint_address, TOKEN_2022_PROGRAM_ID
        )
        recipient_token_account = get_associated_token_address(
            recipient_pubkey, mint_address, TOKEN_2022_PROGRAM_ID
        )

        instructions = []
        account_info = await rpc.get_account_info(recipient_token_account)

        if account_info.value is None:
            create_ata_ix = create_associated_token_account(
                payer=fee_payer.pubkey(),  # Fee payer pays for ATA creation
                owner=recipient_pubkey,
                mint=mint_address,
                token_program_id=TOKEN_2022_PROGRAM_ID
            )
            instructions.append(create_ata_ix)

        transfer_instruction = transfer_checked(
            TransferCheckedParams(
                amount=amount,
                decimals=6,
                dest=recipient_token_account,
                mint=mint_address,
                owner=sender.pubkey(),  # Sender still owns/controls the tokens
                program_id=TOKEN_2022_PROGRAM_ID,
                source=sender_token_account
            )
        )
        instructions.append(transfer_instruction)

        recent_blockhash = await rpc.get_latest_blockhash()

        message = MessageV0.try_compile(
            payer=fee_payer.pubkey(),  # Changed: fee payer covers transaction fees
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=recent_blockhash.value.blockhash,
        )

        # Both wallets must sign: fee_payer first, then sender
        transaction = VersionedTransaction(message, [fee_payer, sender])

        result = await rpc.send_transaction(transaction)
        print(f"Transaction signature: {result.value}")

async def get_token_account_id(account_pubkey: str):

    rpc = AsyncClient("https://api.mainnet-beta.solana.com")

    mint_address = Pubkey.from_string("2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo")

    async with rpc:
        return get_associated_token_address(Pubkey.from_string(account_pubkey), mint_address, TOKEN_2022_PROGRAM_ID)



# async def main():
#     await get_token_account_id(pubkey)
    # print(Keypair.from_bytes(base58.b58decode("V2Kbvzc2EjUVsb9Fb8EocB8Mt7eTRNX6VJ9qmbdQwHnYajb3Qjsa53hFaeUZsZVyTFVeXgkBPRpq4GAit7rTizg")).pubkey())
    # await get_account_balance(Pubkey.from_string(""))
    #await transfer("SENDER_PRIV_KEY", "RECIP_PUBKEY", 25_0000)
    
    #await transfer_with_fee_payer("FEE_PAYER_PRIV_KEY",
    #               "SENDER_PRIV_KEY",
    #                "RECIP_PUBKEY", 25_0000)

# if __name__ == "__main__":
#     asyncio.run(main())