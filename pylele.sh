#!/usr/bin/env bash

LOG=pylele.log
time python3 -m cProfile -s tottime ./pylele.py $@ > $LOG
head $LOG
