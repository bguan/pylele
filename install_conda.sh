#!/usr/bin/env bash


# CONDA_REPO=https://repo.anaconda.com/archive/
# CONDA=Anaconda3-2024.02-1-Linux-x86_64.sh # based on python 3.11
# CONDA_BIN_DIR=~/anaconda3/bin

CONDA_REPO=https://repo.anaconda.com/miniconda/
CONDA=Miniconda3-py311_24.7.1-0-Linux-x86_64.sh # miniconda python 3.11
CONDA_BIN_DIR=~/miniconda3/bin

PYTHON=$CONDA_BIN_DIR/python


# get and install conda
wget ${CONDA_REPO}${CONDA}
chmod +x $CONDA
./$CONDA -b

# check python version
$PYTHON --version

# get pip
# GET_PIP=get-pip.py
# wget https://bootstrap.pypa.io/$GET_PIP
# $PYTHON $GET_PIP

# install pip through conda
conda install pip

# install pip requirements
$PYTHON -m pip install -r requirements.txt

# install requirements with conda or pip
# https://stackoverflow.com/questions/65753317/strategies-to-convert-requirements-txt-to-a-conda-environment-file
# while read requirement; do conda install --yes $requirement || pip install $requirement; done < requirements.txt
