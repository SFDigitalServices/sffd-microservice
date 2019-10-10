# pylint: disable=redefined-outer-name
"""Tests"""
import os
import json
import jsend
import pytest
import falcon
from falcon import testing
import service.microservice
from unittest.mock import patch
from service.resources.fire_request import FireRequest
from service.resources.records import Records
from requests.models import Response
from http.client import responses
from urllib.parse import urlencode

MOCK_RECORDS_LISTING = """{  
    "items":[
        {
            "id":1,
            "dbi_no":"1111",
            "revision":null,
            "block":null,
            "lot":null,
            "job_size":null,
            "floors":null,
            "dba_date":null,
            "occupant_type":null,
            "contractor":null,
            "dbi_empl":null,
            "created":"2019-06-18T22:37:04Z",
            "updated":null,
            "status":"NEW"
        },
        {  
            "id":3,
            "dbi_no":"1111",
            "revision":"2",
            "block":null,
            "lot":null,
            "job_size":null,
            "floors":null,
            "dba_date":null,
            "occupant_type":null,
            "contractor":null,
            "dbi_empl":null,
            "created":"2019-06-18T22:38:37Z",
            "updated":null,
            "status":"NEW"
        },
        {  
            "id":4,
            "dbi_no":"1111",
            "revision":"3",
            "block":null,
            "lot":null,
            "job_size":null,
            "floors":null,
            "dba_date":null,
            "occupant_type":null,
            "contractor":null,
            "dbi_empl":null,
            "created":"2019-06-19T18:26:29Z",
            "updated":null,
            "status":"NEW"
        }
    ],
    "hasMore":false,
    "limit":25,
    "offset":0,
    "count":3,
    "links":[  
        {  
            "rel":"self",
            "href":"http://10.31.6.233/ords/fp/dbi/stage/"
        },
        {  
            "rel":"edit",
            "href":"http://10.31.6.233/ords/fp/dbi/stage/"
        },
        {  
            "rel":"describedby",
            "href":"http://10.31.6.233/ords/fp/metadata-catalog/dbi/stage/"
        },
        {  
            "rel":"first",
            "href":"http://10.31.6.233/ords/fp/dbi/stage/"
        }
    ]
}"""

CLIENT_HEADERS = {
    "ACCESS_KEY": "1234567"
}

@pytest.fixture
def client():
    """ client fixture """
    return testing.TestClient(app=service.microservice.start_service(), headers=CLIENT_HEADERS)

@pytest.fixture
def mock_env_access_key(monkeypatch):
    header_key = "ACCESS_KEY"
    monkeypatch.setenv(header_key, CLIENT_HEADERS[header_key])

def test_default_error(client, mock_env_access_key):
    """Test default error response"""
    response = client.simulate_get('/some_page_that_does_not_exist')

    assert response.status_code == 404

    expected_msg_error = jsend.error('404 - Not Found')
    assert json.loads(response.content) == expected_msg_error

