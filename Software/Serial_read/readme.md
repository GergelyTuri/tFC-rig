# Pyhton scripts for data collection

## Overview

This folder contains two scripts which can perform data collection. The `py_arduino_serial.py` script is the one of main scripts which could be used if camera recording is not needed. The `py_arduino_serial_camera.py` script is a script which can be used when the White Matter cameras are connected to the recording setup and video footage is needed. The headers of these scripts also contain instructions on how to use them.

## Installation and usage

### Installation

1. A new Anaconda environment should be created with the packages listed in the `requirements.txt` file. The environment can be created with the following command:

### Usage

#### Behavior recording without camera

1. Open an Anaconda terminal, activate the environment and navigate to the `Software/Serial_read` folder.
2. Run the following command for further instructions:

```bash
python py_arduino_serial.py -h
```

#### Behavior recording with camera

1. Open an Anaconda terminal, activate the environment and navigate to the `Software/Serial_read` folder.
2. Run the following command for further instructions:

```bash
python py_arduino_serial_camera.py -h
```

### Data

Data is saved in JSON format. The data is saved in a folder named `data` in the same directory as the script. The data is saved in a subfolder named. 