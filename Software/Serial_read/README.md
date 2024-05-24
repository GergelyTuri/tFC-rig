# Pyhton scripts for data collection

## Overview

This folder contains two scripts which can perform data collection. The `py_arduino_serial.py` script is the one of main scripts which could be used if camera recording is not needed. The `py_arduino_serial_camera.py` script is a script which can be used when the White Matter cameras are connected to the recording setup and video footage is needed. The headers of these scripts also contain instructions on how to use them.

## Installation

The installation and functionalities tested on PC with Windows 10 operating system. 

### Prerequisites

Before proceeding with the installation, ensure you have the following prerequisites installed on your system:

* Git: Needed to clone the repository from GitHub.
* Conda: Used to create and manage the project environment. You can use either Anaconda or Miniconda. If you don't have Conda installed, you can download it from the official Conda website.
* Arduino-cli: Needed to update arduino files. This can be downloaded here: https://arduino.github.io/arduino-cli/0.35/installation/

### Installation Steps

Follow these steps to set up the project environment and start using the package:

1. Clone the GitHub Repository
First, clone the repository containing the project to your local machine. Open a terminal or command prompt and run the following command, replacing [Your-Repo-URL] with the URL of your GitHub repository:

    ``` bash
    git clone https://github.com/GergelyTuri/tFC-rig.git
    cd [Your-Repo-name/Software]
    ```

2. Create the Conda Environment

    ```bash
    conda env create -f environment.yml
    ```

3. Activate the Environment

    ```bash
    conda activate cued-fc
    ```
    
4. Install Arduino-cli at https://arduino.github.io/arduino-cli/0.35/installation/. 
Install it in a directory already in your PATH or add the Arduino CLI installation path to your PATH environment variable. This ensures your system will be able to detect and use it.

Environment Variables
Windows:
a. Go to your  windows search bar at the bottom of the screen and look up "Edit the system environment variables"
b. Click "Environment variables", then click edit "Path" variable under "user variables". 
c. Simply add the path to your arduino-cli software, save, and restart your vscode.

Mac:
a. Edit one of these files: ~/.bashrc or ~/.bash_profile.
b. Enter the file with nano ~/.bashrc, or through your file explorer
c. either add this new line or append the new path to your PATH variable:
            export PATH="{arduino-cli path}"
d. Save the changes (in nano this is ctrl-0, then hit enter) and restart vscode

## Usage

### GUI

1. Open an Anaconda terminal, activate the environment and navigate to the `tFC-rig` folder.
2. Run the following command to activate the GUI. 

```bash
python -m Software.Serial_read.py_arduino_serial_GUI
```
This will run the `py_arduino_serial_camera` script (behavior recording with camera) when you submit


### Behavior recording without camera

1. Open an Anaconda terminal, activate the environment with "conda activate condaenv" and navigate to the `Software/Serial_read` folder. (View conda envs with "conda info --envs" and verify installed packages with "conda list")
2. Run the following command for further instructions:

    ```bash
    python py_arduino_serial.py -h
    ```

### Behavior recording with camera

1. Open an Anaconda terminal, activate the environment and navigate to the `tFC-rig` folder.
2. Run the following command for further instructions:

    ```bash
    python -m Software.Serial_read.py_arduino_serial_camera.py -h
    ```


## Data

Data is saved in JSON format. The data is saved in a folder named `data` in the same directory as the script.
