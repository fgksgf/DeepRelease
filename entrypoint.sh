#!/bin/bash

# if a command fails, exit
set -e
# treat unset variables as error
set -u
# if any command in a pipe fails, fail
set -o pipefail
# print all debug information
set -x

# This is populated by our secret from the Workflow file.
if [[ -z "$GITHUB_TOKEN" ]]; then
	echo "Set the GITHUB_TOKEN env variable."
	exit 1
fi

python /app/deeprelease.py "$@"