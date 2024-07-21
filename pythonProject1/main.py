from time import sleep
import numpy as np
from config import api_key, secret_key
from bybit import Bybit_api
from indicators import ema
import time


def sleep_to_next_minute():
    """
    Function to calculate the time to sleep until the next minute and sleep for that duration.
    """
    time_to_sleep = 60 - time.time() % 60 + 2
    print(f'Sleeping for {time_to_sleep} seconds')
    time.sleep(time_to_sleep)


if __name__ == "__main__":
    # Initialize the Bybit API client
    client = Bybit_api(api_key, secret_key, futures=True)

    while True:
        # Sleep until the start of the next minute
        sleep_to_next_minute()

        # Get the latest klines data for ETHUSDT with a 5-minute interval
        klines = client.get_klines(symbol='ETHUSDT', interval='5', limit=20)
        klines = klines['result']['list']
        last_candle = klines[0]

        # Remove the last candle if its closing time is in the future
        if time.time() < int(last_candle[0]):
            klines.pop()

        # Convert klines data to numpy array for easier manipulation
        numpy_klines = np.array(klines)
        close_prices = numpy_klines[:, 4].astype(float)

        # Calculate short and long EMAs
        ema_short = ema(close_prices, 6)
        ema_long = ema(close_prices, 12)

        # Get the last values of short and long EMAs
        short_value = ema_short[-1]
        prev_short_value = ema_short[-2]

        long_value = ema_long[-1]
        prev_long_value = ema_long[-2]

        # Execute buy or sell orders based on EMA crossover strategy
        if short_value > long_value and prev_short_value < prev_long_value:
            print('buy')
            client.post_market_order(symbol='ETHUSDT', side='Buy', qnt=1)
        elif short_value < long_value and prev_short_value > prev_long_value:
            print('sell')
            client.post_market_order(symbol='ETHUSDT', side='Sell', qnt=1)
        else:
            print('no signal')

        print('short_value', short_value)
        print('long_value', long_value)