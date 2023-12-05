/* Set of constants that define the trial. Change these before uploading
 * a sketch for each trial.
 *
 * NOTE: some of these should be `int` but had to be `long` during
 * debugging for unclear reasons
 *
 */

#ifndef TRIAL
#define TRIAL



// --------------------------------------------------------------------
// ---- RIG SETTINGS --------------------------------------------------
// --------------------------------------------------------------------
//
// --------------
// IS_PRIMARY_RIG
// [bool]
// This is the only setting that should need to change when a sketch is
// uploaded to a primary vs. a secondary rig.
const bool IS_PRIMARY_RIG = true;
//
// -------------------
// SECONDARY_PIN_PAUSE
// [milliseconds]
// This is the amount of time we set the secondary pin to `HIGH` when
// we send a signal from the primary to the secondary rigs. Its value
// needs to be large enough for the secondary rigs to detect the signal
// but does not matter otherwise (all rigs, primary and secondary, take
// the pause even if they do not send a secondary signal)
const long SECONDARY_PIN_PAUSE = 500;
//
// --------------------------
// SECONDARY_RIG_PAUSE_OFFSET
// [milliseconds]
// The secondary rig pauses for this many milliseconds less than the
// primary rig. In theory this is the time it takes for the primary rig
// to send a signal and the secondary rig to process it (from end to
// end). In practice we measure the trial markers in the output data
// and can tweak this accordingly.
const long SECONDARY_RIG_PAUSE_OFFSET = 250;
//
// -----------------------
// RIG_PERIODIC_RESET_TIME
// [milliseconds]
// If we have waited this amount of time without a session start,
// perform a software reset
const long RIG_PERIODIC_RESET_TIME = 300000;



// --------------------------------------------------------------------
// ---- DEBUG SETTINGS ------------------------------------------------
// --------------------------------------------------------------------
//
// ---------
// DEBUGGING
// [bool]
// Set this to `true` to put the rig into debug mode. The goal of debug
// mode is to make it easy to test certain aspects of rig operation
// that shouldn't be tested during mouse training or experiments. For
// example:
//
//  - A fixed inter-trial interval, `INTER_TRIAL_DEBUG_WAIT_INTERVAL`
//    is used instead of a random, longer interval
//  - During the "outside session pause" (a period of time where the
//    Arduino loop pauses while waiting for the session start
//    trigger), specific debug operations, driven by subsequent debug
//    parameters, are conducted (cycling output to each output pin)
//  - Certain calls to `print` are only made when `DEBUGGING` is `true`
//    to avoid sending too much information over the serial port during
//    rig operation, except when debugging rig code
//
const bool DEBUGGING = false;
//
// -------------------------------
// INTER_TRIAL_DEBUG_WAIT_INTERVAL
// [milliseconds]
// The fixed inter-trial wait time used when `DEBUGGING` is `true`
const long INTER_TRIAL_DEBUG_WAIT_INTERVAL = 5000;
//
// --------------
// N_DEBUG_CYCLES
// [integer]
// Set this value to an integer greater than zero to trigger a debug
// operation (during the "outside session pause") that cycles each
// output pin a number of times and for a fixed duration. This is
// especially useful when developing the board to observe that each pin
// is connected to the expected pin. Keep this value at zero to skip
// this specific debug operation
const int N_DEBUG_CYCLES = 0;
//
// --------------------
// DEBUG_CYCLE_DURATION
// [milliseconds]
// How long, in milliseconds, each output is set to during the debug
// operation controlled by `N_DEBUG_CYCLES`. Needs to be long enough to
// observe the output, but short enough for the rig to cyclde through
// all outputs in a reasonable time
const int DEBUG_CYCLE_DURATION = 1000;
//
// --------------------
// DEBUG_TEST_SECONDARY
// [bool]
// Set to `true` to enable a debug operation that, during each "outside
// session pause", sends a simulated button press on the secondary pin.
// This will only work when a rig is configured as the primary rig,
// otherwise the `PIN_SECONDARY` is not an output pin
const int DEBUG_TEST_SECONDARY = false;



