import os
import falcon

def validate_access(req, resp, resource, params):
    access_key = os.environ.get('ACCESS_KEY')
    if access_key and req.get_header('ACCESS_KEY') != access_key:
        raise falcon.HTTPForbidden(description='Get off my lawn!')
