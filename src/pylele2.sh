#!/usr/bin/env bash

LOG=pylele.log
time python3 -m cProfile -s tottime ./pylele2/all_assembly.py $@ > $LOG
head $LOG