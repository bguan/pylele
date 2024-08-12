#!/usr/bin/env bash

LOG=pylele.log
time python3 -m cProfile -s tottime ./pylele2/pylele_bottom_assembly.py $@ > $LOG
head $LOG
