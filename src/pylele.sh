#!/usr/bin/env bash

LOG=pylele.log
time python3 -m cProfile -s tottime ./pylele/pylele1/pylele.py $@ > $LOG
head $LOG
