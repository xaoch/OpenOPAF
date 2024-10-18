![OpenOpafLogo](logo.png)

Open Sourced Multimodal Learning Analytics system to provide automated feedback for oral presentations.

### Hardware Requirements
Please check the [hardware section](hardware/hardware.md).

### OS Installation
Follow the instructions [here](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit#intro) 

### OpenOPAF System Installation

#### Clone this Github repository

    git clone https://github.com/xaoch/OpenOPAF.git

#### Update repositories and install pip
    
    sudo apt-get update
    sudo apt-get install -y python3-pip
    pip3 install --upgrade pip
    cd OpenOPAF

#### Install Requirements

    sudo apt-get install libxml2-dev libxslt-dev python-dev
    sudo apt-get install libjpeg-dev zlib1g-dev 
    sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
    sudo apt-get install libffi-dev
    pip3 install -r requirements.txt

#### Install Mediapipe

Follow the instructions [here](https://github.com/Melvinsajith/How-to-Install-Mediapipe-in-Jetson-Nano?tab=readme-ov-file). The process will take at least 2 hours.

#### Create Virtual Environment

    cd
    cd OpenOPAF
    sudo apt-get install python3-venv
    python3 -m venv --system-site-packages ooEnv

#### Create User Database

    python3 create_database.py

#### Run application to test it
    export FLASK_APP=application
    flask run --host=0.0.0.0

#### Connect from frontal machine

Get the IP from your device (or configure an alias in the router):
    
    ifconfig

In the browser of the machine that will project the interface and the virtual audience access, set the web browser to http://ipNumber:5000

If you are able to see the interface, the system is ready.  Kill the server to continue the installation.

### Run the appplication as a server

Install nano file editor and edit start.sh file
    
    sudo apt-get install nano
    nano start.sh

Change the following line in the start.sh file to reflect the location of the OpenOPAF directory.
    
    cd /home/augmented/OpenOPAF


Now create the systemd service file:
    
    sudo nano /lib/systemd/system/openopaf.service

The contents of the files should be:

    [Unit]
    Description=OpenOPAF Service
    After=network.target

    [Service]
    Type=idle
    Restart=on-failure
    User=<the user that you created at OS Installation>
    ExecStart=/path-to-OpenOPAF/start.sh

    [Install]
    WantedBy=multi-user.target

Now restart the demon to start and enable the service

    sudo systemctl daemon-reload
    sudo systemctl enable openopaf.service
    sudo systemctl start openopaf.service

Check if the service is active with:

    sudo systemctl status openopaf.service

Now every time that the Jetson Nano starts, it will start the OpenOPAF application after a few minutes.

You can install the Jetson Nano inside the case and use it without a monitor.

### Questions

If you have any questions or problems running the project, contact [xavier.ochoa@nyu.edu](mailto:xavier.ochoa@nyu.edu). 

