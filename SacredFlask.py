from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import altair as alt
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from ScryingOrb import ScryingOrb
from CarrierPigeon import CarrierPigeon

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
    one_day_contracts = query_db('SELECT * FROM Contract WHERE market_id = ? AND timestamp >= date("now", "-1 day") ORDER BY timestamp DESC', [market_id])
    print(market_id)

    # text notifications
    pidgey = CarrierPigeon()
    #pidgey.send_text("Test")

    
    # Chart
    # TODO: Make seperate chart handler class
    chart_data = pd.DataFrame(one_day_contracts)
    print(chart_data.columns)
    chart_data.columns = ['id', 'contract_id', 'market_id', 'name', 'short_name', 'status', 'last_trade_price', 'best_buy_yes_cost', 'best_buy_no_cost', 'best_sell_yes_cost', 'best_sell_no_cost', 'last_close_price', 'display_order', 'timestamp']
    chart_data = chart_data.dropna()
    chart_data = chart_data[chart_data['last_trade_price'] > 0.03]
    
    latest_contracts = chart_data.loc[chart_data.groupby('contract_id')['timestamp'].idxmax()]

    # TODO: Make chart toggle distances better so it doesnt load a bunch of granular data at once
    alt.data_transformers.enable('vegafusion')
    chart = alt.Chart(chart_data).mark_line().encode(
        x='timestamp:T',
        y='last_trade_price:Q',
        color='name:N'
    ).properties(
        width=600,
        height=400
    )
    chart_json = chart.to_json(format = 'vega')
    
    return render_template('market_detail.html', market=market_id, contracts=one_day_contracts, latest_contracts=latest_contracts, chart_json=chart_json)

@app.route('/set_threshold/<market_id>/<contract_id>', methods=['POST'])
def set_threshold(market_id, contract_id):
    buy_threshold = float(request.form['buy_threshold'])
    sell_threshold = float(request.form['sell_threshold'])
    
    orb.set_price(market_id, contract_id, 'buy', buy_threshold)
    orb.set_price(market_id, contract_id, 'sell', sell_threshold)
    
    print('Thresholds set successfully!')
    return redirect(url_for('market_detail', market_id=market_id))


if __name__ == '__main__':
    orb = ScryingOrb()

    # Scheduler to update data every minute
    scheduler = BackgroundScheduler()
    scheduler.add_job(orb.get_markets, 'interval', minutes = 1)
    scheduler.add_job(orb.check_price, 'interval', minutes = 1)
    scheduler.start()

    app.run(debug=True)