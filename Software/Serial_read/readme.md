# Pyhton scripts for data collection

## Overview

This folder contains two scripts which can perform data collection. The `py_arduino_serial.py` script is the one of main scripts which could be used if camera recording is not needed. The `py_arduino_serial_camera.py` script is a script which can be used when the White Matter cameras are connected to the recording setup and video footage is needed. The headers of these scripts also contain instructions on how to use them.

## Installation

The installation and functionalities tested on PC with Windows 10 operating system. 

### Prerequisites

Before proceeding with the installation, ensure you have the following prerequisites installed on your system:

* Git: Needed to clone the repository from GitHub.
* Conda: Used to create and manage the project environment. You can use either Anaconda or Miniconda. If you don't have Conda installed, you can download it from the official Conda website.

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
    conda env create -f environment.yaml
    ```

3. Activate the Environment

    ```bash
    conda activate cued-fc
    ```

## Usage

### Behavior recording without camera

1. Open an Anaconda terminal, activate the environment and navigate to the `Software/Serial_read` folder.
2. Run the following command for further instructions:

    ```bash
    python py_arduino_serial.py -h
    ```

### Behavior recording with camera

1. Open an Anaconda terminal, activate the environment and navigate to the `Software/Serial_read` folder.
2. Run the following command for further instructions:

    ```bash
    python py_arduino_serial_camera.py -h
    ```

## Data

Data is saved in JSON format. The data is saved in a folder named `data` in the same directory as the script.
