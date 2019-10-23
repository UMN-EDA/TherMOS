#!/bin/bash
pip install virtualenv
echo "Setting up virtual environment"
virtualenv TherMOS
source TherMOS/bin/activate
which python
echo "Installing all the necessary pacakges"
pip3 install -r requirements.txt --no-cache-dir
