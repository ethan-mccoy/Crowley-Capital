#TODO: Create a browser extension or similar to scry (scrape) volume data
#TODO: Incorporate polls
#TODO: Incorporate news

import requests
import json
import sqlite3
from datetime import datetime

"""
Hail the magical Scrying Orb! 

The Orb retrieves, parses and saves data from the PredictIt API

"""
class ScryingOrb:

    """ Initialize the Orb  """
    def __init__(self):
        self.url = "https://www.predictit.org/api/marketdata/all/"
        self.db_path = 'markets.db'

    """ Use the Eye of Ra to see all 𓂀 """
    def get_markets(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            markets = self.parse_markets(response.json())
            self.save_to_db(markets)
            print("The Eye of Ra sees all 𓂀")
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
        return markets

    """  """
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
        
    