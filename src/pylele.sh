#!/usr/bin/env bash

SCRIPT_DIR=`dirname $0`
LOG=pylele.log
time python3 -m cProfile -s tottime $SCRIPT_DIR/pylele/pylele1/main.py $@ > $LOG
head $LOG
