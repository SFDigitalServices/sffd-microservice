"""Records in the fire db"""
import json
import falcon
import jsend
from http.client import responses
from .fire_request import *

from pprint import pprint

class Records():
    ERROR_MSG = 'There was a problem communicating with the fired db api'
    
    def on_get(self, req, resp):
        response = FireRequest().get()
        if response.status_code == 200:
            resp.body = json.dumps(jsend.success(response.json()))
        else:
            resp.body = json.dumps(jsend.error(Records.ERROR_MSG))
            resp.status = str(response.status_code) + " " + responses[response.status_code]
        
    def on_post(self, req, resp):
        apiParams = {
            'revision': None
        }
        apiParams.update(req.params)

        response = FireRequest().post(json=apiParams)

        if response and response.status_code == 200:
            id = response.headers.get('id', False)
            payload = {
                'message':response.headers.get('result_message')
            }
            if id:
                # response returned an id
                payload['id'] = id
                resp.body = json.dumps(jsend.success(payload))
                resp.status = falcon.HTTP_200
            else:
                # no id means something went wrong
                resp.body = json.dumps(jsend.fail(payload))
                resp.status = falcon.HTTP_500
        else:
            resp.body = json.dumps(jsend.error(Records.ERROR_MSG))
            resp.status = str(response.status_code) + " " + responses[response.status_code]
