#!/usr/bin/env bash

LOG=pylele.log
time python3 -m cProfile -s tottime ./pylele/pylele1/main.py $@ > $LOG
head $LOG