// --------------------------------------------------------------------
// ---- TRIAL SETTINGS ------------------------------------------------
// --------------------------------------------------------------------
//
// ----------------
// NUMBER_OF_TRIALS
// [integer]
// Define the number of trials to execute per session. The rig was
// developed for a session consisting of six trials
const int NUMBER_OF_TRIALS = 6;
//
// -------
// MIN_ITI
// [milliseconds]
// The minimum inter-trial interval when ITI is selected randomly
const long MIN_ITI = 60000;
//
// -------
// MAX_ITI
// [milliseconds]
// The maximum inter-trial interval when ITI is selected randomly
const long MAX_ITI = 300000;
//
// --------------
// TRIAL_DURATION
// [milliseconds]
// The total length of each trial, which depends to some extent on the
// trial design. Be careful setting trial duration. It needs to be at
// least equal to the air puff start time plus air puff duration based
// on trial design
const long TRIAL_DURATION = 50000;
//
// ------------------------
// POST_LAST_TRIAL_INTERVAL
// [milliseconds]
// Wait for this amount of time after the last trial. We don't want
// this length to be random, but the inter-trial code is run during this
// interval as well
const long POST_LAST_TRIAL_INTERVAL = 60000;



// --------------------------------------------------------------------
// ---- LICK, WATER SETTINGS ------------------------------------------
// --------------------------------------------------------------------
//
// ----------------------
// WATER_REWARD_AVAILABLE
// [bool]
// Globally enable or disable whether the water solenoid can be
// activated through licks
const bool WATER_REWARD_AVAILABLE = true;
//
// -------------------
// WATER_DISPENSE_TIME
// [milliseconds]
// When water begins dispensing (water solenoid valve is open), keep
// dispensing for this amount of time. This controls how much water is
// available when water is available
const int WATER_DISPENSE_TIME = 200;
//
// -------------
// WATER_TIMEOUT
// How long after turning the water solenoid turns on can we turn it on
// again? A value of 700ms with a 200ms dispense time means a 500ms
// window where no water can be dispensed. It might make sense to
// refactor this to actually be the time from the end of water
// dispensing, but that requires code changes, too
const int WATER_TIMEOUT = 700;
//
// ------------
// LICK_TIMEOUT
// [milliseconds]
// Mouse licks are recorded. The time of each lick is stored, and if
// another lick is detected sooner than `LICK_TIMEOUT` milliseconds has
// elapsed, it is not recorded. This prevents too many licks from being
// recorded due to the sensitivity of the sensor. To some extent it
// defines a "lick" as "the number of intervals where the mouse is
// activating the lick sensor"
const long LICK_TIMEOUT = 100;
//
// ------------------
// LICK_COUNT_TIMEOUT
// [milliseconds]
// Count the number of licks accumulated in a window of this length.
// Can be used to only turn water on after a certain number of
// accumulated licks, preventing less intentional or accidental lick
// sensor recordings from activating water.
const long LICK_COUNT_TIMEOUT = 1000;
//
// ------------------------------
// WATER_DISPENSE_ON_NUMBER_LICKS
// [integer]
// Set to the number of licks required in a given `LICK_COUNT_TIMEOUT`
// window before water is dispensed
const int WATER_DISPENSE_ON_NUMBER_LICKS = 2;



