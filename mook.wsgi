#!/usr/bin/python
import os, sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MookAPI import app as application
