# Canvas Tools

A suite of tools and Python interface for Instructure's Canvas LMS.

This project is not affiliated with Instructure.

Documentation Table of Contents:
 - [Installation](#installation)
 - [CLI Configuration](#cli-configuration)
 - [CLI Tools](#cli-tools)
    - [List Course Users](#list-course-users)
    - [Fetch Gradebook](#fetch-gradebook)
    - [Fetch Assignment Scores](#fetch-assignment-scores)

## Installation

The project (tools and API) can be installed from PyPi with:
```
pip install edq-canvas
```

Standard Python requirements are listed in `pyproject.toml`.
The project and Python dependencies can be installed from source with:
```
pip3 install .
```

### CLI Configuration

Before discussing specific tools, you should know some general information about
configuring and sending options to each CLI tool.

To know who you are and what you are working on the package needs a few configuration options:
 - `server` -- The Canvas server to connect to.
 - `course` -- The Canvas ID for the course you are working with.
 - `token` -- Your Canvas API token (see the [Canvas documentation](https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89).
 - `assignment` -- The Canvas ID for the current assignment you are working on (does not always apply).

All these options can be set on the command line when invoking on of these tools, e.g.,:
```sh
python3 -m canvas.cli.user.list --server canvas.test.com --course 12345 --token abc123
```
However, it will generally be more convenient to hold these common options in a more reusable location.

There are several other places that config options can be specified,
with each later location overriding any earlier options.
Here are the places options can be specified in the order that they are checked:
 1. `./config.json` -- If a `config.json` exists in the current directory, it is loaded.
 2. `<platform-specific user config location>/edq-canvas.json` -- A directory which is considered the "proper" place to store user-related config for the platform you are using (according to [platformdirs](https://github.com/platformdirs/platformdirs)). Use `--help` to see the exact place in your specific case. This is a great place to store login credentials.
 3. Files specified by `--config` -- These files are loaded in the order they appear on the command-line.
 4. Bare Options -- Options specified directly like `--course` or `--token`. These will override all previous options.

Using the default config file (`config.json`):
```sh
# `./config.json` will be looked for and loaded if it exists.
python3 -m canvas.cli.user.list
```

Using a custom config file (`my_config.json`):
```sh
# `./my_config.json` will be used.
python3 -m canvas.cli.user.list --config my_config.json
```

For brevity, all future commands in this document will assume that all standard config options are in the default
config files (and thus will not need to be specified).

## CLI Tools

All CLI tools can be invoked with `-h` / `--help` to see the full usage and all options.

### List Course Users

Course users can be listed using the `canvas.cli.user.list` tool.
For example:
```
python3 -m canvas.cli.user.list
```

To list each user as a tab-separated row, use the `-t` / `--table` option:
```
python3 -m canvas.cli.user.list --table
```

### Fetch Gradebook

To fetch the full gradebook for a course, use the `canvas.cli.gradebook.fetch` tool.
For example:
```
python3 -m canvas.cli.gradebook.fetch
```

A gradebook will be written to stdout as a tab-separated file.
To output the gradebook to a file, you can redirect stdout to a file.
Expect this command to take a few minutes for larger classes.

You can limit to gradebook to only specific students by specifying their IDs on the command line.
Any number of students can be specified.
```
python3 -m canvas.cli.gradebook.fetch 12345 67890
```

To prune assignments that have no submissions with the `--skip-empty-assignments` flag,
and prune users with no submissions using the `--skip-empty-users` flag.

For example, you can write a gradebook with pruned assignments and users to `grades.txt` using the following command:
```
python3 -m canvas.cli.gradebook.fetch --skip-empty-assignments --skip-empty-users > grades.txt
```

### Fetch Assignment Scores

To fetch the scores for a specific assignment, use the `canvas.cli.assignment.fetch-scores` tool.
For example:
```
python3 -m canvas.cli.assignment.fetch-scores --assignment 123456
```

The student's email and score will be written to stdout as a tab-separated row.