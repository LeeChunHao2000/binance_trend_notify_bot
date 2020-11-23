# -*- coding: utf-8 -*
import ssl
import time
import datetime
import requests
import pandas as pd

ssl._create_default_https_context = ssl._create_unverified_context

# global variables
pairs = {}
price = []

def updatePair():
    try:
        data = requests.get('https://fapi.binance.com/fapi/v1/exchangeInfo').json()['symbols']
    except Exception as e:
        print (f'無法獲取交易對，錯誤為: {str(e)}')

    for pair in data:
        pairs[pair['symbol']] = {}

def updateHL():
    try:
        for symbol in pairs:
            high = 0
            low  = 200000
            data = requests.get(f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1w&limit=4').json()
            for i in data:
                high = float(i[2]) if float(i[2]) > high else high
                low  = float(i[3]) if float(i[3]) < low  else low
            pairs[symbol] = {'high': high * 0.999, 'low': low * 1.001}
    except Exception as e:
        print (f'無法獲取最高最低價，錯誤為: {str(e)}')

def updatePrice():
    try:
        global price
        price = requests.get('https://fapi.binance.com/fapi/v1/ticker/price').json()
    except Exception as e:
        print (f'無法獲取最新價格，錯誤為: {str(e)}')

def comparePrice():
    for pair in price:
        if float(pair['price']) > pairs[pair['symbol']]['high']:
            statics[pair['symbol']] += 1
            alart(pair['symbol'], '新高', pair['price'])
            saveStatics()
        if float(pair['price']) < pairs[pair['symbol']]['low']:
            statics[pair['symbol']] += 1
            alart(pair['symbol'], '新低', pair['price'])
            saveStatics()

def getRatio(symbol):
    try:
        ratio = requests.get(f'https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period=5m&limit=1').json()[0]['longShortRatio']
        ratio4h = requests.get(f'https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period=4h&limit=2').json()[0]['longShortRatio']
    except Exception as e:
        print (f'無法獲取多空比，錯誤為: {str(e)}')
    
    change = round((float(ratio) / float(ratio4h) - 1) * 100, 2)
    change = f'+{change}' if change > 0 else change
    
    return ratio, str(change)

def getInterest(symbol):
    try:
        interest = requests.get(f'https://fapi.binance.com/futures/data/openInterestHist?symbol={symbol}&period=5m&limit=1').json()[0]['sumOpenInterestValue']
        interest4h = requests.get(f'https://fapi.binance.com/futures/data/openInterestHist?symbol={symbol}&period=4h&limit=2').json()[0]['sumOpenInterestValue']
    except Exception as e:
        print (f'無法獲取持倉量，錯誤為: {str(e)}')

    change = round((float(interest) / float(interest4h) - 1) * 100, 2)
    change = f'+{change}' if change > 0 else change
    
    interest = round(int(float(interest))/1000000, 2)
    
    return str(interest), change

def getFundingRate(symbol):
    try:
        rate = requests.get(f'https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}').json()['interestRate']
    except Exception as e:
        print (f'無法獲取資金費，錯誤為: {str(e)}')
    
    return str(float(rate) * 100)

def alart(symbol, side, current):
    ratio, change = getRatio(symbol)
    interest, ichange = getInterest(symbol)
    rate = getFundingRate(symbol)
    times = statics[symbol]
    v = f'突破幣種: {symbol}<br>' + \
        f'突破方向: {side}<br>' + \
        f'本日次數: {times}<br>' + \
        f'當前價格: {current}<br>' + \
        f'多空比例: {ratio} ({change}%)<br>' + \
        f'持倉價值: {interest}M ({ichange}%)<br>' + \
        f'資金費率: {rate} %'
    r = requests.get(f'https://maker.ifttt.com/trigger/binance_chasing/with/key/密鑰?value1={str(v)}')
    if r.text[:5] == 'Congr':
        print(f'Success send ({symbol}) to Line')

def readStatics():
    global statics
    statics = pd.read_csv('statics.csv', index_col=0)

def saveStatics():
    statics.to_csv('statics.csv')

def resetStatics():
    severTime = int(requests.get('https://fapi.binance.com/fapi/v1/time').json()['serverTime'] / 1000)
    today = f'{datetime.date.today()} 00:00:00'
    today = time.strptime(today, "%Y-%m-%d %H:%M:%S")
    today = int(time.mktime(today))
    if severTime - today < 300:
        statics = pd.DataFrame(pairs)
        statics.loc['times'] = 0
        statics.to_csv('statics.csv')


if __name__ == "__main__":
    updatePair()
    resetStatics()
    readStatics()
    updateHL()
    updatePrice()
    comparePrice()