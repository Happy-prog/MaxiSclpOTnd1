import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
import time
import logging
from strategy import ScalpingStrategy
from risk_management import RiskManager
from portfolio import Portfolio

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScalpingBot:
    def __init__(self, exchange_name='binance', api_key='', api_secret='', pair='BTC/USDT'):
        self.exchange = self._init_exchange(exchange_name, api_key, api_secret)
        self.pair = pair
        self.strategy = ScalpingStrategy()
        self.risk_manager = RiskManager(initial_balance=1000)
        self.portfolio = Portfolio()
        self.trades_today = 0
        self.max_trades_per_day = 100
        self.min_holding_time = 60
        self.last_trade_time = None
        
    def _init_exchange(self, exchange_name, api_key, api_secret):
        if exchange_name.lower() == 'binance':
            exchange = ccxt.binance({'apiKey': api_key, 'secret': api_secret})
        elif exchange_name.lower() == 'coinbase':
            exchange = ccxt.coinbase({'apiKey': api_key, 'secret': api_secret})
        elif exchange_name.lower() == 'kraken':
            exchange = ccxt.kraken({'apiKey': api_key, 'secret': api_secret})
        else:
            raise ValueError(f"Exchange {exchange_name} not supported")
        return exchange
    
    def fetch_ohlcv(self, timeframe='1m', limit=100):
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.pair, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"Error fetching OHLCV: {e}")
            return None
    
    def get_current_price(self):
        try:
            ticker = self.exchange.fetch_ticker(self.pair)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
            return None
    
    def generate_signal(self, df):
        if df is None or len(df) < 50:
            return None
        signal = self.strategy.calculate_signal(df)
        return signal
    
    def place_order(self, side, amount, price=None):
        try:
            if price:
                order = self.exchange.create_limit_order(self.pair, side, amount, price)
            else:
                order = self.exchange.create_market_order(self.pair, side, amount)
            logger.info(f"Order placed: {side.upper()} {amount} {self.pair} at {price or 'market price'}")
            return order
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def execute_trade(self, signal, current_price, account_balance):
        if signal is None:
            return
        if self.trades_today >= self.max_trades_per_day:
            logger.warning("Max trades per day reached")
            return
        if self.last_trade_time and time.time() - self.last_trade_time < self.min_holding_time:
            return
        position_size = self.risk_manager.calculate_position_size(account_balance, risk_per_trade=0.02)
        
        if signal == 'BUY':
            logger.info(f"BUY Signal at {current_price}")
            order = self.place_order('buy', position_size, current_price)
            if order:
                self.portfolio.add_position('BTC', position_size, current_price)
                self.trades_today += 1
                self.last_trade_time = time.time()
        elif signal == 'SELL':
            if self.portfolio.has_position('BTC'):
                logger.info(f"SELL Signal at {current_price}")
                order = self.place_order('sell', position_size, current_price)
                if order:
                    profit = self.portfolio.close_position('BTC', current_price)
                    logger.info(f"Trade closed with profit: {profit}")
                    self.trades_today += 1
                    self.last_trade_time = time.time()
    
    def run(self):
        logger.info("Scalping bot started")
        while True:
            try:
                df = self.fetch_ohlcv(timeframe='1m', limit=100)
                current_price = self.get_current_price()
                if df is None or current_price is None:
                    time.sleep(5)
                    continue
                signal = self.generate_signal(df)
                balance = self.exchange.fetch_balance()
                usdt_balance = balance['USDT']['free']
                self.execute_trade(signal, current_price, usdt_balance)
                logger.info(f"Price: {current_price}, Portfolio: {self.portfolio.get_summary()}")
                time.sleep(5)
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    bot = ScalpingBot(exchange_name='binance', api_key='YOUR_API_KEY', api_secret='YOUR_API_SECRET', pair='BTC/USDT')
    bot.run()