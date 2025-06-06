#!/bin/sh
# Flash release script: update the version string in `config/version.py`
# and in `package.json`
#
# Usage:
# - commit all the changes you want to release to whatever branch
# - launch this script from the base dir of the project
# - commit all changes and ship
#
# To increment the mayor.minor part, tag a commit as in:
#   git tag -a -m 'start of 1.0 version' 2.0 HEAD
#
# Copyright (C) 2025 Paolo Greppi

set -e

GIT_MAJOR=$(git describe --long | cut -d- -f1 | cut -d. -f1)
GIT_MINOR=$(git describe --long | cut -d- -f1 | cut -d. -f2)
GIT_PATCH=$(git describe --long | cut -d- -f2)
GIT_COMMIT=$(git log -n1 --pretty='%h')
GIT_VERSION="$GIT_MAJOR.$GIT_MINOR.$GIT_PATCH+$GIT_COMMIT"

echo "__version__ = \"$GIT_VERSION\"" > config/version.py

sed -i "s/\"version\": \".*\"/\"version\": \"$GIT_VERSION\"/g" frontend/package.json

echo "$GIT_VERSION"
