NOTE: 
It is best to not have any version of python installed. This can affect where
the libraries need to run the virtual vision simulator will be installed.

When installing the python libraries, make sure that the installer finds the 
version of python that comes with Panda3D.

Go into the dependencies/windows folder. This folder includes all of the necessary libraries needed to run the virtual vision simulator.
                        
Install Panda3D-1.7.2 which comes with python 2.6. You can use all of the default values.
                       
Install numpy-1.6.0-win32-superpack-python2.6.
                        
Install wxPython2.8-win32-unicode-2.8.12.0-py26.
                        
Install matplotlib-1.0.1.win32-py.2.6.
                        
Install OpenCV-2.1.0-win32-vs2008.

Copy OPENCV_DIR\Python2.6\Lib\site-packages\cv.lib and OPENCV_DIR\Python2.6\Lib\site-packages\cv.pyd to PANDA3D_DIR\python\Lib\site-packages folder. (OPENCV_DIR and PANDA3D_DIR are the directories where OpenCV and Panda3D were installed)

Your installation is now complete! Go to the Usage section to see how to run the virtual vision simulator.