import time
import pyupbit
import datetime
import numpy as np

access = "your-access"
secret = "your-secret"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_average(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['avg_buy_price'] is not None:
                return float(b['avg_buy_price'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 매도가 조회"""
    return pyupbit.get_orderbook(ticker)["orderbook_units"][0]["ask_price"]

def get_bid_price(ticker):
    """현재 매수가 조회"""
    return pyupbit.get_orderbook(ticker)["orderbook_units"][0]["bid_price"]

def cur_price(ticker):
    """현재 체결가 조회"""
    return pyupbit.get_current_price(ticker)

def get_odd(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    odd = df.iloc[1]['volume'] / df.iloc[0]['volume']
    return odd

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

transaction=0
avg_price=0
k=0.3
sp=0.98
target_coin=[]
t_coin=[]
target_price=[]
tops = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-ADA', 'KRW-SOL']
ts=[]
for no in range(len(tops)):
    t=tops[no][4:]
    ts.append(t)

pools= ['KRW-STPT', 'KRW-QKC', 'KRW-AXS', 'KRW-CBK', 'KRW-RFR', 'KRW-HIVE', 'KRW-STX', 'KRW-DOT', 'KRW-POLY', 'KRW-OMG']
    
# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        pooltime1=start_time + datetime.timedelta(minutes=30)
        pooltime2=start_time + datetime.timedelta(minutes=60)
        pooltime3=start_time + datetime.timedelta(minutes=90)
        pooltime4=start_time + datetime.timedelta(minutes=120)
        pooltime5=start_time + datetime.timedelta(minutes=150)
        pooltime6=start_time + datetime.timedelta(minutes=180)

        if start_time < now < end_time - datetime.timedelta(seconds=30):
            if transaction == 0:
                if pooltime1 < now < (pooltime1 + datetime.timedelta(seconds=10)) or pooltime2 < now < (pooltime2 + datetime.timedelta(seconds=10)) or pooltime3 < now < (pooltime3 + datetime.timedelta(seconds=10)) or pooltime4 < now < (pooltime4 + datetime.timedelta(seconds=10)) or pooltime6 < now < (pooltime2 + datetime.timedelta(seconds=10)) or pooltime6 < now < (pooltime6 + datetime.timedelta(seconds=10)):
                    poolplus=[]
                    for po in pools:
                        odd= get_odd(po)
                        if odd > 2:
                            poolplus.append(po)
                    [tops.append(x) for x in poolplus if x not in tops]     
                    ts=[]
                    for no in range(len(tops)):
                        t=tops[no][4:]
                        ts.append(t) 
                    for n in tops:
                        target = get_target_price(n, k)
                        target_price.append(target)
                        
                if not bool(target_price):
                    for n in tops:
                        target = get_target_price(n, k)
                        target_price.append(target)
                
                current_price=[]
                comp=[]
                i=0
                for nn in tops:
                    current = get_current_price(nn)
                    current_price.append(current)
                    comp.append(target_price[i] < current)
                    i += 1

                if any(comp):  
                    buying=[]
                    for ii in list(np.where(comp)[0]):
                        val = pyupbit.get_ohlcv(tops[ii], interval="day", count=1)
                        buying.append((tops[ii], val.iloc[0]['value']))
                    sorted_buying = sorted(buying, key=lambda x:x[1], reverse=True)
                    target_coin=sorted_buying[0][0]
                    t_coin=target_coin[4:]
                    krw = get_balance("KRW")
                    if krw > 5000:
                        upbit.buy_market_order(target_coin, krw*0.9995)
                        transaction = 1    
                        avg_price = get_average(t_coin)          
    
            elif transaction == 1:
                curr_price = cur_price(target_coin)    
                if curr_price < (avg_price * sp):
                    coin_val = get_balance(t_coin)
                    if coin_val > (5000 / curr_price): 
                        upbit.sell_market_order(target_coin, coin_val)  
                        transaction=2
 
        else:
            for c in range(len(tops)):
                coin_val = get_balance(ts[c])
                curr_price = cur_price(tops[c])   
                if coin_val > (5000/curr_price): 
                    upbit.sell_market_order(target_coin, coin_val)  
            transaction=0
            avg_price=0
            target_price=[]
            tops= ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-ADA', 'KRW-SOL']
            ts=[]
            for no in range(len(tops)):
                t=tops[no][4:]
                ts.append(t) 
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
