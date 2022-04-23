# [Repos](http://repos.hive.pt)

Modular repository management system, should be able to accommodate multiple layouts
or types of packages to server Hive Solutions purposes.

## Features

* Agnostic management of packages
* CDN based package management
* Integration with S3 compatible storage engines

## Configuration

The most relevant configuration variables for Repos are:

| Name              | Type  | Description                                                          |
| ----------------- | ----- | -------------------------------------------------------------------- |
| **REPO_PATH**     | `str` | May be used to define the local file system directory for storage.   |
| **REPO_USERNAME** | `str` | If used limits the access to artifacts for only authenticated users. |
| **REPO_PASSWORD** | `str` | Defines the password to be used for access to the artifacts.         |

## License

Repos is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![Build Status](https://github.com/hivesolutions/repos/workflows/Main%20Workflow/badge.svg)](https://github.com/hivesolutions/repos/actions)
[![PyPi Status](https://img.shields.io/pypi/v/repos.svg)](https://pypi.python.org/pypi/repos)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/)
