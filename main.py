from argparse import ArgumentParser
import logging
from erdpy.accounts import Account, Address
from erdpy.proxy import ElrondProxy
from erdpy.proxy.core import ElrondProxy
from erdpy.transactions import Transaction, BunchOfTransactions

import helper

def main():
    #python3 main.py --receiver=erd1yqv7q0khhrlxc8w0q8cv85ddlur8wdsu5q39kazpkhmyrdmnrzyqkkkqzg --sender=wallet2.pem
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

    # proxy = ElrondProxy("https://devnet-gateway.elrond.com")
    # network = proxy.get_network_config()
    # receiver = Address("erd1yqv7q0khhrlxc8w0q8cv85ddlur8wdsu5q39kazpkhmyrdmnrzyqkkkqzg")
    # # receiver = Address("erd1u64t98v0n4d8ayx6r9nmwrpzvxezyzyz5ewn80ulhhuj02x9ragqp6ffa2")
    # sender = Account(pem_file="wallet2.pem")
    # sender.sync_nonce(proxy=proxy)

    transactions: BunchOfTransactions = BunchOfTransactions()
    esdts = helper.get_esdt(sender.address,network.chain_id)
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
    
    #add new tx for the egld amount
    num, hashes = transactions.send(proxy)
    print(f"Sent {num} transactions:")
    print(hashes)

def test():
  proxy = ElrondProxy("https://devnet-gateway.elrond.com")
  network = proxy.get_network_config()
  receiver = Address("erd1u64t98v0n4d8ayx6r9nmwrpzvxezyzyz5ewn80ulhhuj02x9ragqp6ffa2")
  sender = Account(pem_file="wallet.pem")
  sender.sync_nonce(proxy=proxy)
  transaction = Transaction()
  transaction.chainID = network.chain_id
  transaction.nonce = sender.nonce
  transaction.version = network.min_tx_version
  transaction.gasPrice = network.min_gas_price
  transaction.value = "0"
  transaction.sender = sender.address.bech32()
  transaction.receiver = receiver.bech32()
  transaction.gasLimit = 500000
  #Ticker de la collection, puis id du nft, puis qty et enfin l'adresse du receiver
  transaction.data = "ESDTTransfer"\
        "@" + "AERO-ecf4e7".encode("utf-8").hex() +\
        "@" + hex(624280529419019210).replace("0x","0")
  transaction.sign(sender)
  print(transaction.send(proxy))

if __name__ == "__main__":
    main()