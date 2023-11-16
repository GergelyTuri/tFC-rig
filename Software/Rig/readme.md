# Arduino software components for the trace-fear conditioning rig

Upload `Rig.ino` to the Arduino. This is the main program that runs the rig.

TODO:

* Block water delivery during the ITI!!!
* Can we add a `MAX_REWARD_NUMBER` which sets the maximum number of water deliveries in a row? This is to prevent the animal from drinking too much water. Let's say we set it to 5, then the animal can only get 5 rewards in a row, then a few sec later it can get reawards again. 
* Documetation -- Doxygen?
* need a way to daisy chain multiple arduinos together and run the same script on then simultanelously.

## Rig Operation

The rig Arduino sketch works with the following stages:

1. Session has not started: rig is waiting for an input to start the session
    * No air puffs
    * No water available
    * No audio signals
1. Six trials with random inter-trial intervals: six trials, as defined in the top-level README, are run automatically by the rig, with a random inter-trial interval between each trial whose length is determined at runtime
1. Session has ended: rig does nothing, waiting for the Arduino to be stopped or reset
    * No air puffs
    * No water available
    * No audio signals

### Maximum Session Length

The maximum session length depends on:

* Trial duration
* Number of trials
* Maximum inter-trial interval length

With the following values originally described:

* 50 second trials
* 6 trials
* 5 minute maximum inter-trial interval

The maximum session length is 30 minutes. It is unlikely that all five inter-trial intervals, which are defined as a random value between 1 and 5 minutes, are exactly 5 minutes, and so the average session will be much shorter (the expected value is 17 minutes 30 seconds).

### Using the Rig for Training

It is valuable to habituate mice to the rig environment. There are a few variables that can be set in `trial.h` that may be useful to facilitate training (as well as debugging issues with the rig).

#### `WATER_REWARD_AVAILABLE`

Water is available to the mouse when certain conditions are met. It is then dispensed for a set time. Set this to `true` to enable water _when_ those conditions are met.

#### `USING_AUDITORY_CUES`

During each trial, a random auditory cue is played, and in the `CS+` case air puffs are sent towards the mouse. Set `USING_AUDITORY_CUES` to `false` to turn off _both_ the auditory signal playing, _and_ the air puffs.

#### `USING_AIR_PUFFS`

Set this to `false` to stop sending air puffs, whether or not we are using auditory cues (although if we are not using auditory cues, we will also not send air puffs based on the way the rig was designed).
