from argparse import ArgumentParser
import logging
from erdpy.accounts import Account, Address
from erdpy.proxy import ElrondProxy
from erdpy.proxy.core import ElrondProxy
from erdpy.transactions import Transaction, BunchOfTransactions

import helper

def main():
    #python3 main.py --receiver=erd1snukhz9375qdjejsryxm3lqlh5r0hm7dvrez6cmqt08rznsf5h0sn290k5 --sender=wallet3.pem --proxy=mainnet
    logging.basicConfig(level=logging.ERROR)
    parser = ArgumentParser()
    parser.add_argument("--receiver", help="receiver address", required=True)
    parser.add_argument("--sender", help="sender pem", required=True)
    parser.add_argument("--proxy", help="mainnet, default is devnet")
    args = parser.parse_args()

    if (args.proxy=="mainnet"):
      proxy = ElrondProxy("https://gateway.elrond.com")
    else :
      proxy = ElrondProxy("https://devnet-gateway.elrond.com")
    network = proxy.get_network_config()
    
    receiver = Address(args.receiver)
    sender = Account(pem_file=args.sender)
    sender.sync_nonce(proxy=proxy)

    transactions: BunchOfTransactions = BunchOfTransactions()
    esdts = helper.get_esdt(sender.address,network.chain_id)
    at_least_one = False
    hashes = []
    for ticker in esdts:
      transaction = Transaction()
      transaction.chainID = network.chain_id
      transaction.nonce = sender.nonce
      transaction.version = network.min_tx_version
      transaction.gasPrice = network.min_gas_price
      transaction.value = "0"
      transaction.sender = sender.address.bech32()
      transaction.gasLimit = 500000
      dash_occurences = ticker.count("-")
      quantity = esdts[ticker]["balance"]
      if dash_occurences==2: #NFT/SFT
        split = ticker.split("-")
        collection = split[0]+"-"+split[1]
        id = split[2]
        transaction = helper.set_esdt_nft_transfer(transaction,receiver,sender.address,collection,id,quantity)
      else : #esdt
        transaction = helper.set_esdt_transfer(transaction,receiver,ticker,quantity)
      transaction.sign(sender)
      
      sender.nonce+=1
      transactions.add_prepared(transaction)
      at_least_one = True

    if at_least_one: 
      _, hashes = transactions.send(proxy)
      print(f"Sent {len(hashes)} esdt transactions:\n{hashes}")
    
    #process new tx for the egld amount
    egld_amount = int(helper.get_egld_balance(sender.address,network.chain_id))
    keep_for_gas = 50000000000000000 #keep 0.05 egld for the gas
    hashes_two = []
    if egld_amount>keep_for_gas:
      transaction = Transaction()
      transaction.chainID = network.chain_id
      transaction.nonce = sender.nonce
      transaction.version = network.min_tx_version
      transaction.gasPrice = 500000000
      transaction.value = str(egld_amount-keep_for_gas)
      transaction.sender = sender.address.bech32()
      transaction.receiver=receiver.bech32()
      transaction.gasLimit = 50000
      transaction.sign(sender)
    
      hashes_two = transaction.send(proxy)
      print(f"Sent {len(hashes_two)} egld transactions:\n{hashes_two}")

    print("Main finished")


if __name__ == "__main__":
  while True:
    main()