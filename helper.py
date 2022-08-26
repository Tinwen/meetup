from enum import Enum
from typing import Tuple
import requests
from erdpy.accounts import Address
from erdpy.transactions import Transaction

def get_esdt(address:Address,network:str) -> str :
    if network=="1":
      url ="https://gateway.elrond.com/address/"+address.bech32()+"/esdt"
    elif network=="D":
      url ="https://devnet-gateway.elrond.com/address/"+address.bech32()+"/esdt"
    elif network=="T":
      url ="https://testnet-gateway.elrond.com/address/"+address.bech32()+"/esdt"
    
    return requests.get(url).json()["data"]["esdts"]

def get_egld_balance(address:Address,network:str)->str:
  if network=="1":
      url_egld = "https://api.elrond.com/accounts/"+address.bech32()
  elif network=="D":
    url_egld = "https://devnet-api.elrond.com/accounts/"+address.bech32()
  elif network=="T":
    url_egld = "https://testnet-api.elrond.com/accounts/"+address.bech32()
  
  return requests.get(url_egld).json()["balance"]
def set_esdt_nft_transfer(transaction:Transaction,receiver:Address,sender:Address,collection:str, id_nft:str,quantity:str):
  #Ticker de la collection, puis id du nft, puis qty et enfin l'adresse du receiver
  transaction.receiver = sender.bech32()
  transaction.data = "ESDTNFTTransfer"\
          "@" + collection.encode("utf-8").hex() +\
          "@" + id_nft +\
          "@" + manage_quantity(quantity) +\
          "@" + receiver.hex()
  return transaction

def set_esdt_transfer(transaction:Transaction,receiver:Address,ticker:str, quantity:str):
  transaction.receiver = receiver.bech32()
  transaction.data = "ESDTTransfer"\
      "@" + ticker.encode("utf-8").hex() +\
      "@" + manage_quantity(quantity)
  return transaction

def manage_quantity(quantity:str)-> str:
  qty = hex(int(quantity)).replace("0x","")
  if len(qty)%2 != 0:
    qty = qty.zfill(len(qty)+1)
  return qty