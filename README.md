# QuickBot_local
This is the code that runs on your local computer that can interface with the QuickBot.

## Overview
This code will establish socket (UDP) connection with the QuickBot to give the robot commands.

## Installation
Clone the repo into some directory:

    git clone https://bitbucket.org/rowoflo/quickbot_local.git

## Running
Change into working directory:

    cd quickbot_local

Launch code with BBB on QuickBot IP address (example IP address shown):

    ./joystickControl.py 192.168.1.101

## Notes
The the joystickControl.py script only works with 32-bit python and does not work with 64-bit python. Notice that the shebang line in the script calls a 32-bit python interpreter. This line may need to be adjusted for your python installation.
