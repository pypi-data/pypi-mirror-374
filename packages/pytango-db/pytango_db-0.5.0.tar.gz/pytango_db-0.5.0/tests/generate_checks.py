"""
It seems the specification of the Tango database device is the C++
implementation.

This script is intended to be run against a C++ Tango database
and will run all the test commands and record the results. Then
it outputs a new test JSON file that can be run against another
Database implementation to check that it behaves the same.
"""

import json
import sys

import numpy as np
import tango

db = tango.Database()


for filename in sys.argv[1:]:
    with open(filename) as f:
        specs = json.load(f)

    for setup, check, cleanup in specs:
        for op in setup:
            db.command_inout(op["command"], op["argument"])
        for op in check:
            result = db.command_inout(op["command"], op["argument"])
            if result and len(result) == 2 and isinstance(result[0], np.ndarray):
                # This means the command returns e.g. a DevVarLongStringArray
                nums = result[0].tolist()
                data = result[1]
                op["result"] = nums, data
            else:
                op["result"] = result
        for op in cleanup:
            db.command_inout(op["command"], op["argument"])

    with open(filename, "w") as f:
        json.dump(specs, f, indent=4)
