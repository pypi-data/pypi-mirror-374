"""
Tests checking DB device commands.
The tests are defined under specs/ as JSON files. They are all
run against both the standard C++ DB device and the PyTango
implementation in this repo, the idea being to ensure they behave
the same.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from random import shuffle

import numpy as np
import pytest
import tango


def validate_spec(spec):
    "Check that an operation is well formed, no misspelled keys etc."
    # TODO maybe just make a json schema instead
    assert (
        spec.keys() - {"name", "skip", "comment", "setup", "check", "teardown"} == set()
    ), "Malformed spec: unknown key"


# Load the test specifications from JSON
command_specs = []
for file in Path("tests/specs").glob("*.json"):
    with file.open() as f:
        try:
            specs = json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse test spec {file}: {e}") from e
    for i, spec in enumerate(specs):
        validate_spec(spec)
        command_specs.append(pytest.param(spec, id=f"{file.name}:{i}:{spec['name']}"))
# The order of the tests should never matter, so let's run them in a random order
# If we see random failures, it means some tests aren't cleaning up properly
shuffle(command_specs)


ALLOWED_CHECK_KEYS = {"command", "argument", "result", "raises", "result_slice"}


def validate_op(op):
    assert op.keys() - ALLOWED_CHECK_KEYS == set(), "Malformed operation: unknown key"


class Anything:
    "Object that's equal to everything. For matching e.g. timestamps we can't control"

    # TODO would be nice to have a way to check format etc

    def __eq__(self, other):
        return True


class RegExp:
    def __init__(self, pattern: str):
        self.regexp = re.compile(pattern)

    def __eq__(self, other: str):
        return bool(self.regexp.match(other))

    def __repr__(self):
        return f"RegExp({self.regexp})"


class Timestamp:
    def __init__(self, pattern: str):
        self.pattern = pattern

    def __eq__(self, other: str):
        try:
            datetime.strptime(other, self.pattern)
            return True
        except ValueError:
            return False

    def __repr__(self):
        return f"Timestamp({self.pattern})"


def activate_value(value, **kwargs):
    if isinstance(value, dict):
        if "regexp" in value:
            return RegExp(value["regexp"])
        if "timestamp" in value:
            return Timestamp(value["timestamp"])
        else:
            raise ValueError(f"Bad matcher {value}!")
    if value is None:
        return Anything()
    if isinstance(value, str):
        return value.format(**kwargs)
    raise ValueError(f"Bad value {value}!")


def template_value(argument, **kwargs):
    """
    Replace e.g. {name} with given values.
    It can be very helpful to "tag" e.g. property names with the test
    they are used in, when tracking down things that haven't been cleaned
    up properly.
    """
    if argument is None:
        return None
    if isinstance(argument, list):
        # Can be either a list of strings, or a list containing a
        # list of integers and a list of strings.
        if len(argument) == 2 and isinstance(argument[0], list):
            return [
                argument[0],
                [activate_value(item, **kwargs) for item in argument[1]],
            ]
        else:
            return [activate_value(item, **kwargs) for item in argument]
    else:
        return activate_value(argument, **kwargs)
    return argument


def run_database_test(
    name: str, comment=None, setup=None, check=None, teardown=None, skip=False
):
    "Perform a test from the given specification"
    if teardown is None:
        teardown = []
    if check is None:
        check = []
    if setup is None:
        setup = []
    db = tango.Database()
    if skip:
        pytest.skip("Configured to be skipped")
    try:
        if setup:
            print("=== SETUP ===")
        for op in setup:
            # Setup commands, to get the DB into some specific state
            validate_op(op)
            argument = template_value(op.get("argument"), name=name)
            print("Command:", op["command"], argument)
            db.command_inout(op["command"], argument)
        if check:
            print("=== CHECK ===")
        for op in check:
            # Check conditions
            validate_op(op)
            if "raises" in op:
                # Operation is expected to raise an exception
                with pytest.raises(Exception) as e_info:
                    argument = template_value(op.get("argument"), name=name)
                    print("Command:", op["command"], argument)
                    db.command_inout(op["command"], argument, "raising", op["raises"])
                    assert e_info.value.__name__ == op["raises"]
            else:
                argument = template_value(op.get("argument"), name=name)
                print("Command:", op["command"], argument)
                result = db.command_inout(op["command"], argument)
                if "result_slice" in op:
                    # Enable only checking a part of the result
                    # Useful for "hist" commands where we need to ignore older entries
                    result = result[slice(*op["result_slice"])]
                if op.get("result") is not None:
                    print("Result:", result)
                    expected = template_value(op["result"], name=name)
                    if len(result) == 2 and isinstance(result[0], np.ndarray):
                        # This means the command returns e.g. a DevVarLongStringArray
                        nums = result[0].tolist()
                        data = result[1]
                        assert [nums, data] == expected
                    else:
                        assert result == expected
                else:
                    assert result is None, "Did not expect a result!"
    finally:
        if teardown:
            print("=== TEARDOWN ===")
        for op in teardown:
            # Teardown commands, to restore the DB
            validate_op(op)
            try:
                argument = template_value(op.get("argument"), name=name)
                print("Command:", op["command"], argument)
                db.command_inout(op["command"], argument)
            except tango.DevFailed as e:
                print(e)
                raise


@pytest.mark.tangodb
@pytest.mark.parametrize("spec", command_specs)
def test_external_database_device(spec, tango_db_dummy_device):
    "Run the tests with an externally provided tango DB"
    run_database_test(**spec)


@pytest.mark.parametrize("spec", command_specs)
def test_pytango_database_device(spec, pytango_db_dummy_device):
    "Run the tests with PyTango database device"
    run_database_test(**spec)
