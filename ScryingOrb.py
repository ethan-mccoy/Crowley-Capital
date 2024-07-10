#TODO: Create a browser extension or similar to scry (scrape) volume data
#TODO: Incorporate polls
#TODO: Incorporate news

import requests
import json
import sqlite3
from datetime import datetime
from CarrierPigeon import CarrierPigeon

"""
Hail the magical Scrying Orb! 

The Orb retrieves, parses and saves data from the PredictIt API

also it checks if any of the buy or sell yes pricing data passes set threshold

"""
class ScryingOrb:
    """ Initialize the Orb  """
    def __init__(self):
        self.url = "https://www.predictit.org/api/marketdata/all/"
        self.db_path = 'markets.db'
        self.pigeon = CarrierPigeon()
        self.thresholds = {}

    """ adds a price threshold to a contract """
    def set_price(self, market_id, contract_id, threshold_type, price):
        if market_id not in self.thresholds:
            self.thresholds[market_id] = {}
        if contract_id not in self.thresholds[market_id]:
            self.thresholds[market_id][contract_id] = {'buy': [], 'sell': []}

        if threshold_type == 'buy':
            self.thresholds[market_id][contract_id]['buy'].append(price)
        elif threshold_type == 'sell':
            self.thresholds[market_id][contract_id]['sell'].append(price)

        print(f"Threshold set for market {market_id}, contract {contract_id}, type {threshold_type}, price {price}")

    # TODO: make id to market dict and remove for loop
    """ checks latest prices for contracts with thresholds set """
    def check_price(self):
        for market in self.latest_markets:
            market_id = market['ID']
            if market_id in self.thresholds:
                for contract in market['Contracts']:
                    contract_id = contract['ID']
                    if contract_id in self.thresholds[market_id]:
                        buy_prices = self.thresholds[market_id][contract_id]['buy']
                        sell_prices = self.thresholds[market_id][contract_id]['sell']
                        current_buy_price = contract['BestBuyYesCost']
                        current_sell_price = contract['BestSellYesCost']

                        if any(current_buy_price <= threshold for threshold in buy_prices):
                            self.pigeon.send(f"Buy threshold met for market {market_id}, contract {contract_id} at price {current_buy_price}")

                        if any(current_sell_price >= threshold for threshold in sell_prices):
                            self.pigeon.send(f"Sell threshold met for market {market_id}, contract {contract_id} at price {current_sell_price}")

    """ Use the Eye of Ra to see all 𓂀 """
    def get_markets(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            print("The Eye of Ra sees all 𓂀")
            markets = self.parse_markets(response.json())
            self.save_to_db(markets)
        else:
            print("The Eye of Ra sees nothing :(")
            response.raise_for_status()

    """ Contemplate on the Visions of Ra """
    def parse_markets(self, json_data):
        markets = []
        for market in json_data['markets']:
            market_info = {
                'ID': market['id'],
                'Name': market['name'],
                'ShortName': market['shortName'],
                'Image': market['image'],
                'URL': market['url'],
                'Contracts': []
            }
            for contract in market['contracts']:
                contract_info = {
                    'ID': contract['id'],
                    'Name': contract['name'],
                    'ShortName': contract['shortName'],
                    'Status': contract['status'],
                    'LastTradePrice': contract['lastTradePrice'],
                    'BestBuyYesCost': contract['bestBuyYesCost'],
                    'BestBuyNoCost': contract['bestBuyNoCost'],
                    'BestSellYesCost': contract['bestSellYesCost'],
                    'BestSellNoCost': contract['bestSellNoCost'],
                    'LastClosePrice': contract['lastClosePrice'],
                    'DisplayOrder': contract['displayOrder']
                }
                market_info['Contracts'].append(contract_info)
            markets.append(market_info)
        print("The Eye of Ra parses all 𓂀")
        self.latest_markets = markets
        return markets

    """ saves market info to sqlite3 db """
    def save_to_db(self, markets):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        for market in markets:
            c.execute('''
            INSERT INTO Market (market_id, name, short_name, image, url, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (market['ID'], market['Name'], market['ShortName'], market['Image'], market['URL'], timestamp))
            
            for contract in market['Contracts']:
                c.execute('''
                INSERT INTO Contract (contract_id, market_id, name, short_name, status, last_trade_price, best_buy_yes_cost, best_buy_no_cost, best_sell_yes_cost, best_sell_no_cost, last_close_price, display_order, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (contract['ID'], market['ID'], contract['Name'], contract['ShortName'], contract['Status'], contract['LastTradePrice'], contract['BestBuyYesCost'], contract['BestBuyNoCost'], contract['BestSellYesCost'], contract['BestSellNoCost'], contract['LastClosePrice'], contract['DisplayOrder'], timestamp))
        
        conn.commit()
        conn.close()
        
    