def test_fire_request_get():
    with patch('service.resources.fire_request.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(MOCK_RECORDS_LISTING)

        resp = FireRequest.get()
    assert resp.status_code == 200
    assert resp.json() == json.loads(MOCK_RECORDS_LISTING)

def test_fire_request_post():
    with patch('service.resources.fire_request.requests.post') as mock_post:
        mock_post.return_value.status_code = 200

        resp = FireRequest.post({})
    assert resp.status_code == 200

def test_get_records(client, mock_env_access_key):
    # fire db api return error
    with patch('service.resources.records.FireRequest.get') as mock_get:
        mock_get.return_value.status_code = 500
        response = client.simulate_get("/records")
    assert response.status_code == 500
    response_json = json.loads(response.text)
    assert response_json['message'] == Records.ERROR_MSG

    # happy path
    with patch('service.resources.records.FireRequest.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(MOCK_RECORDS_LISTING)
        mock_get.return_value.text.return_value = MOCK_RECORDS_LISTING

        response = client.simulate_get("/records")
    assert response.status_code == 200
    
    response_json = json.loads(response.text)
    assert response_json['status'] == 'success'
    assert response_json['data'] == json.loads(MOCK_RECORDS_LISTING)

    # no access key from client
    client_no_access_key = testing.TestClient(app=service.microservice.start_service())
    with patch('service.resources.records.FireRequest.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = json.loads(MOCK_RECORDS_LISTING)
        mock_get.return_value.text.return_value = MOCK_RECORDS_LISTING

        response = client_no_access_key.simulate_get("/records")
    assert response.status_code == 403

def post_params():
    return {
        'dbi_no': 201912251234,
        'lot': 'lot',
        'block': 'block'
    }

def post_response_with_successful_fire_api_mock(client, params):
    with patch('service.resources.records.FireRequest.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.headers = {
            'id':1
        }
        response = client.simulate_post("/records", headers={'Content-Type': 'application/x-www-form-urlencoded'}, body=urlencode(params))
    return response

def test_create_record(client, mock_env_access_key):
    # #######################################
    # fire db api returns error
    # #######################################
    with patch('service.resources.records.FireRequest.post') as mock_post:
        mock_post.return_value.status_code = 500
        response = client.simulate_post("/records", headers={'Content-Type': 'application/x-www-form-urlencoded'}, body=urlencode(post_params()))
    assert response.status_code == 500
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # #######################################
    # fire dbi api doesn't return id in header
    # #######################################
    with patch('service.resources.records.FireRequest.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.headers = {}
        response = client.simulate_post("/records", headers={'Content-Type': 'application/x-www-form-urlencoded'}, body=urlencode(post_params()))
    assert response.status_code == 500
    response_json = json.loads(response.text)
    assert response_json['status'] == 'fail'

    # #######################################
    # missing dbi_no
    # #######################################
    params = post_params()
    params.pop('dbi_no')
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 400
    assert response.status == falcon.HTTP_400
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # #######################################
    # missing block
    # #######################################
    params = post_params()
    params.pop('block')
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 400
    assert response.status == falcon.HTTP_400
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # #######################################
    # missing lot
    # #######################################
    params = post_params()
    params.pop('lot')
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 400
    assert response.status == falcon.HTTP_400
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # #######################################
    # invalid dbi_no length
    # #######################################
    params = post_params()
    params['dbi_no'] = 1234567
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 400
    assert response.status == falcon.HTTP_400
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # #######################################
    # invalid dbi_no non digits
    # #######################################
    params = post_params()
    params['dbi_no'] = '2019010143ab'
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 400
    assert response.status == falcon.HTTP_400
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # #######################################
    # invalid dbi_no length
    # #######################################
    params = post_params()
    params['dbi_no'] = 1234567
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 400
    assert response.status == falcon.HTTP_400
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # #######################################
    # invalid dbi_no month
    # #######################################
    params = post_params()
    params['dbi_no'] = 201913091234
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 400
    assert response.status == falcon.HTTP_400
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # #######################################
    # invalid dbi_no day
    # #######################################
    params = post_params()
    params['dbi_no'] = 201909321234
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 400
    assert response.status == falcon.HTTP_400
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # #######################################
    # invalid dbi_no nonexistant date
    # #######################################
    params = post_params()
    params['dbi_no'] = 201902291234
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 400
    assert response.status == falcon.HTTP_400
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # #######################################
    # job_size must be int
    # #######################################
    params = post_params()
    params['job_size'] = "5,000"
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 200
    assert response.status == falcon.HTTP_200
    response_json = json.loads(response.text)
    assert response_json['status'] == 'success'

    params['job_size'] = "50A"
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 400
    assert response.status == falcon.HTTP_400
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # #######################################
    # dbi_date in YYYY/MM/DD format
    # #######################################
    params = post_params()
    params['dbi_date'] = "2019/09/10"
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 200
    assert response.status == falcon.HTTP_200
    response_json = json.loads(response.text)
    assert response_json['status'] == 'success'

    params['dbi_date'] = "20190910"
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 400
    assert response.status == falcon.HTTP_400
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    params['dbi_date'] = "Dec 25, 2001"
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client, params)
    assert response.status_code == 400
    assert response.status == falcon.HTTP_400
    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # #######################################
    # no access key from client
    # #######################################
    client_no_access_key = testing.TestClient(app=service.microservice.start_service())
    # fire api is mocked to succeed, but error should be returned before and fire api shouldn't be called
    # if fire api gets called, response will return success where we are expecting an error
    response = post_response_with_successful_fire_api_mock(client_no_access_key, post_params())
    assert response.status_code == 403

    # #######################################
    # happy path
    # #######################################
    response = post_response_with_successful_fire_api_mock(client, post_params())
    assert response.status_code == 200
    assert response.status == falcon.HTTP_200
    response_json = json.loads(response.text)
    assert response_json['status'] == 'success'
    assert isinstance(response_json['data']['id'], int)
