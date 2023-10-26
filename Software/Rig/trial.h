/* Set of constants that define the trial. Change these before uploading
 * a sketch for each trial.
 *
 * NOTE: some of these should be `int` but had to be `long` during
 * debugging for unclear reasons
 *
 */

#ifndef TRIAL
#define TRIAL

const int NUMBER_OF_TRIALS = 6;
const int INTER_TRIAL_WAIT_INTERVAL = 60000; // ms
const long TRIAL_DURATION = 50000; // ms

const long LICK_TIMEOUT = 100; // ms
const bool WATER_REWARD_AVAILABLE = true;
const int WATER_DISPENSE_TIME = 200; // ms

const bool DELIVER_AIR_PUFFS = true;
const int NUMBER_OF_PUFFS = 5;
const long AIR_PUFF_START_TIME = 35000; // ms
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
const int NEGATIVE_PULSE_DURATION = 200; // ms
// Rest plus pulse duration (cycle) is one second
const int NEGATIVE_CYCLE_DURATION = 1000; // ms

#endif
