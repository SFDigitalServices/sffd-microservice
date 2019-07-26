"""subclass of requests"""
import os
import requests

class FireRequest():
    proxy_token = os.environ.get('DS_PROXY_TOKEN')
    api_key = os.environ.get('FIRE_API_KEY')

    reqs = requests.Session()
    reqs.headers.update({
        'X-DS-PROXY-TOKEN': proxy_token,
        'api_key': api_key
    })

    url = os.environ.get('FIRE_DB_URL')


    def get():
        return FireRequest.reqs.get(FireRequest.url)

    def post(jsonParams):
        return FireRequest.reqs.post(FireRequest.url, json=jsonParams)