import daemon

from connection_test import test_connection

with daemon.DaemonContext():
    test_connection()
