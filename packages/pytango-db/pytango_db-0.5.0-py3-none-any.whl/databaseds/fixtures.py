"""This module defines some pytest fixtures

The module is registered as a pytest plugin, meaning fixtures will be automatically
available when installed.
"""

import contextlib
import os
import subprocess
import time
from collections.abc import Iterator
from unittest import mock

import pytest
import tango

try:
    from tango.test_context import get_server_port_via_pid
except ImportError:
    from .compatibility import get_server_port_via_pid


@pytest.fixture
def pytango_db():
    """Function-scoped fixture to start the Python Tango Database device server on a random port.

    Set TANGO_HOST variable in the environment and return its value.
    """
    yield from run_pytango_db()


@pytest.fixture(scope="session")
def session_pytango_db():
    """Session-scoped fixture to start the Python Tango Database device server on a random port.

    Set TANGO_HOST variable in the environment and return its value.
    """
    yield from run_pytango_db()


def run_pytango_db() -> Iterator[str]:
    """Start the Python Tango Database device server on a random port.

    Set TANGO_HOST variable in the environment and yield its value.
    This function is meant to be used as a pytest fixture.
    """
    # Copy the current env to preserve the PATH
    # Passing env to subprocess overwrites the complete env.
    env = os.environ.copy()
    # Don't write to disk
    env["PYTANGO_DATABASE_NAME"] = ":memory:"
    host = "127.0.0.1"
    try:
        # Use port 0 to let the OS allocate a free port
        databaseds = subprocess.Popen(
            ["PyDatabaseds", "--port", "0", "--host", host, "2"],
            stderr=subprocess.PIPE,
            env=env,
        )
        databaseds.poll()
        port = get_server_port_via_pid(databaseds.pid, host)
        waited = 0
        dt = 0.3
        while True:
            time.sleep(dt)
            waited += dt
            if databaseds.poll() is not None:
                stderr = databaseds.stderr.read().decode()
                print("------------------STDERR------------------")
                print(stderr)
                print("------------------------------------------")
                raise RuntimeError(f"PyDatabaseds stopped: {databaseds.returncode}")
            try:
                db = tango.Database(host, port)
                db.get_info()
                break
            except tango.DevFailed as exc:
                if waited > 10:
                    raise RuntimeError(
                        f"Tired of waiting for database...{exc}"
                    ) from exc
        tango_host = f"{host}:{port}"
        print(f"Python Databaseds started on {tango_host}")
        with mock.patch.dict(os.environ, {"TANGO_HOST": tango_host}):
            yield tango_host
    finally:
        with contextlib.suppress(Exception):
            databaseds.kill()
