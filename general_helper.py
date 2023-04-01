from dataclasses import dataclass
from typing import Dict, ClassVar
from web3 import Web3
import requests
import json
import time
from sdk_py.auction_calculator.auction_calculator import AuctionCalculator
import os

def contert_str_datetime_to_timestamp(str_datetime):
    return int(time.mktime(time.strptime(str_datetime, "%Y-%m-%dT%H:%M:%S.%fZ"))+3600-time.timezone)

def get_token_info(token_address):
    w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'))
    token_address = w3.toChecksumAddress(token_address)
    standart_abi = json.loads(open(os.getcwd()+"/"+"standart_abi.json", "r").read())
    token = w3.eth.contract(address=token_address, abi=standart_abi)
    decimals = int(token.functions.decimals().call())
    symbol = token.functions.symbol().call()
    name = token.functions.name().call()
    token = {"decimals": decimals, "symbol": symbol, "name": name, "address": token_address}
    return token, token_address
    
@dataclass
class Order:
    orderHash: str = ""
    makerAsset: str = ""
    makingAmount: int = 0
    amount: int = 0
    takerAsset: str = ""
    takingAmount: int = 0
    amountOut: int = 0
    deadline: int = ""
    salt: str = ""
    interactions: str = ""
    curr_takingAmount: int = 0
    updated: int = int(time.time()*1000)
    
    def read_order_from_json(self, json):
        order = Order(
            orderHash=json['orderHash'],
            makerAsset=json['order']['makerAsset'],
            makingAmount=int(json['order']['makingAmount']),
            takerAsset=json['order']['takerAsset'],
            takingAmount=int(json['order']['takingAmount']),
            deadline=contert_str_datetime_to_timestamp(json['deadline']),
            salt = json['order']['salt'],
            interactions = json['order']['interactions']
        )
        auction_calculator = AuctionCalculator.fromLimitOrderV3Struct(order.to_v3_format())
        rate = auction_calculator.calcRateBump(int(time.time()))
        order.curr_takingAmount = auction_calculator.calcAuctionTakingAmount(order.takingAmount, rate)
        return order

    def config_order(self, tokens):
        if not self.amount:
            self.amount = self.makingAmount/10**tokens.get_token(self.makerAsset).decimals
        if not self.curr_takingAmount:
            self.curr_takingAmount = self.takingAmount
        self.amountOut = self.curr_takingAmount/10**tokens.get_token(self.takerAsset).decimals
    
    def to_v3_format(self):
        return {
                "interactions": self.interactions,
                "salt": self.salt,
        }
    
    def update(self, tokens):
        auction_calculator = AuctionCalculator.fromLimitOrderV3Struct(self.to_v3_format())
        rate = auction_calculator.calcRateBump(int(time.time()))
        self.curr_takingAmount = auction_calculator.calcAuctionTakingAmount(self.takingAmount, rate)
        self.config_order(tokens)    
        self.updated = int(time.time()*1000)

    def update_as_partial_filled(self, json, tokens):
        self.makingAmount = int(json['order']['makingAmount'])
        self.takingAmount = int(json['order']['takingAmount'])
        for fill in json['fills']:
            self.makingAmount -= int(fill['filledMakerAmount'])
            self.takingAmount -= int(fill['filledAuctionTakerAmount'])
        if self.makingAmount < 0 or self.takingAmount < 0:
            self.makingAmount = 0.1
            self.takingAmount = 0.1
        
        auction_calculator = AuctionCalculator.fromLimitOrderV3Struct(self.to_v3_format())
        rate = auction_calculator.calcRateBump(int(time.time()))
        self.curr_takingAmount = auction_calculator.calcAuctionTakingAmount(self.takingAmount, rate)
        self.config_order(tokens) 
        self.updated = int(time.time()*1000)

    def check_order_profit(self, tokens, openocean_api):
        oo_deal = openocean_api.get_quote_from_token(self.makerAsset, self.takerAsset, self.amount, tokens)
        if oo_deal:
            if oo_deal > self.amountOut:
                profit_amount = oo_deal - self.amountOut
                profit_percent = profit_amount/self.amountOut*100
                prof_deal = ProfitableDeal(self.orderHash, self.amount, tokens.get_token(self.makerAsset).symbol, self.amountOut, tokens.get_token(self.takerAsset).symbol, oo_deal, profit_percent)
                return prof_deal
            else:
                return None
    def to_calc(self, tokens):
        return {
            "makerAsset": self.makerAsset,
            "makingAmount": self.makingAmount,
            "takerAsset": self.takerAsset,
            "takingAmount": self.takingAmount,
            "amount": self.amount,
            "amountOut": self.amountOut,
            "makerSymbol": tokens.get_token(self.makerAsset).symbol,
            "takerSymbol": tokens.get_token(self.takerAsset).symbol,
        }

    
