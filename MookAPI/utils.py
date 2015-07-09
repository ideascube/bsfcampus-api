from flask import current_app

def is_local():
    server_type = current_app.config.get('SERVER_TYPE', 'central')
    return server_type == 'local'

def is_central():
    return not is_local()
