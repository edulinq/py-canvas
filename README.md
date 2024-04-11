# Canvas Tools

A suite of tools and Python interface for Instructure's Canvas LMS.

This project is not affiliated with Instructure.

Documentation Table of Contents:
 - [Installation](#installation)
 - [CLI Configuration](#cli-configuration)
 - [Usage Notes](#usage-notes)
    - [User Queries](#user-queries)
    - [Assignment Queries](#assignment-queries)
 - [CLI Tools](#cli-tools)
    - [List Course Users](#list-course-users)
    - [Fetch a Single User](#fetch-a-single-user)
    - [List Assignments](#list-assignments)
    - [Fetch a Single Assignment](#fetch-a-single-assignment)
    - [Fetch Assignment Scores](#fetch-assignment-scores)
    - [Upload Assignment Scores](#upload-assignment-scores)
    - [Upload Single Assignment Score](#upload-single-assignment-score)
    - [Fetch Gradebook](#fetch-gradebook)
    - [Upload Gradebook](#upload-gradebook)

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
 - `assignment` -- A query for the current assignment you are working on (does not always apply).

All these options can be set on the command line when invoking on of these tools, e.g.,:
```sh
python3 -m canvas.cli.user.list --server canvas.test.com --course 12345 --token abc123
```
However, it will generally be more convenient to hold these common options in a more reusable location.

There are several other places that config options can be specified,
with each later location overriding any earlier options.
Here are the places options can be specified in the order that they are checked:
 1. `./edq-canvas.json` -- If a `edq-canvas.json` exists in the current directory, it is loaded.
 2. `<platform-specific user config location>/edq-canvas.json` -- A directory which is considered the "proper" place to store user-related config for the platform you are using (according to [platformdirs](https://github.com/platformdirs/platformdirs)). Use `--help` to see the exact place in your specific case. This is a great place to store login credentials.
 3. Files specified by `--config` -- These files are loaded in the order they appear on the command-line.
 4. Bare Options -- Options specified directly like `--course` or `--token`. These will override all previous options.

Using the default config file (`edq-canvas.json`):
```sh
# `./edq-canvas.json` will be looked for and loaded if it exists.
python3 -m canvas.cli.user.list
```

Using a custom config file (`my_config.json`):
```sh
# `./my_config.json` will be used.
python3 -m canvas.cli.user.list --config my_config.json
```

A sample config file is provided in this repo at [sample-edq-canvas.json](./sample-edq-canvas.json).

For brevity, all future commands in this document will assume that all standard config options are in the default
config files (and thus will not need to be specified).

## Usage Notes

### User Queries

When a user is required, tools and API functions accept a "user query" (unless specified).
A user query is any object that can be used to uniquely identify a user.
Valid user queries are:
 - Canvas User ID (as an integer or string of digits)
 - Email
 - Full Name
 - "email (id)" where "email" is an email and "id" is a Canvas ID

User queries must be unambiguous within the pool of possible users (e.g., students in a course).
It is recommended to use an email or Canvas ID as a user query.
Resolving a user query that is not a Canvas ID will take longer,
because a list of users must be fetched from Canvas.

### Assignment Queries

When an assignment is required, tools and API functions accept an "assignment query" (unless specified).
An assignment query is any object that can be used to uniquely identify an assignment.
Valid assignment queries are:
 - Canvas Assignment ID (as an integer or string of digits)
 - Full Name
 - "name (id)" where "name" is a full assignment name and "id" is a Canvas ID

Assignment queries must be unambiguous within the pool of possible assignments (e.g., assignments in a course).
Resolving an assignment query that is not a Canvas ID will take longer,
because a list of assignments must be fetched from Canvas.

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

### Fetch a Single User

To fetch information about a single course user, use the `canvas.cli.user.fetch` tool.
For example:
```
python3 -m canvas.cli.user.fetch 12345
```

### List Assignments

Course assignments can be listed using the `canvas.cli.assignment.list` tool.
For example:
```
python3 -m canvas.cli.assignment.list
```

To list each assignment as a tab-separated row, use the `-t` / `--table` option:
```
python3 -m canvas.cli.assignment.list --table
```

### Fetch a Single Assignment

Fetch information about a single assignment using the `canvas.cli.assignment.fetch` tool.
For example:
```
python3 -m canvas.cli.assignment.fetch 123456

python3 -m canvas.cli.assignment.fetch 'My Assignment'
```

### Fetch Assignment Scores

To fetch the scores for a specific assignment, use the `canvas.cli.assignment.fetch-scores` tool.
For example:
```
python3 -m canvas.cli.assignment.fetch-scores 123456

python3 -m canvas.cli.assignment.fetch-scores 'My Assignment'
```

The student's email and score will be written to stdout as a tab-separated row.

### Upload Assignment Scores

Uploading scores for an assignment can be done with the `canvas.cli.assignment.upload-scores` tool:
```
python3 -m canvas.cli.assignment.upload-scores <assignment query> <path>
```

Where `<path>` points to a tab-separated file where each row has 2-3 columns: email, score, and comment (optional).
Each row does not need to have the same length (i.e., some rows can have comments where others do not).
Empty comments are ignored.

The `--skip-rows` argument can be used to skip a specified number of header rows.
For example:
```
python3 -m canvas.cli.assignment.upload-scores 'My Assignment' grades.txt --skip-rows 1
```

Where `grades.txt` looks like:
```
user	score	comment?
1001	75
alice@uni.edu	100	Great Job!
```

### Upload Single Assignment Score

To upload just one assignment score without a file, you can use the `canvas.cli.assignment.upload-score` tool:
```
python3 -m canvas.cli.assignment.upload-score <assignment query> <user query> <score> [comment]
```

Note that the comment is optional.

For example:
```
python3 -m canvas.cli.assignment.upload-score 'My Assignment' alice@uni.edu 100 'Great Job!'
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

By default, assignments and users without submissions will be pruned.
They can be included by using the respective `--include-empty-assignments` and `--include-empty-users` flags.

For example, you can write a gradebook with all assignments and users to `grades.txt` using the following command:
```
python3 -m canvas.cli.gradebook.fetch --include-empty-assignments --include-empty-users > grades.txt
```

### Upload Gradebook

To upload a gradebook, use the `canvas.cli.gradebook.upload` tool:
```
python3 -m canvas.cli.gradebook.upload <path>
```

Where `<path>` points to a gradebook file that has the same format as the output from `canvas.cli.gradebook.fetch`:
a tab-separated file with users down the rows and assignments along the columns.
The first column is user queries where the first cell is ignored,
the first row is assignment queries where the first cell is ignored,
and the remaining cells are the associated scores.
Any number of users and assignments can be specified as long as they exist in the course.
Empty cells will not be uploaded.

A gradebook file can look like:
```
user	98765	Assignment 2
1001	1	2
alice@uni.edu	3	
```
