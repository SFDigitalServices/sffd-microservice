"""subclass of requests"""
import os
import requests

class FireRequest():
    proxy_token = os.environ.get('DS_PROXY_TOKEN')
    api_key = os.environ.get('FIRE_API_KEY')
    url = os.environ.get('FIRE_DB_URL')

    headers = {
        'X-DS-PROXY-TOKEN': proxy_token,
        'api_key': api_key
    }

    def get():
        return requests.get(FireRequest.url, headers=FireRequest.headers)

    def post(jsonParams):
        return requests.post(FireRequest.url, headers=FireRequest.headers, json=jsonParams)