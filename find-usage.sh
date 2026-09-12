#!/bin/sh
# List files containing the given text, skipping the git directory.

find . -path ./.git -prune -o -type f -print0 | xargs -0 grep -lI "$1"
