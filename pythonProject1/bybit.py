import hashlib
import hmac
import json
import requests
import time
from config import api_key, secret_key


class Bybit_api:
    """
    Class to interact with Bybit API
    """
    BASE_LINK = 'https://api.bybit.com'

    def __init__(self, api_key=None, api_secret=None, futures=True):
        """
        Initialize the Bybit API class

        Parameters:
        api_key (str): API key for Bybit
        api_secret (str): API secret key for Bybit
        futures (bool): Flag to indicate if using futures API
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.futures = futures
        if self.futures:
            self.category = 'linear'
        else:
            self.category = 'spot'

        self.header = {
            'X-BAPI-API-KEY': self.api_key,
            'X=BAPI-RECV-WINDOW': '5000'
        }

    def gen_signature(self, mod_params, timestamp):
        """
        Generate HMAC signature for API request

        Parameters:
        mod_params (str): Modified parameters string
        timestamp (str): Timestamp for the request

        Returns:
        str: HMAC signature
        """
        param_str = timestamp + self.api_key + '5000' + mod_params
        sign = hmac.new(bytes(self.secret_key, 'utf-8'), param_str.encode('utf-8'), hashlib.sha256).hexdigest()
        return sign

    def http_request(self, method, endpoint, params):
        """
        Make HTTP request to Bybit API

        Parameters:
        method (str): HTTP method (GET or POST)
        endpoint (str): API endpoint
        params (dict): Request parameters

        Returns:
        tuple: JSON response and response headers
        """
        timestamp = str(int(time.time() * 1000))
        params_get_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        params_post_json = json.dumps(params)

        if method == 'GET':
            sign = self.gen_signature(params_get_string, timestamp)
            self.header['X-BAPI-SIGN'] = sign
            self.header['X-BAPI-TIMESTAMP'] = timestamp
            response = requests.get(url=self.BASE_LINK + endpoint, params=params, headers=self.header)
        elif method == 'POST':
            sign = self.gen_signature(params_get_string, timestamp)
            self.header['X-BAPI-SIGN'] = sign
            self.header['X-BAPI-TIMESTAMP'] = timestamp
            response = requests.post(url=self.BASE_LINK + endpoint, json=params, headers=self.header)
        else:
            print('method error')
            return None

        if response:
            response_json = response.json()
            response_headers = response.headers
            return response_json, response_headers
        else:
            return response.text, None

    def get_klines(self, symbol: str, interval: str, start: int = None, end=None, limit=200, headers=False):
        """
        Get kline data for a symbol

        Parameters:
        symbol (str): Symbol to fetch kline data for
        interval (str): Kline interval
        start (int): Start timestamp
        end (int): End timestamp
        limit (int): Limit of data points to retrieve
        headers (bool): Flag to include response headers

        Returns:
        dict or tuple: Kline data or tuple of kline data and headers
        """
        endpoint = '/v5/market/kline'
        method = 'GET'
        params = {
            'category': self.category,
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        if start:
            params['start'] = start
        if end:
            params['end'] = end

        response_json, response_headers = self.http_request(method=method, endpoint=endpoint, params=params)
        if headers:
            return response_json, response_headers
        else:
            return response_json

    def post_market_order(self, symbol: str, side: str, qnt, reduce_only=False, headers=False):
        """
        Place a market order

        Parameters:
        symbol (str): Symbol to trade
        side (str): Order side (BUY or SELL)
        qnt (int): Quantity to trade
        reduce_only (bool): Flag for reduce-only order
        headers (bool): Flag to include response headers

        Returns:
        dict or tuple: Order response or tuple of order response and headers
        """
        endpoint = 'v5/order/create'
        method = 'POST'
        params = {
            'category': self.category,
            'symbol': symbol,
            'side': side.capitalize(),
            'order_type': 'Market',
            'qty': str(qnt),
        }
