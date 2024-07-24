#!/usr/bin/env bash

# ubuntu dependencies
sudo apt update 
sudo apt install python3-pip libgl1 -y

# install fonts
sudo apt install ttf-mscorefonts-installer -y
sudo fc-cache -f

# update pip
python3 -m pip install --upgrade pip
# python dependencies
pip install -r requirements.txt