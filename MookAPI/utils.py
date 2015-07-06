from flask import current_app

def is_local():
    return current_app.config['SERVER_TYPE'] == 'local'

def is_central():
    return not is_local()
