#!/bin/sh
cd /home/augmented/Code/OpenOPAF
. opaf/bin/activate
export FLASK_APP=application
export DISPLAY=:0
python -m sounddevice
flask run --host=0.0.0.0