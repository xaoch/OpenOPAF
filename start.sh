#!/bin/sh
cd /home/augmented/OpenOPAF
. ooEnv/bin/activate
sleep 5
export FLASK_APP=application
export DISPLAY=:0
python3 -m flask run --host=0.0.0.0