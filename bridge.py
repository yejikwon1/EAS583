from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware #Necessary for POA chains
from datetime import datetime
import json
import pandas as pd

#test

def connect_to(chain):
    if chain == 'source':  # The source contract chain is avax
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'destination':  # The destination contract chain is bsc
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['source','destination']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_contract_info(chain, contract_info):
    """
        Load the contract_info file into a dictionary
        This function is used by the autograder and will likely be useful to you
    """
    try:
        with open(contract_info, 'r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( f"Failed to read contract info\nPlease contact your instructor\n{e}" )
        return 0
    return contracts[chain]


def scan_blocks(chain, contract_info="contract_info.json"):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    # This is different from Bridge IV where chain was "avax" or "bsc"
    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return 0
    
        #YOUR CODE HERE
    w3=connect_to(chain)
    other_chain='destination' if chain=='source' else 'source'
    other_w3=connect_to(other_chain)

    with open(contract_info, 'r') as f:
        info=json.load(f)

    this_contract_info=info[chain]
    other_contract_info=info[other_chain]
    warden=Web3.to_checksum_address(info['warden'])
    warden_privkey=info['warden_privkey']

    this_contract=w3.eth.contract(
        address=Web3.to_checksum_address(this_contract_info["address"]),
        abi=this_contract_info["abi"]
    )
    other_contract=other_w3.eth.contract(
        address=Web3.to_checksum_address(other_contract_info["address"]),
        abi=other_contract_info["abi"]

    )


    latest=w3.eth.block_number
    from_block=max(0,latest-5)
    to_block=latest

    if chain=='source':
        events=this_contract.events.Deposit().get_logs(fromBlock=from_block,toBlock=to_block)
    else:
        events=this_contract.events.Unwrap().get_logs(fromBlock=from_block,toBlock=to_block)

    
    for evt in events:
        args=evt['args']

        if chain=='source':
            token=args['token']
            recipient=args['recipient']
            amount=args['amount']
            func=other_contract.functions.wrap(token,recipient, amount)
        else:
            token=args['underlying_token']
            recipient=args['to']
            amount=args['amount']
            func=other_contract.functions.withdraw(token,recipient,amount)

            tx=func.build_transaction({
                'from':warden,
                'nonce': other_w3.eth.get_transaction_count(warden),
                'gas':500000,
                'gasPrice': other_w3.to_wei('10','gwei'),
                'chainId':other_w3.eth.chain_id

            })
            signed=other_w3.eth.account.sign_transaction(tx,private_key=warden_privkey)
            tx_hash=other_w3.eth.send_raw_transaction(signed.rawTransaction)

