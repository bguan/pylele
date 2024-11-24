#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
time python3 $SCRIPT_DIR/pylele/test.py $@
