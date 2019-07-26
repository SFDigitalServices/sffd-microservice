"""Main application module"""
import os
import json
import jsend
import sentry_sdk
import falcon
from .resources.records import Records
from .resources.record import Record

def start_service():
    """Start this service
    set SENTRY_DSN environmental variable to enable logging with Sentry
    """
    # Initialize Sentry
    sentry_sdk.init(os.environ.get('SENTRY_DSN'))
    # Initialize Falcon
    api = falcon.API()
    api.add_route('/records', Records())
    # api.add_route('/records/{id}', Record())
    api.add_sink(default_error, '')

    api.req_options.auto_parse_form_urlencoded = True
    api.req_options.strip_url_path_trailing_slash = True
    
    return api

def default_error(_req, resp):
    """Handle default error"""
    resp.status = falcon.HTTP_404
    msg_error = jsend.error('404 - Not Found')

    sentry_sdk.capture_message(msg_error)
    resp.body = json.dumps(msg_error)
