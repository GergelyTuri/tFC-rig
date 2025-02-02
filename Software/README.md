# Arduino Sketch for Performing Trace-Fear Conditioning

Graphical representation of the trace-fear conditioning protocol:

![Trace-fear conditioning protocol](./figs/tf_protocol.PNG)

### Hardware Components

The Arduino controls the following components:

- 2 speakers which play two different tones (`CS+` and `CS-`)
- One water solenoid valve which delivers a water drop throughout the trial
- One air solenoid valve which delivers a series (5x) of airpuffs at the end of `CS+` the trial 
- Lickport which delivers a water drop when the mouse licks it

### The arduino records the following events:

- Times the mouse licks the lickometer

The trials make up blocks. 
One block consists of 3 trials of `CS+` and 3 trials of `CS-` in random order with random inter trial intervals (ITIs) between them.

### Development Environment

The code was developed in a conda environment. To create it please follow the instructions in the README.md file in the root directory.
