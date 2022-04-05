# OpenOPAF
 Multimodal Learning Analytics system to provide automated feedback for oral presentations

Clone repository

git clone https://github.com/xaoch/OpenOPAF.git

Update repositories and install pip
    
    sudo apt-get update
    sudo apt-get install -y python3-pip
    sudo apt-get install python-venv
    sudo apt-get install curl
    pip3 install --upgrade pip
    cd OpenOPAF

Install Requirements

    sudo apt-get install libxml2-dev libxslt-dev python-dev
    sudo apt-get install libjpeg-dev zlib1g-dev 
    sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
    sudo apt-get install libffi-dev
    pip3 install -r requirements.txt

Install Mediapipe


export FLASK_APP=application
flask run
