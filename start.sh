#!/bin/sh
cd /home/augmented/Code/OpenOPAF
. opaf/bin/activate
sleep 5
export FLASK_APP=application
export DISPLAY=:0
flask run --host=0.0.0.0