/* Set of constants that define the trial. Change these before uploading
 * a sketch for each trial.
 *
 * NOTE: some of these should be `int` but had to be `long` during
 * debugging for unclear reasons
 *
 */

#ifndef TRIAL
#define TRIAL

const bool DEBUGGING = false;

const int NUMBER_OF_TRIALS = 6;
// NOTE: this is only used for debugging, the "real" trial uses a
// random value between 1min and 5min
const long INTER_TRIAL_DEBUG_WAIT_INTERVAL = 1000; // ms
const long MIN_ITI = 1000; // ms
const long MAX_ITI = 5000; // ms
// Be careful setting trial duration. It needs to be at least equal to
// the air puff start time plus air puff duration
const long TRIAL_DURATION = 50000; // ms

const long LICK_TIMEOUT = 100; // ms
// Count the number of licks accumulated in this window. Can be used to
// only turn water on after a certain number of accumulated licks
const long LICK_COUNT_TIMEOUT = 1000; // ms
const bool WATER_REWARD_AVAILABLE = true;
const int WATER_DISPENSE_TIME = 200; // ms
// Set to the number of licks required to dispense water
const int WATER_DISPENSE_ON_NUMBER_LICKS = 2;
// How long after turning the water solenoid turns on can we turn it on again?
// It is easier to calculate it since the last time water was turned on,
// so a value of 700ms means a 500ms timeout after it closes
const int WATER_TIMEOUT = 700; // ms

const bool USING_AUDITORY_CUES = true; // Turns off auditory cue checks for debugging etc.
const int NUMBER_OF_PUFFS = 5;
// Note that air puff start time is relative to the trial start time.
// If the air puff should start 10s after the auditory cue ends, it
// should be set to `AUDITORY_STOP + 15000` or `50000` in the case
// that auditory stop is 35000
const long AIR_PUFF_START_TIME = 45000; // ms
const int AIR_PUFF_DURATION = 200;
const int INTER_PUFF_PAUSE_TIME = 1000;
// n_puffs*(puff_duration + puff_pause_time) - puff_pause_time
// TODO: calculate me
const int AIR_PUFF_TOTAL_TIME = 5000; // [ms]

const long AUDITORY_START = 15000; // ms, in trial time
const long AUDITORY_STOP = 35000; // ms, trial time
const int POSITIVE_FREQUENCY = 5000; // Hz
// Auditory stop minus start
// TODO: calculate me
const long POSITIVE_DURATION = 20000;
// This needs to be less than the duration of any auditory signal burst
const int AUDITORY_BUFFER = 100; // ms
const int NEGATIVE_FREQUENCY = 2000; // Hz
const int NEGATIVE_PULSE_DURATION = 1000; // ms
// Rest plus negative pulse duration is cycle duration
const int NEGATIVE_CYCLE_DURATION = 2000; // ms

#endif
