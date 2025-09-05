import random
import string
import time

DEFAULT_LENGHT = 15

def generate_unique_token(db_cursor, token_select):

    token = generate_token()

    tokens_exists = check_token_exists(db_cursor, token_select, token)
    while tokens_exists:

        time.sleep(200/1000)
        token = generate_token()
        tokens_exists = check_token_exists(db_cursor, token_select, token)

    return token

def check_token_exists(db_cursor, token_select, token):

    sql_param = (token, )
    db_cursor.execute(token_select, sql_param)
    (row_count,) = db_cursor.fetchone()
    
    return (row_count != 0)

def generate_token(length=DEFAULT_LENGHT):

    characters = string.ascii_letters + string.digits  # a-zA-Z0-9
    token = ''.join(random.choices(characters, k=length))
    return token
