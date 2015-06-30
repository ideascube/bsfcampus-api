#!/usr/bin/python
import os, sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import settings_central
from MookAPI import create_app

application = create_app(settings_override=settings_central.Config)
