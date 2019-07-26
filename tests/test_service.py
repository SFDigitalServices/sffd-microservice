# pylint: disable=redefined-outer-name
"""Tests"""
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

@pytest.fixture()
def client():
    """ client fixture """
    return testing.TestClient(service.microservice.start_service())

def test_default_error(client):
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

def test_get_records(client):
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

def test_create_record(client):
    # fire db api returns error
    with patch('service.resources.records.FireRequest.post') as mock_post:
        mock_post.return_value.status_code = 500
        response = client.simulate_post("/records")
    assert response.status_code == 500

    response_json = json.loads(response.text)
    assert response_json['status'] == 'error'

    # fire dbi api doesn't return id in header
    with patch('service.resources.records.FireRequest.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.headers = {}
        response = client.simulate_post("/records")
    assert response.status_code == 500
    response_json = json.loads(response.text)
    assert response_json['status'] == 'fail'

    # happy path
    with patch('service.resources.records.FireRequest.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.headers = {
            'id':1
        }
        response = client.simulate_post("/records")
    assert response.status_code == 200
    assert response.status == falcon.HTTP_200
    response_json = json.loads(response.text)
    assert response_json['status'] == 'success'
    assert isinstance(response_json['data']['id'], int)
    