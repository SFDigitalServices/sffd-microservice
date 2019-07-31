"""FireRequests"""
import os
import requests

class FireRequest():
    """Like requests, but encapsulates api_key and proxy token"""
    proxy_token = os.environ.get('DS_PROXY_TOKEN')
    api_key = os.environ.get('FIRE_API_KEY')
    url = os.environ.get('FIRE_DB_URL')

    headers = {
        'X-DS-PROXY-TOKEN': proxy_token,
        'api_key': api_key
    }

    @staticmethod
    def get():
        """perform get request"""
        return requests.get(FireRequest.url, headers=FireRequest.headers)

    @staticmethod
    def post(json_params):
        """perform post request"""
        return requests.post(FireRequest.url, headers=FireRequest.headers, json=json_params)
