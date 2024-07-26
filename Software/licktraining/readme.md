# TODO for implementing lick training protocol

No camera recording is needed. Let's try daisy chaning the rigs. the implementation looks relatievly simple and we woudln't need to modify the serial communication code either. Let's just write the code for the main arduino for now and i will help you with the rest.

## prototyping

### Setting up prototyping environment and ardunio

1. Pinout for ardunio
   1. Lick sensor
   2. Push button
   3. LEDs needed for:
      1. Trial start and end
      2. Reward delivery

2. Session structure is one single 30 min long session
   1. Trial start
   2. Lick detection
   3. Reward delivery (i.e. solenoid opening)
   4. Trial end

3. Logic for the session
   1. Set up variables for the session. _Use the exact same varible names as in the `Rig.ino` code._
   2. Start the session with a push button
   3. in the loop:
      1. Wait for the lick
      2. Deliver the reward
      3. End the trial

#### Helpful code

1. Rig.ino code from this repo to define variables and functions
2. camera recording stuf from the context project: [ODU_GT.ino](https://github.com/GergelyTuri/context-project/blob/main/Arduino_code/ODU_GT/ODU_GT.ino)
