# conftest.py

import json
import os
import pytest


def pytest_sessionstart(session):
    with open("app/config/.env", mode="a") as f:
        f.write("\nYOUR_ENV=testing\n")
    
def pytest_sessionfinish(session, exitstatus):
    with open("app/config/.env", mode="r+") as f:
        f.flush()
        os.fsync(f.fileno())