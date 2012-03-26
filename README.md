Virtual Vision Simulator
========================
Version:

Author: Wiktor Starzyk

Supervisor: Dr. Faisal Qureshi


Introduction
============

Our Virtual Vision Simulator is a distributed, customizable simulator capable of 
simulating pedestrian traffic in a variety of 3D environments. Virtual cameras 
deployed in this synthetic environment generate synthetic imagery---boasting 
realistic lighting effects, shadows, etc.---using the state-of-the-art computer 
graphics techniques. Our virtual vision simulator is realized as a collection of 
modules that communicate with each other over the network. Consequently, we can 
deploy our simulator over a network of computers, allowing us to simulate much 
larger networks and much more complex scenes then is otherwise possible.

Please send us any comments or feedback about how to make our simulator better.
Your input is greatly appreciated.


Directory Structure
===================

The directory structure of this package is as follows:

    src/            The source code along with the 3 applications that can be 
                    executed
    dependencies/   The dependencies needed to run the simulator on windows 
    config/         Sample configuration files
    media/          3D models that make up the scene as well as the pedestrians


Installation
============

Windows
-------

Install all of the executables provided in the dependencies/windows folder.

NOTES:

- Make sure they all use the same version of python. (The version that comes with Panda3D is probably the best choice)

- You will probably have to copy cv.lib and cv.pyd from the OPENCV_DIR/Python2.6/Lib/site-packages folder to the folder where your version of python is located. 

    - OPENCV_DIR is your opencv directory. By default this is C:\OpenCV2.1 
    
    - PANDA3D_DIR is your panda3D directory. By default this is C:\Panda3D-1.7.2

- Make sure OPENCV_DIR\bin is added to your Path


Linux-Ubuntu
------------

The system is developed on Ubuntu 10.10 using packages from the Ubuntu 
repository. The following packages have to be installed:

- python2.6
- python-numpy 1.3.0
- python-matplotlib 0.99.3
- python-opencv 2.1.0
- panda3d 1.7.2 (Not in ubuntu repository)
- python-wxgtk2.8 2.8.11


Usage
=====

Simulator
---------

1. Go into the src folder.
2. Execute:

python 3D_Simulator.py [options]

Options:

    -d directory    Set the directory where the config files are located
    -p port         Set the port the server should run on (default is 9099)
    -a              Set the mode of the simulation controller to automatic
    -s              A Sync session is used to control the time
    -h              Print this help message and exit
    --debug         Print debug messages to the console
  

- Use the right arrow key to switch between different cameras
- Use the escape key to exit


Sync Client
-----------
Execute: python Sync_Client.py [options] ip_address:port ip_address:port ...

Where ip_address:port is replaced with the ip address and port of all the simulators

Options:

    --debug         Show debug messages


Sample Client
--------------

Execute: python sample_client.py [options]

Options:

    - p port        Set the port of the virtual world
    - a ip_address  Set the ip address of the virtual world
    - s             Save the images received from the server
    - h             Print this help message and exit
    --debug         Show debug messages


Contact Information
===================

Wiktor Starzyk        wiktor.starzyk@uoit.ca

Faisal Z. Qureshi     faisal.qureshi@uoit.ca

To report bugs or give feedback, please email Wiktor.


Copyright and License
=====================

Virtual Vision Simulator Copyright (c) 2011-2012 Wiktor Starzyk, Faisal Z. Qureshi

See license.txt for complete license.
