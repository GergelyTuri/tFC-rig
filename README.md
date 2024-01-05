# tFC-rig

## Project Description

This repo contains hardware and software for a trace fear conditioning setup for headfixed rodents. The rig is designed to be modular and flexible, allowing for easy customization and expansion. The rig is controlled by Arduino microcontrollers equipeed with sensors. The conditioning is done by airpuffs directed toward the snout of the animals. Multiple Arduinos can be used in a daisy-chain manner which allows for paralel data collection of multiple mice. The rigs can also be equipped with video cameras (currently sourced from White Matter Inc.) to record the mice's facial expression throughout the training sessions. The data collection is controlled by a Python script that interfaces with the hardware via serial communication. The raw data is saved in JSON fromat.

## Repository Structure

The repository is organized as follows:

- The `Components` folder contains all the hardware designs for the rig. These include 3D printable parts, laser cuttable parts, and electronics schematics.
- the `Software` folder contains the Arduino code for the microcontrollers and the Python code for the data collection and analysis.

## Software Installation and usage

### Arduino

The Arduino code is written in C++ and can be compiled and uploaded to the microcontrollers using the Arduino IDE. Details of the code are provided in the `README.md` file under the `/Rig` folder.
