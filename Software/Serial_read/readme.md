# Pyhton scripts for data collection

## Overview

This folder contains two scripts which can perform data collection. The `py_arduino_serial.py` script is the one of main scripts which could be used if camera recording is not needed. The `py_arduino_serial_camera.py` script is a script which can be used when the White Matter cameras are connected to the recording setup and video footage is needed. The headers of these scripts also contain instructions on how to use them.

## Installation and usage

### Installation

1. A new Anaconda environment should be created with the packages listed in the `requirements.txt` file. The environment can be created with the following command: "conda create --name <env_name> --file requirements.txt"

2. arduino-cli is needed to set the trial settings in the GUI. This can be downloaded here: https://arduino.github.io/arduino-cli/0.35/installation/

### Usage

#### Run the GUI

1. Open an Anaconda terminal, activate the environment and navigate to the `tFC-rig` folder.
2. Run the following command to activate the GUI. 

```bash
python -m Software.Serial_read.py_arduino_serial_GUI
```
This will run the `py_arduino_serial_camera` script (behavior recording with camera) when you submit


#### Behavior recording without camera

1. Open an Anaconda terminal, activate the environment with "conda activate condaenv" and navigate to the `Software/Serial_read` folder. (View conda envs with "conda info --envs" and verify installed packages with "conda list")
2. Run the following command for further instructions:

```bash
python py_arduino_serial.py -h
```

#### Behavior recording with camera

1. Open an Anaconda terminal, activate the environment and navigate to the `tFC-rig` folder.
2. Run the following command for further instructions:

```bash
python -m Software.Serial_read.py_arduino_serial_camera.py -h
```

### Data

Data is saved in JSON format. The data is saved in a folder named `data` in the same directory as the script. The data is saved in a subfolder named. 