# Arduino software components for the trace-fear conditioning rig

Upload `Rig.ino` to the Arduino. This is the main program that runs the rig.

TODO:

* Block water delivery during the ITI!!!
* need two versions of this script: one for the training wihc has only the CS and the US tones and no air puff, and one which has the CS, the US and the air puff.
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
