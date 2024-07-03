from flask import Flask, render_template, jsonify
import sqlite3
import altair as alt
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from ScryingOrb import ScryingOrb

app = Flask(__name__)

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('markets.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    markets = query_db('SELECT DISTINCT market_id, name FROM Market')
    return render_template('index.html', markets=markets)

@app.route('/market/<market_id>')
def market_detail(market_id):
    market = query_db('SELECT * FROM Market WHERE market_id = ? ORDER BY timestamp DESC', [market_id], one=True)
    contracts = query_db('SELECT * FROM Contract WHERE market_id = ? ORDER BY timestamp DESC', [market_id])
    
    # Chart
    chart_data = pd.DataFrame(contracts)
    chart_data.columns = ['id', 'contract_id', 'market_id', 'name', 'short_name', 'status', 'last_trade_price', 'best_buy_yes_cost', 'best_buy_no_cost', 'best_sell_yes_cost', 'best_sell_no_cost', 'last_close_price', 'display_order', 'timestamp']
    chart_data = chart_data.dropna()
    chart_data = chart_data[chart_data['last_trade_price'] > 0.03]
    
    latest_contracts = chart_data.loc[chart_data.groupby('contract_id')['timestamp'].idxmax()]

    chart = alt.Chart(chart_data).mark_line().encode(
        x='timestamp:T',
        y='last_trade_price:Q',
        color='name:N'
    ).properties(
        width=600,
        height=400
    )
    chart_json = chart.to_json()
    
    return render_template('market_detail.html', market=market, contracts=contracts, latest_contracts=latest_contracts, chart_json=chart_json)

if __name__ == '__main__':
    orb = ScryingOrb()

    # Scheduler to update data every minute
    scheduler = BackgroundScheduler()
    scheduler.add_job(orb.get_markets, 'interval', minutes=1)
    scheduler.start()

    app.run(debug=True)