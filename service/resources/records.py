"""Records in the fire db"""
import json
from http.client import responses
import falcon
import jsend
import re
import datetime
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

        """check for required fields"""
        if not all(x in req.params.keys() for x in ['dbi_no', 'block', 'lot']):
            resp.body = json.dumps(jsend.error("dbi_no, block, and lot are required"))
            resp.status = falcon.HTTP_400
            return

        """check dbi_no is in correct format"""
        """YYYYMMDDNNNN"""
        is_valid_dbi_no = False
        dbi_no = req.params.get('dbi_no')
        if len(dbi_no) == 12 and re.match(r'\d+$', dbi_no) is not None:
            is_valid_dbi_no = True
            # The following lines of code are commented out in order to enable fake dbi_no.
            # Keeping the code around in case fake dbi_no are no longer necessary.
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # date_part = dbi_no[:8]
            # try:
            #     datetime.datetime.strptime(date_part, '%Y%m%d')
            #     is_valid_dbi_no = True
            # except:
            #     pass
            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        if not is_valid_dbi_no:
            resp.body = json.dumps(jsend.error("invalid dbi_no"))
            resp.status = falcon.HTTP_400
            return

        """job_size is integer"""
        if req.params.get('job_size', False):
            try:
                int(req.params.get('job_size').replace(',', ''))
            except:
                resp.body = json.dumps(jsend.error("job_size should be an integer"))
                resp.status = falcon.HTTP_400
                return

        """dbi_date in YYYY/MM/DD format"""
        if req.params.get('dbi_date', False):
            try:
                datetime.datetime.strptime(req.params.get('dbi_date'), '%Y/%m/%d')
            except:
                resp.body = json.dumps(jsend.error("dbi_date should be in YYYY/MM/DD format"))
                resp.status = falcon.HTTP_400
                return

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
