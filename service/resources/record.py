"""A record in the fire db"""
import os
import json
import falcon
import jsend
from .fire_object import *

from pprint import pprint

class Record(FireObject):
    def on_get(self, req, resp, id):
        print("Record.on_get")
        url = os.environ.get('FIRE_DB_URL')
        if not url.endswith('/'):
            url += '/'
        url += id
        # print("url:"+url)
        response = self.requests.get(url)
        resp.body = json.dumps(jsend.success(response.json()))

    # def on_post(self, req, resp):
    #     msg = {'message': 'Welcome'}
    #     resp.body = json.dumps(jsend.success(msg))
    #     resp.status = falcon.HTTP_200
