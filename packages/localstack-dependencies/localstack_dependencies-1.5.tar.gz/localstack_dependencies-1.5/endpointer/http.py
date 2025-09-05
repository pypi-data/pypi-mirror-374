import json
from urllib.parse import parse_qs
from http import HTTPStatus as http_status
import endpointer.regexp as ep_regexp

RESPONSE_STATUS = 'response_status'
RESPONSE_HEADERS = 'response_headers'
RESPONSE_BODY = 'response_body'
CONTENT_LENGTH = 'Content-Length'
CONTENT_TYPE = 'Content-Type'
UTF_8 = 'utf-8'
APPLICATION_JSON = 'application/json'
CLIENT_IP = 'client_ip'
PATH_INFO = 'PATH_INFO'
ERROR_CODE_FIELD = 'error-code'
DOCS_URL_FIELD = 'docs-url'
INVALID_PATH_OPERATION = 'invalid-patch-operation'

FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S'

def format_datetime(date_time, format_string=FORMAT_DATETIME):

    date_time_string = date_time.strftime(format_string)
    return date_time_string

def get_path_info(environ):

    path_info = environ.get(PATH_INFO)
    if path_info is None:
        return None
    
    return path_info

def get_request_uri(environ):

    uri = get_path_info(environ)
    if uri is None:
        return None
    
    request_uri = uri.split('/')

    del request_uri[0]
   
    return request_uri

def get_request_verb(environ):
    
    request_verb = environ.get('REQUEST_METHOD')
    return request_verb

def get_request_headers(environ):
    
    request_headers = {}

    for k,v in environ.items():

        key = str(k).lower().replace('_', '-')

        is_http = key.startswith('http-')
        if is_http:
            new_key = key[5:]
            request_headers[new_key] = v

    request_headers[CLIENT_IP] = environ['REMOTE_ADDR']

    return request_headers

def get_client_ip(request_headers):

    return request_headers[CLIENT_IP]

def get_request_parameters(environ):

    query_string = get_query_string(environ)
    query_params = parse_qs(query_string)

    single_params = {}

    for k in query_params:

        has_more_than_one = (len(query_params[k]) > 1)
        if has_more_than_one:
            single_params[k] = query_params[k]
        else:
            single_params[k] = query_params[k][0]

    return single_params

def get_query_string(environ):

    query_string = environ['QUERY_STRING']

    return query_string

def get_request_body(environ):
    
    if not ('CONTENT_LENGTH' in environ):
        return None

    content_length = int(environ['CONTENT_LENGTH'])

    if content_length == 0:
        return None

    request_body = environ['wsgi.input'].read(content_length)

    request_body_string = request_body.decode(UTF_8)

    request_body_json = json.loads(request_body_string)

    return request_body_json

def prepare_response_package(response_headers, response_body):

    response_body_string = json.dumps(response_body)

    response_body_bytes = response_body_string.encode(UTF_8)

    response_headers[CONTENT_TYPE] = APPLICATION_JSON
    response_headers[CONTENT_LENGTH] = str(len(response_body_bytes))

    response_headers_list = list(response_headers.items())
    
    return (response_headers_list, [response_body_bytes])

def ok_response(response_headers, response_body):

    return {

        RESPONSE_STATUS: http_status.OK,
        RESPONSE_HEADERS: response_headers,
        RESPONSE_BODY: response_body

    }

def created_response(response_headers, response_body):

    return {

        RESPONSE_STATUS: http_status.CREATED,
        RESPONSE_HEADERS: response_headers,
        RESPONSE_BODY: response_body

    }

def no_content_response(response_headers={}):

    response_body = {}

    return {

        RESPONSE_STATUS: http_status.NO_CONTENT,
        RESPONSE_HEADERS: response_headers,
        RESPONSE_BODY: response_body

    }

def method_not_allowed_response(response_headers={}):

    response_body = {}

    return {

        RESPONSE_STATUS: http_status.METHOD_NOT_ALLOWED,
        RESPONSE_HEADERS: response_headers,
        RESPONSE_BODY: response_body

    }

def not_found_response(response_headers={}):

    response_body = {}

    return {

        RESPONSE_STATUS: http_status.NOT_FOUND,
        RESPONSE_HEADERS: response_headers,
        RESPONSE_BODY: response_body

    }

def bad_request_response(response_headers, error_code, docs_url):

    return send_error(http_status.BAD_REQUEST, response_headers, error_code, docs_url)

def invalid_patch_operation_response(response_headers, docs_url):

    error_code = INVALID_PATH_OPERATION
    
    return bad_request_response(response_headers, error_code, docs_url)

def unauthorized_response(response_headers, error_code, docs_url):

    return send_error(http_status.UNAUTHORIZED, response_headers, error_code, docs_url)

def send_error(response_status, response_headers, error_code, docs_url):

    response_body = {

        ERROR_CODE_FIELD:error_code,
        DOCS_URL_FIELD:docs_url

    }

    return {

        RESPONSE_STATUS: response_status,
        RESPONSE_HEADERS: response_headers,
        RESPONSE_BODY: response_body

    }