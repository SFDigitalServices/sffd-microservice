"""Records in the fire db"""
import json
from http.client import responses
import falcon
import jsend
from .fire_request import FireRequest
from .hooks import validate_access

@falcon.before(validate_access)
class Records():
    """Records Controller"""
    ERROR_MSG = 'There was a problem communicating with the fired db api'

    def on_get(self, req, resp):
        """handle the get request"""
        response = FireRequest.get()
        if response.status_code == 200:
            resp.body = json.dumps(jsend.success(response.json()))
        else:
            resp.body = json.dumps(jsend.error(Records.ERROR_MSG))
            resp.status = str(response.status_code) + " " + responses[response.status_code]

    def on_post(self, req, resp):
        """handle the post request"""
        api_params = {
            'revision': None
        }
        api_params.update(req.params)

        response = FireRequest.post(api_params)

        if response and response.status_code == 200:
            return_id = response.headers.get('id', False)
            payload = {
                'message':response.headers.get('result_message')
            }
            if return_id:
                # response returned an id
                payload['id'] = return_id
                resp.body = json.dumps(jsend.success(payload))
                resp.status = falcon.HTTP_200
            else:
                # no id means something went wrong
                resp.body = json.dumps(jsend.fail(payload))
                resp.status = falcon.HTTP_500
        else:
            resp.body = json.dumps(jsend.error(Records.ERROR_MSG))
            resp.status = str(response.status_code) + " " + responses[response.status_code]
