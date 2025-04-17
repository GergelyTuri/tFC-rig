#ifndef TRIAL
#define TRIAL
#define CS_PLUS_RATIO 0.8

// Rig settings
const bool IS_PRIMARY_RIG = true;
const long SECONDARY_PIN_PAUSE = 500;
const long SECONDARY_RIG_PAUSE_OFFSET = 250;
const long RIG_PERIODIC_RESET_TIME = 300000;

// Debug settings
const bool DEBUGGING = false;
const long INTER_TRIAL_DEBUG_WAIT_INTERVAL = 5000;
const int N_DEBUG_CYCLES = 0;
const int DEBUG_CYCLE_DURATION = 1000;
const int DEBUG_TEST_SECONDARY = false;

// Trial settings
const int NUMBER_OF_TRIALS = 6;
const char* TRIAL_TYPE_1 = "no_water_CS-";
const char* TRIAL_TYPE_2 = "water_CS+";
const bool IS_TRAINING = false;
const bool TRAINING_TRIALS_ARE_REWARDED = true;
const long MIN_ITI = 60000;
const long MAX_ITI = 300000;
const long TRIAL_DURATION = 50000;
const long POST_LAST_TRIAL_INTERVAL = 60000;

// Lick, water settings
const bool WATER_REWARD_AVAILABLE = false;
const int WATER_DISPENSE_TIME = 200;
const int WATER_TIMEOUT = 700;
const long LICK_TIMEOUT = 100;
const long LICK_COUNT_TIMEOUT = 1000;
const int WATER_DISPENSE_ON_NUMBER_LICKS = 2;

// Air puff settings
const bool USING_AIR_PUFFS = true;
const long AIR_PUFF_START_TIME = 45000;
const int AIR_PUFF_DURATION = 200;
const int INTER_PUFF_PAUSE_TIME = 1000;
const int AIR_PUFF_TOTAL_TIME = 5000;

// Auditory settings
const bool USING_AUDITORY_CUES = true;
const long AUDITORY_START = 15000;
const long AUDITORY_STOP = 35000;
const int AUDITORY_BUFFER = 100;
const int POSITIVE_FREQUENCY = 5000;
const long POSITIVE_DURATION = 20000;
const int NEGATIVE_FREQUENCY = 2000;
const int NEGATIVE_PULSE_DURATION = 1000;
const int NEGATIVE_CYCLE_DURATION = 2000;

#endif
