import re

def is_valid_uri(uri):

    if uri == None:
        return False    

    regex = r'^(\/[a-zA-Z0-9]{1,15})(\/[a-zA-Z0-9]{1,15})*$'
    
    return re.match(regex, uri) is not None

def is_valid_email(email):

    if email == None:
        return False    

    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    return re.match(regex, email) is not None

def is_valid_alias(alias):

    if alias == None:
        return False    

    regex = r'^[a-zA-Z0-9]{1,50}$'
    
    return re.match(regex, alias) is not None

def is_valid_token(token):

    if token == None:
        return False    

    regex = r'^[a-zA-Z0-9]{15}$'
    
    return re.match(regex, token) is not None

def is_valid_lambda_reference(lambda_ref):

    if lambda_ref == None:
        return False    

    regex = r'^[a-zA-Z0-9]{15}\.[a-zA-Z0-9]{15}$'
    
    return re.match(regex, lambda_ref) is not None
