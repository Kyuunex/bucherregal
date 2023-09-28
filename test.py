#!/usr/bin/env python3
import os

os.environ["BUCHERREGAL_SQLITE_FILE"] = os.path.expanduser("~") + "/Documents/bucherregal.sqlite3"

from bucherregal import app as application

application.run(
    host='127.0.0.1',
    port=8089,
    debug=True
)
