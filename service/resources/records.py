"""Records in the fire db"""
import os
import json
import falcon
import jsend
from .fire_object import *

from pprint import pprint

class Records(FireObject):
    def on_get(self, req, resp):
        response = self.requests.get(self.url)
        resp.body = json.dumps(jsend.success(response.json()))
        resp.status = falcon.HTTP_200
        
    def on_post(self, req, resp):
        apiParams = {
            'revision': None
        }
        apiParams.update(req.params)

        response = self.requests.post(self.url, json=apiParams)

        if response and response.status_code == 200:
            id = response.headers.get('id')
            payload = {
                'message':response.headers.get('result_message')
            }
            if str.isdigit(id):
                # response returned an id
                payload['id'] = id
                resp.body = json.dumps(jsend.success(payload))
                resp.status = falcon.HTTP_200
            else:
                # no id means something went wrong
                resp.body = json.dumps(jsend.fail(payload))
                resp.status = falcon.HTTP_500
        else:
            resp.body = json.dumps(jsend.fail('There was a problem communicating with the fire db api'))
            resp.status = response.status_code