// --------------------------------------------------------------------
// ---- AIR PUFF SETTINGS ---------------------------------------------
// --------------------------------------------------------------------
//
// ---------------
// USING_AIR_PUFFS
// [bool]
// Turns off _just_ air puffs, not air puffs and auditory cues. If set
// to `false` no air puff signal is sent
const bool USING_AIR_PUFFS = true;
//
// -------------------
// AIR_PUFF_START_TIME
// [milliseconds]
// At what time, during a trial, do air puffs start. Make sure to
// consider how long you want air puffs to start after the auditory
// cue stops, for example if you want the air puff to start 10s after
// the auditory cue ends, it should be set to `AUDITORY_STOP` + 10s or
// `45000` in the case that the auditory stop is `35000`
const long AIR_PUFF_START_TIME = 45000;
//
// -----------------
// AIR_PUFF_DURATION
// [milliseconds]
// Length of each air puff in milliseconds. The number of air puffs
// that will be delivered depends on the duration of each air puff and
// the length of the pause between air puffs and the total air puff
// time. The rig was developed with an air puff total time of `5000`
// with puff duration `200` and puff pause time `1000`. Meaning there
// would be five total air puffs of duration `200` with a 1s pause
// between each puff. If you wanted six air puffs of duration `200` to
// be delivered in `5000` you would need a puff pause time of `760`. If
// you want six air puffs of duration `200` to be delivered with `1000`
// puff pause time you need a total duration of `6200`. This is a bit
// over-complicated because we cannot (or, I could not) perform
// calculations in a header file
const int AIR_PUFF_DURATION = 200;
//
// ---------------------
// INTER_PUFF_PAUSE_TIME
// [milliseconds]
// Time to pause (no air puff delivered) between each air puff. See the
// description of `AIR_PUFF_DURATION` for more information
const int INTER_PUFF_PAUSE_TIME = 1000;
//
// -------------------
// AIR_PUFF_TOTAL_TIME
// [milliseconds]
// Total time where air puffs can be delivered after the air puff start
// time. Note that this interval is not guaranteed to deliver a set
// number of puffs or to end on an air puff. See the description of
// `AIR_PUFF_DURATION` for more information 
const int AIR_PUFF_TOTAL_TIME = 5000;



// --------------------------------------------------------------------
// ---- AUDITORY SETTINGS ---------------------------------------------
// --------------------------------------------------------------------
//
// -------------------
// USING_AUDITORY_CUES
// [bool]
// Set to `false` to turn off auditory cues AND air puffs. Was
// originally added for debugging other portions of the rig and might
// not be used in regular training or experimentation. You can consider
// setting this to `false` on secondary rigs but it is easier to just
// disconnect secondary rigs from peripherals they will not control
const bool USING_AUDITORY_CUES = true;
//
// --------------
// AUDITORY_START
// [milliseconds]
// At what point in a trial of any variety do auditory signals start.
// Note that this is measured from the trial start time
const long AUDITORY_START = 15000;
//
// -------------
// AUDITORY_STOP
// [milliseconds]
// At what point in a trial of any variety do auditory signals stop.
// Note that this is measured from the trial start time
const long AUDITORY_STOP = 35000;
//
// ---------------
// AUDITORY_BUFFER
// [milliseconds]
// This needs to be less than the duration of any auditory signal burst
// and is only added to the code to prevent a final tone from being
// played that lasts beyond the intended duration of the auditory
// portion of each trial. Consider extending this buffer or adding
// similar logic to the auditory cue check functions if a tone is
// observed playing after the intended time
const int AUDITORY_BUFFER = 100;
//
// ------------------
// POSITIVE_FREQUENCY
// [Hz]
// Frequency passed to the tone function for the positive auditory cue
const int POSITIVE_FREQUENCY = 5000;
//
// -----------------
// POSITIVE_DURATION
// [milliseconds]
// For the positive tone, this is the auditory stop minus the auditory
// start time, because the positive tone is not pulsed
const long POSITIVE_DURATION = 20000;
//
// ------------------
// NEGATIVE_FREQUENCY
// [Hz]
// Frequency passed to the tone function for the negative auditory cue
const int NEGATIVE_FREQUENCY = 2000;
//
// -----------------------
// NEGATIVE_PULSE_DURATION
// [milliseconds]
// The duration of each negative pulse, which is followed by a rest (a
// time where no signal is played)
const int NEGATIVE_PULSE_DURATION = 1000;
//
// -----------------------
// NEGATIVE_CYCLE_DURATION
// [milliseconds]
// The negative cycle duration is the pulse duration minus the rest
// time. Set it to twice the pulse duration for an even square wave.
const int NEGATIVE_CYCLE_DURATION = 2000;

#endif
