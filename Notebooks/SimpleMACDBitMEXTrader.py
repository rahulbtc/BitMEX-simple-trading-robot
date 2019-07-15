import talib
import pandas as pd
import bitmex
import time
    

class Strategy():
        def __init__(self, client, timeframe='5m'):
            self.client = client
            self.timeframe = timeframe
            
        def predict(self):
            ohlcv_candles = pd.DataFrame(self.client.Trade.Trade_getBucketed(
                binSize=self.timeframe,
                symbol='XBTUSD',
                count=100,
                reverse=True
            ).result()[0])
            ohlcv_candles.set_index(['timestamp'], inplace=True)
            macd, signal, hist = talib.MACD(ohlcv_candles.close.values,
                                            fastperiod = 8, slowperiod = 28, signalperiod = 9)
            
            #sell
            if hist[-2] > 0 and hist[-1] < 0:
                return -1
            #buy
            if hist[-2] < 0 and hist[-1] > 0:
                return 1
            #do nothing
            else:
                return 0
                
class Trader():
        def __init__(self, client, strategy, money_to_trade=100, leverage=5):
            self.client = client
            self.strategy = strategy
            
            self.money_to_trade = money_to_trade
            self.leverage = leverage
            
        def execute_trade(self):
            prediction = self.strategy.predict()
            
            print("Last prediction: {prediction}")
            
            try:
              if prediction == 1:
                response = self.client.Order.Order_new(
                    symbol='XBTUSD',
                    side='Buy',
                    orderQty=self.money_to_trade * self.leverage,
                    ).result()
                   
              if prediction == -1:
                response = self.client.Order.Order_new(
                    symbol='XBTUSD',
                    side='Sell',
                    orderQty=self.money_to_trade * self.leverage,
                    ).result()
                
            except Exception:
                print("Something goes wrong!")
            
            return
client = bitmex.bitmex(test=True,
                       api_key="ryJtdgCmz0P-_fjB5PadKqEc",
                       api_secret="4ED3zMDg4yadbjqxMzqYogEKn1STgtLO7mwrVkdWVZEuPUYA", 
                       time_to_wait_new_trade = 60*60,
                       strategy = Strategy(client, timeframe='1h'),
                       trader = Trader(client, strategy))
while True:
  if round(time.time()) % time_to_wait_new_trade == 0:
      trader.execute_trade()
      time.sleep(1)
