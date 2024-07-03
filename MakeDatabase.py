import sqlite3

def init_db():
    conn = sqlite3.connect('markets.db')
    c = conn.cursor()
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS Market (
        id INTEGER PRIMARY KEY,
        market_id TEXT,
        name TEXT,
        short_name TEXT,
        image TEXT,
        url TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS Contract (
        id INTEGER PRIMARY KEY,
        contract_id TEXT,
        market_id TEXT,
        name TEXT,
        short_name TEXT,
        status TEXT,
        last_trade_price REAL,
        best_buy_yes_cost REAL,
        best_buy_no_cost REAL,
        best_sell_yes_cost REAL,
        best_sell_no_cost REAL,
        last_close_price REAL,
        display_order INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (market_id) REFERENCES Market (market_id)
    )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()