import contextlib
import os
import subprocess
import sys
import time
from collections.abc import Iterator

import pytest
import tango


@pytest.fixture(scope="session")
def pytango_db_dummy_device(session_pytango_db):
    yield from run_dummy_device(session_pytango_db)


@pytest.fixture(scope="session")
def tango_db_dummy_device(session_tango_db):
    yield from run_dummy_device(session_tango_db)


@pytest.fixture(scope="session")
def session_tango_db():
    """This fixture expects a "default" Tango database to be available at TANGO_HOST.

    It only returns the current TANGO_HOST variable.
    """
    yield tango.ApiUtil.get_env_var("TANGO_HOST")


def run_dummy_device(tango_host: str) -> Iterator[str]:
    """Start a dummy device server

    Add and start a dummy device server for tests.
    The server is deleted at the end.
    This function is meant to be used as a pytest fixture.
    """
    host, port = tango_host.split(":")
    db = tango.Database(host, port)
    try:
        device = "test/dummy/1"
        dev_info = tango.DbDevInfo()
        dev_info.name = device
        dev_info._class = "Dummy"
        server = "Dummy/1"
        dev_info.server = server
        db.add_server(dev_info.server, dev_info, with_dserver=True)

        # Start our dummy device
        path = os.path.abspath(os.path.dirname(__file__))
        dummy = subprocess.Popen(
            [sys.executable, f"{path}/dummy.py", "1"],
            stderr=subprocess.PIPE,
        )
        waited = 0
        dt = 0.3
        while True:
            time.sleep(dt)
            waited += dt
            if dummy.poll() is not None:
                stderr = dummy.stderr.read().decode()
                print("------------------STDERR------------------")
                print(stderr)
                print("------------------------------------------")
                raise RuntimeError(f"Dummy device stopped: {dummy.returncode}")
            try:
                proxy = tango.DeviceProxy(
                    f"tango://{tango_host}/{device}",
                    green_mode=tango.GreenMode.Synchronous,
                )
                proxy.ping()
                if proxy.read_attribute("State").value == tango.DevState.RUNNING:
                    break
            except tango.DevFailed as exc:
                if waited > 10:
                    raise RuntimeError("Tired of waiting for device proxy...") from exc
            except AssertionError:
                pass

        yield tango_host

    finally:
        # Clean up
        with contextlib.suppress(Exception):
            dummy.kill()
        with contextlib.suppress(Exception):
            db.delete_server(server)
