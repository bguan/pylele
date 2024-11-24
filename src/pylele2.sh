#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
LOG=pylele.log
time python3 -m cProfile -s tottime $SCRIPT_DIR/pylele/pylele2/all_assembly.py $@ > $LOG
head $LOG
