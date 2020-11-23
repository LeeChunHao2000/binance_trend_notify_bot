<<<<<<< HEAD
# binance_trend_notify_bot
=======
# binance_trend_notify_bot
<<<<<<< HEAD
=======


需要一個統計每日信號次數的函式

思路如下:

每日第一次
1. 在 updatePair() 存一份幣種清單 {'BTCUSDT': 0, ....., 'ZZZUSDT': 0}
2. 在 alart() 把 清單['symbol'] += 1
3. 存到 csv

其他次
1. 讀取 csv
2. 在 alart() 把 清單['symbol'] += 1
3. 存到 csv
<<<<<<< HEAD
"""
>>>>>>> 56de667... First commit
=======
>>>>>>> baef981... First commit
>>>>>>> 9fd682c... reset 2
