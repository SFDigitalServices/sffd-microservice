"""subclass of requests"""
import os
import requests

class FireRequest():
    def __init__(self):
        proxy_token = os.environ.get('DS_PROXY_TOKEN')
        api_key = os.environ.get('FIRE_API_KEY')

        self.requests = requests.Session()
        self.requests.headers.update({
            'X-DS-PROXY-TOKEN': proxy_token,
            'api_key': api_key
        })

        self.url = os.environ.get('FIRE_DB_URL')

    def get(self):
        return self.requests.get(self.url)

    def post(self, jsonParams):
        return self.requests.post(self.url, json=jsonParams)