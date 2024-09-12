#!/usr/bin/env bash


CONDA=Anaconda3-2024.02-1-Linux-x86_64.sh # based on python 3.11
CONDA_BIN_DIR=~/anaconda3/bin
GET_PIP=get-pip.py
PYTHON=$CONDA_BIN_DIR/python

# get and install conda
wget https://repo.anaconda.com/archive/$CONDA
chmod +x $CONDA
./$CONDA -y

# check python version
$PYTHON --version

# get pip
wget https://bootstrap.pypa.io/$GET_PIP
$PYTHON $GET_PIP

# install pip requirements
$PYTHON -m pip install -r requirements.txt