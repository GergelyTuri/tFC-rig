Pyhton script to read serial data from the Arduino and save it to a file.

The main script is `py_arduino_serial.py` should be run in the command line with the following command:
```bash
python py_arduino_serial.py -id mouse_id -c COM_port
```
where `mouse_id` is the ID of the mouse, `COM_port` is the COM port number of the Arduino.
The files will be saved in this folder for now. 

Use the `environment.yml` file located in this directory to create a conda environment with the required packages.
The main package is `pyserial`, which was installed with pip.

TODO:
* python script to parse the json files. 