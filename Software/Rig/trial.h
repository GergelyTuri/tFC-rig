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
const int INTER_TRIAL_WAIT_INTERVAL = 1000; // ms
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

#endif
