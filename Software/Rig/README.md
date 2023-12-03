# Arduino software components for the trace-fear conditioning rig

Upload `Rig.ino` to the Arduino. This is the main program that runs the rig.

TODO:

* Block water delivery during the ITI!!!
* Documetation -- Doxygen?
* Need a way to daisy chain multiple arduinos together and run the same script on then simultanelously.
* Let's reset the arduino every time before the session starts to make sure everything is in a good state. see [this](https://arduinogetstarted.com/faq/how-to-reset-arduino-by-programming)
this does not seem to work. I think i don't get the logic. it resets the arduino but then it does not run the setup function again. i also tried an implementation based on [watchdog timer](https://chat.openai.com/share/15c3ecfc-6d2a-4661-86cb-448098e0bf0f) but that did not work either. it resets the arduino but then it does not run the setup function again. Maybe using the reset pin would work. 
* let's also stop running the script when `KeyboardInterrupt` is raised in the  `py_arduion_serial.py` script. 

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

### Daisy-Chaining Rigs

The rig Arduino sketch has been written to be run in two overall modes:

* Primary
* Secondary

When running a `primary` rig, all peripherals are controlled as described elsewhere, _and_ a "secondary" signal is sent on `PIN_SECONDARY` when:

* The session starts (the button connected to the primary rig is pressed)
* Each trial starts (each inter-trial interval ends)

When running a `secondary` rig, the `PIN_BUTTON` is not connected, and instead `PIN_SECONDARY` is used to determine when:

* The session starts
* Each trial starts

Follow these steps to configure multiple boards:

1. Setup the hardware on the primary rig. Ensure all peripherals (lick sensor, water solenoid, positive tone speaker, negative tone speaker, air puff, session start button, and a connection on the secondary pin to as many secondary rigs, in parallel, as desired)
1. Setup the hardware on the secondary rig. There is no need to connect the button, speakers, or air puff. The pinout can be exactly the same, noting that the `PIN_SECONDARY` is an input pin during setup rather than an output pin
1. Upload the latest working rig sketch to the primary rig. Be sure to set `IS_PRIMARY_RIG` to `true` and be sure that all other trial parameters are set as desired based on whether the session is a training session or an experiment, and based on the trial design as discussed elsewhere
1. Upload the latest working rig sketch to the primary rig. Be sure to set `IS_PRIMARY_RIG` to `false`. All other settings should be identical

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

### Attenuating Water Rewards

There are a few options for modifying how much, and how often, water is available to the mouse.

#### `WATER_DISPENSE_ON_NUMBER_LICKS`

Licks are recorded with a small timeout `LICK_TIMEOUT` between licks. Consecutive licks are counted, with a longer timeout `LICK_COUNT_TIMEOUT` to reset the lick counter. So, if the lick timeout is 100ms, but the mouse is licking continuously for 300ms, there are 3 licks counted. But then if the lick count timeout is 250ms and the mouse stops licking for the next 300ms, the lick counter is set back to 0.

For water to dispense, a set number of `WATER_DISPENSE_ON_NUMBER_LICKS` licks have to have occurred in a row. In the above example where the mouse licks continuously for 300ms (three licks counted), with water dispensed after `2` licks the water reward would become available 200ms into the mouse's 300ms licking. Increasing this value makes it more difficult to obtain the water reward.

#### `WATER_DISPENSE_TIME`

This controls how long water is dispensed for in milliseconds. That is, once the conditions for dispensing water are met, water is dispensed for a set time (to ensure some water is available to the mouse) based on this parameter. The amount of reward available _when_ the mouse is rewarded can be controlled by this parameter.

#### `WATER_TIMEOUT`

When the conditions for water dispensation are met, a water timeout counter starts, and `WATER_TIMEOUT` milliseconds must elapse before another reward is available. So, if the timeout is 700ms and water is dispensed for 200ms, but the mouse continues to meet the conditions for water dispensation (much licking), water is unavailable for 500ms. This timeout can be increased to attenuate the water available to the mouse.

#### Further Attenuation

The software running the rig can be modified to further prevent or attenuate the availability of the water reward, but the above parameters are considered sufficient at this time.
