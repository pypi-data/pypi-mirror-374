# PyTango DatabaseDS

This is a "fork" of some internal code from pytango, that runs a Tango database device server. This
code was originally written by Tiago Coutinho. It uses sqlite for storing data and therefore
doesn't have any dependencies beyond python and PyTango.

It's currently under heavy development, but is pretty usable. Please report any problems!

The repo also contains (the beginnings of) a test suite that runs on both this device and a C++ database, for compatibility checking.

For discussion of the future of this device, see https://gitlab.com/tango-controls/pytango/-/issues/626


## Usage

Create a python environment and:

    $ pip install pytango-db
    $ TANGO_HOST=localhost:11000 PyDatabaseds 2

To work from source, check out this repo, create a python environment, and

    $ pip install -e .
    $ TANGO_HOST=localhost:11000 PyDatabaseds 2

Now you should be able to use any normal Tango stuff like Jive etc, as long as you set `TANGO_HOST=localhost:11000`. You can pick any port, but 10000 might be taken if you
already have a Tango installation locally.

The sqlite database is saved in the current working directory. It's possible to have
any number of databases running on the same host, with different ports, but be careful
about sharing the same database file, it will likely cause problems. You can configure
where it is stored by setting the environment variable `PYTANGO_DATABASE_NAME`.
For a pure in-memory db, use `:memory:`.

For debugging, you can enable logging:

    $ TANGO_HOST=localhost:11000 PyDatabaseds --logging_level=2 2

## pytest fixture

This project also includes two pytest fixtures to start a database:

- `pytango_db`, a function-scoped fixture (database is started and stopped after each test)
- `session_pytango_db`, a session-scoped fixture (database is started only once and stopped at the end of the test session)

To use one of this fixture in your project, add `pytango-db` to your tests requirements.

These fixtures will start a database on a random port and return the used `TANGO_HOST` variable,
that has been set in the environment.
The database runs in memory.

Note: if you are using a PyTango version older than 9.4, you will need to install the `psutil` package in order to use the fixtures.


## Use cases

- Local Tango development. Easy setup, possibility of having several databases and switching between them, etc.
- Continuous integration pipelines. Simpler setup, no service depencencies.
- Small lab setups?


## Drawbacks

- Still buggy
- Likely lower performance than the C++ device
- No concurrency (for now)


## Tests

The test suite is implemented as two very simple tests, one runs agains the pytango database device (provided by a fixture) and the other assumes there is a C++ database server running at the configured TANGO_HOST.

The test are run multiple times, with data provided by a JSON "spec". The spec contains separate definitions for each test run, e.g.

```
    {
        "name": "DbAddDevice",
        "check": [
            {
                "command": "DbAddDevice",
                "argument": [
                    "Dummy/1",
                    "test/dummy/2",
                    "Dummy"
                ]
            },
            {
                "command": "DbGetDeviceInfo",
                "argument": "test/dummy/2",
                "result": [
                    [
                        0,
                        0
                    ],
                    [
                        "test/dummy/2",
                        "nada",
                        "0",
                        "Dummy/1",
                        "nada",
                        "?",
                        "?",
                        "Dummy"
                    ]
                ]
            }
        ],
        "teardown": [
            {
                "command": "DbDeleteDevice",
                "argument": "test/dummy/2"
            }
        ]
    },

```
Here, the test is named after "DbAddDevice" since this is the command that is being tested.

The "check" section contains several command runs that will be executed on the database device under test. "command" and "argument" describe what to run, and the optional "result" describes the expected outcome. It will be compared against the actual result, to determine if the test was successful. Multiple commands are run in sequence.

The "teardown" section is optional, and will be run after the "check" section. If any modification is made to the database, this should be implemented in order to restore the database as far as possible, so that the test doesn't interfere with any other tests. At least in the case of the C++ database, we can't wipe it completely between tests so make sure to remove anything that was added by the test.

There is another optional section, "setup" that is run before "check" and can be used in order to create prerequisites for the checks.

The test may also contain a "comment" field for extra information, and a boolean "skip" field which if `true` will cause the test to be skipped. At the time of writing, many command tests are still empty "stubs", set to be skipped.


### Check

The check section also has a few more features:

`result` is a list or a string, depending on the type returned by the command. Items in the list are usually strings, but sometimes it can be useful to match them in a less exact way, when we only care about the "format" of the item:

* `null` means we don't care what the item is, it matches anything.
* `{"regexp": "a.*"}` is an example of a *regular expression* matching any string starting with "a".
* `{"timestamp": "%Y-%m-%d"}` matches any date in ISO format e.g. "2024-10-01". The matcher uses ordinary *strptime* syntax.

Ordinary string values may contain special *template* syntax e.g. `{name}`. before matching, it will be substituted with the name of the current test. This is useful in order to name things uniquely, which simplifies tracking down cases of stuff being left in the database by mistake (which should be cleaned up in the "teardown" step). For now, only "name" is available.

`result_slice` takes a list of arguments, corresponding to the python `slice` builtin; "start", "stop" and "step". Each is an integer or `None`. This can be used to get only part of the result, in case it contains things we aren't interested in.
