__author__ = 'FredFourcade'

from connection_test import test_connection
import sys

do_reset = (sys.argv[1] == "reset") if len(sys.argv) > 1 else False

test_connection(do_reset)
