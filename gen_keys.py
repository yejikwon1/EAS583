from web3 import Web3
from eth_account.messages import encode_defunct
import eth_account
import os

def get_keys (challenge, filename="secret_key.txt"):
    """
    challenge - byte string
    filename - filename of the file that contains your account secret key
    To pass the tests, your signature must verify, and the account you use
    must have testnet funds on both the bsc and avalanche test networks.
    """
    # This code will read your "sk.txt" file
    # If the file is empty, it will raise an exception
    with open(filename, "r") as f:
        key = f.readlines()
    assert(len(key) > 0), "Your account secret_key.txt is empty"

    private_key=key[0].strip()
    acct=eth_account.Account.from_key(private_key)
    eth_addr=acct.address
    message = encode_defunct(text=challenge.hex())

    #w3 = Web3()
    
    # TODO recover your account information for your private key and sign the given challenge
    # Use the code from the signatures assignment to sign the given challenge
    
    signed_message=acct.sign_message(message)
    recovered=eth_account.Account.recover_message(message,signed_message.signature)

    assert eth_account.Account.recover_message(message,signature=signed_message.signature.hex()) == eth_addr, f"Failed to sign message properly"

    #return signed_message, account associated with the private key
  #  return signed_message, eth_addr
    return {"address": eth_addr, "signature":signed_message.signature.hex()}

if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        result=get_keys(challenge)
        print(result )
