import endpointer.regexp as ep_regexp

SESSION_TOKEN_HEADER = 'com-endpointer-session-token'
SESSION_TOKEN_ENV = 'EP_SESSION_TOKEN'

INVALID_SESSION_TOKEN = 'invalid-session-token'

DOCS_URL = 'https://endpointer.com'

def get_session_token(request_headers):
    
    session_token = request_headers.get(SESSION_TOKEN_HEADER)
    
    no_session_token = session_token is None
    if no_session_token:
        return None
    
    is_invalid = not ep_regexp.is_valid_token(session_token)
    if is_invalid:
        return None
    
    return session_token
