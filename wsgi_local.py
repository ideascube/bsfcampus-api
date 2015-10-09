#!/usr/bin/python
import os, sys
import logging

activate_this = os.path.dirname(__file__) + '/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import settings_local
from MookAPI.api import create_app

application = create_app(settings_override=settings_local.Config)
