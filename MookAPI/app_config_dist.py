### Make a copy of this file called 'app_config.py'
### and change the values of the parameters to what you actually want.

## This salt is used to encrpyt data. Use http://randomkeygen.com/ to generate a random string.
password_salt = 'Find a nice salt to put here'

## Is this a central or a local server? Choose 'central' or 'local'. Default: 'central'
server_type = 'central'

## If this is a local server, uncomment the three properties below
## Give the address and credentials to the associated central server
# central_server_api_host = 'http://HOSTNAME:PORT/'
# central_server_api_key = '' # username, email or api key
# central_server_api_secret = '' # password or secret

## Specify a port other than default (optional)
## Default is 5001 if server_type == 'local', 5000 otherwise
# port = 5000
