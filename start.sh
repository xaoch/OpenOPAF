#!/bin/sh
cd /home/augmented/Code/OpenOPAF
. opaf/bin/activate
export FLASK_APP=application
flask run --host=0.0.0.0 --port=80