@dataclass
class Orders:
    orders: ClassVar[Dict[str, int]] = {}
    
    def get_order(self, order_hash):
        return self.orders.get(order_hash, None)
    
    def add_order(self, order, tokens):
        if order.orderHash in self.orders:
            self.orders[order.orderHash].update(tokens)
        else:
            self.orders[order.orderHash] = order
        
    def delete_order(self, order_hash, deals, dbh):
        deals.delete_deal(order_hash, dbh)
        del self.orders[order_hash]
        
    def delete_expired_orders(self, deals, dbh):
        if len(self.orders) == 0:
            return
        orders_for_delete = []
        for order_hash, order in self.orders.items():
            if order.deadline < int(time.time()):
                orders_for_delete.append(order_hash)
                print("Order {} is expired".format(order_hash[-10:]))
        for order_hash in orders_for_delete:
                self.delete_order(order_hash, deals, dbh)
                
    def get_orders_list(self):
        return list(self.orders.keys())
    
    def update_order(self, order, tokens):
        self.orders[order.orderHash].update(tokens)


@dataclass
class ProfitableDeal:
    orderHash: str
    amountIn: float
    tokenIn: str
    amountOut: float
    tokenOut: str
    amountOutOO: float
    profitPercent: float

    def to_humanable(self, orders):
        order = orders.get_order(self.orderHash)
        return "OrderHash: {} {} {} => {} {}, OpenOcean amountOut: {}, Profit amount: {} Profit percent: {}".format(
            self.orderHash[-10:],
            self.amountIn,
            self.tokenIn,
            self.amountOut,
            self.tokenOut,
            self.amountOutOO,
            self.amountOutOO-self.amountOut,
            self.profitPercent,
        )

@dataclass
class ProfitableDeals:
    deals: ClassVar[Dict[str, int]] = {}

    def add_deal(self, deal, dbh):
        if deal.orderHash in self.deals:
            dbh.update_deal(deal)
            self.deals[deal.orderHash] = deal
        else:
            dbh.add_deal(deal)
            self.deals[deal.orderHash] = deal
            
    def delete_deal(self, order_hash, dbh):
        dbh.delete_deal(order_hash)
        if order_hash in self.deals:
            del self.deals[order_hash]
    
    def get_deal(self, order_hash):
        return self.deals.get(order_hash, None)
    
    def get_deals(self):
        return self.deals.values()
                
    def update(self, deal, dbh):
        self.deals[deal.orderHash] = deal
        dbh.update_deal(deal)

@dataclass
class Token:
    address: str
    symbol: str
    decimals: int
    name: str
    
@dataclass
class Tokens:
    tokens: ClassVar[Dict[str, int]] = {}

    def get_token(self, address):
        token = self.tokens.get(address, None)
        if token:
            return token
        else:
            token, address = get_token_info(address)
            token_obj = Token(**token)
            self.tokens[address] = token_obj
            return token_obj



