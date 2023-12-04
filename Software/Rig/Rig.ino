/* Given that the Arduino is connected to components at the following pins:
 *
 * DIGITAL PINS
 * ============
 *  -  digital 4: Air puff
 *  -  digital 5: Water solenoid
 * 
 * ANALOG PINS
 * ===========
 *  -  9: Auditory cue (CS-)
 *  - 10: Auditory cue (CS+)
 *  - 11: Button to start trial
 *  - 12: Lick
 *  -  3: triggering camera recording also
 *  -  4: setting an LED to on during the trial
 *  -  6: Secondary pin (daisy chains)
 *  -  7: Reset pin (board connected to its own reset input)
 *
 * Defines a configurable run of the experimental rig with the following options:
 *
 *  - Choose to make water available
 *  - Deliver a positive or negative auditory signal
 *  - Deliver air puffs or not (positive auditory signal)
 *
 * The current implementation makes some assumptions:
 *
 *  - Each session is triggered with a button press
 *  - Air puffs are delivered at a fixed point in the trial
 *  - There are two auditory signals: positive and negative
 *    - Positive is a constant 5kHz tone
 *    - Negative is a pulsed 2kHz tone
 *  - Air puffs are only delivered after a positive auditory signal
 *
 * It can be improved by:
 *
 *  - Adding an `init.h` with the values we define at start
 *    (So they are not re-used in flush functions)
 *  - Consistency between "end" and "start" semantics
 *  - Check that differences in "global time" and "trial time" aren't
 *    going to cause any issues (some code "thinks" in global, other code
 *    "thinks" in trial, depending on requirements)
 *    - For example, refactor air puffs to use just one
 *  - The trial order randomization seems biased to start at trial 1
 *  - Refactor the top-level `loop` blocks into session functions, e.g.
 *    `preSessionReset`, `sessionStart`, `sessionEnd`, `postSessionReset`
 *
 */
#include "rig.h"
#include "trial.h"

long rigStartTime = __LONG_MAX__;
bool sessionHasStarted = false;
long sessionStartTime = __LONG_MAX__;
bool sessionHasEnded = false;
long sessionEndTime = 0;

char trialTypes[] = "000111";
int currentTrialType = 0;
long randomInterTrialInterval = 0;

int currentTrial = 0;
bool trialHasStarted = false;
long trialStartTime = __LONG_MAX__;
bool trialHasEnded = false;
long trialEndTime = 0;

long lastLickTime = 0;
bool isLicking = false;
int lickCount = 0;
long lastWaterTime = 0;

bool isPuffing = false;
long puffStartTime = __LONG_MAX__;
long puffStopTime = 0;

bool positiveSignalPlaying = false;
long positiveSignalStart = __LONG_MAX__;

bool negativeSignalPlaying = false;
long negativeSignalStart = 0;
long negativeSignalStop = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(PIN_AIR_PUFF, OUTPUT);
  pinMode(PIN_WATER_SOLENOID, OUTPUT);
  pinMode(PIN_TONE_NEGATIVE, OUTPUT);
  pinMode(PIN_TONE_POSITIVE, OUTPUT);
  pinMode(PIN_LICK, INPUT);
  pinMode(PIN_MOUSE_LED, OUTPUT);
  pinMode(PIN_CAMERA, OUTPUT);
  pinMode(PIN_RESET, OUTPUT);

  // Secondary pins are used to trigger "secondary" (vs. primary) rigs
  // in a daisy-chain setup. Just one is added until the primary-
  // secondary code is tested. Only the primary rig should use these
  // pins. The secondary rigs should have a connection to the primary
  // rig in place of the `PIN_BUTTON`. Because a button is `HIGH` by
  // default and `LOW` when pressed, the secondary pins are set to
  // `HIGH` here
  if (IS_PRIMARY_RIG) {
    // Add logic to skip positive and negative tones on secondary rigs (need tok eep water, licks, air puffs)
    pinMode(PIN_BUTTON, INPUT_PULLUP);
    pinMode(PIN_SECONDARY, OUTPUT);
  } else {
    // Configures the secondary pin the and does
    // not configure `PIN_BUTTON`
    pinMode(PIN_SECONDARY, INPUT);
  }

  // Each session of trials has a different random seed taken by
  // reading from a disconnected pin.
  randomSeed(analogRead(0));

  // Each session is a random permutation of {CS-, CS-, CS-, CS+, CS+, CS+}.
  // Note that 0 is CS-, 1 is CS+. This uses Fisher-Yates shuffle. Note
  // that this assumes there are `6` trials and would not fully randomize
  // the trials otherwise
  for (int i = NUMBER_OF_TRIALS-1; i > 0; --i) {
    int j = random (0, i+1);
    char temp = trialTypes[i];
    trialTypes[i] = trialTypes[j];
    trialTypes[j] = temp;
  }

  // Keeps track of the rig start time. This should be close to 0 since
  // `millis` starts when the rig starts, but is tracked separately for
  // readability
  rigStartTime = millis();
}

void loop() {
  // Checks for a pre-session reset
  if ((!sessionHasStarted) && (!sessionHasEnded) && (millis() - rigStartTime > RIG_PERIODIC_RESET_TIME)) {
    rigSoftwareReset();
  }

  // Checks for the session start
  if (checkSessionStart() && (!sessionHasStarted) && (!sessionHasEnded)) {
    // Because this function has a delay to ensure the simulated button
    // press is sent to secondary rigs, call it all the time to avoid
    // drift between rigs
    simulateButtonPress();

    printSessionParameters();

    print("Session has started");
    sessionHasStarted = true;
    digitalWrite(PIN_CAMERA, HIGH);
    sessionStartTime = millis();
  }

  // The session loop. It executes all `n` trials with the
  // inter-trial wait period between trials.
  if (sessionHasStarted && !sessionHasEnded) {
    if (!trialHasStarted) {
      trialStart();
    } else {
      if (!trialHasEnded) {
        // Core rig loop.
        // Executes continuously during each trial
        checkForTrialEnd();
        checkLick();
        if (WATER_REWARD_AVAILABLE) {
          checkWater();
        }
        if (USING_AUDITORY_CUES && IS_PRIMARY_RIG) {
          if (currentTrialType == 1) {
            if (USING_AIR_PUFFS) {
              checkAir();
            }
            checkPositiveSignal();
          } else {
            checkNegativeSignal();
          }
        }

        // Trial clean-up
        if (trialHasEnded) {
          print("Cleaning up last trial");
          flushTrialMetaData();
          flushLickMetaData();
          flushAirPuffMetaData();
          flushPositiveSignalMetaData();
          flushNegativeSignalMetaData();
        }

        // Inter-trial interval
        if (currentTrial >= NUMBER_OF_TRIALS) {
          // Use `randomInterTrialInterval` in the real trial. Use
          // `INTER_TRIAL_DEBUG_WAIT_INTERVAL` for debugging as it is set to
          // just one second
          long interTrialIntervalStartTime = millis();
          long interTrialIntervalWaitTime;
          if (DEBUGGING) {
            print("DEBUGGING: Waiting for 1s");
            interTrialIntervalWaitTime = INTER_TRIAL_DEBUG_WAIT_INTERVAL;
          } else {
            vprint("Waiting the inter-trial interval", randomInterTrialInterval);
            interTrialIntervalWaitTime = randomInterTrialInterval;
          }
          

          /* INTER TRIAL INTERVAL LOOP
           * Do things during the inter-trial interval. For example,
           * continue to detect licks. Functions called during this
           * loop need to be agnostic to the trial time or to the fact
           * that a trial is happening, since there is no trial time
           * and a trial is not happening :)
           */
          if (IS_PRIMARY_RIG) {
            while (millis() - interTrialIntervalStartTime < interTrialIntervalWaitTime) {
              interTrialIntervalLoop();
            }
          } else {
            while (true) {
              interTrialIntervalLoop();
              if (checkSessionStart()) {
                break;
              }
            }
          }
          simulateButtonPress();

          // Any module called during the inter-trial interval loop
          // should be flushed afterwards, so it is ready for the next
          // trial.
          flushLickMetaData();
        }
      }
    }
  } else if (!sessionHasStarted) {
    rigOutsideSessionPause();
  } else {
    print("Your session has ended, but a sketch cannot stop Arduino.");
    print("Waiting a minute...");
    delay(60000);
  }

  // Checks for the session end
  if (currentTrial >= NUMBER_OF_TRIALS) {
    digitalWrite(PIN_MOUSE_LED, LOW);
    print("Session has ended");
    sessionHasEnded = true;
    digitalWrite(PIN_CAMERA, LOW);
    sessionEndTime = millis();
  }

  // If the session has ended and the `RIG_PERIODIC_RESET_TIME` has
  // passed again, we initiate a software reset
  if ((sessionHasStarted) && (sessionHasEnded) && (millis() - sessionEndTime > RIG_PERIODIC_RESET_TIME)) {
    rigSoftwareReset();
  }
}


/* RIG MANAGEMENT
 *
 */
bool checkSessionStart() {
  if (IS_PRIMARY_RIG) {
    if (digitalRead(PIN_BUTTON) == LOW) {
      return true;
    }
  } else {
    if (digitalRead(PIN_SECONDARY) == HIGH) {
      return true;
    }
  }
  return false;
}
void simulateButtonPress() {
  digitalWrite(PIN_SECONDARY, HIGH);
  // WARNING: this waits, to simulate a button press signal sent to
  // other rigs. Do not call `simulateButtonPress` during time-
  // sensitive operations!!!
  delay(SECONDARY_PIN_PAUSE);
  digitalWrite(PIN_SECONDARY, LOW);
}
void interTrialIntervalLoop() {
  // The `interTrialIntervalLoop` is called in two separate while loops
  // for primary and secondary rigs respectively, for now it is just
  // checking licks but if more inter-trial interval stuff needs to
  // happen it can be added here and not in two places above
  checkLick();
}
void rigOutsideSessionPause() {
  if (DEBUGGING) {
    // We do get stuck here, so consider setting `N_DEBUG_CYCLES` to
    // 0 to avoid this when you know your output pins are working
    if (N_DEBUG_CYCLES > 0) {
      print("Testing pins...");
      print("Air puff");
      debugCycleOutputPin(PIN_AIR_PUFF, N_DEBUG_CYCLES, DEBUG_CYCLE_DURATION);
      print("Water solenoid");
      debugCycleOutputPin(PIN_WATER_SOLENOID, N_DEBUG_CYCLES, DEBUG_CYCLE_DURATION);
      print("Positive tone");
      debugCycleOutputPin(PIN_TONE_POSITIVE, N_DEBUG_CYCLES, DEBUG_CYCLE_DURATION);
      print("Negative tone");
      debugCycleOutputPin(PIN_TONE_NEGATIVE, N_DEBUG_CYCLES, DEBUG_CYCLE_DURATION);
      print("Mouse LED");
      debugCycleOutputPin(PIN_MOUSE_LED, N_DEBUG_CYCLES, DEBUG_CYCLE_DURATION);
      print("Camera");
      debugCycleOutputPin(PIN_CAMERA, N_DEBUG_CYCLES, DEBUG_CYCLE_DURATION);
      print("Secondary rig 1");
      debugCycleOutputPin(PIN_SECONDARY, N_DEBUG_CYCLES, DEBUG_CYCLE_DURATION);
    }
    if (DEBUG_TEST_SECONDARY) {
      while (true) {
        print("Simulating button press...");
        delay(DEBUG_CYCLE_DURATION);
        simulateButtonPress();
      }
    }
  } else {
    print("Waiting for session to start...");
    delay(100);
  }
}
void debugCycleOutputPin(int pin, int n_cycles, int cycle_time) {
  // This is a debugging function to cycle an output pin on and off
  // for a given number of cycles. It is meant to be used when
  // developing the rig, not when running trials with a mouse in
  // training or testing
  for (int i = 0; i < n_cycles; i++) {
    print("Pin on");
    digitalWrite(pin, HIGH);
    delay(cycle_time);
    print("Pin off");
    digitalWrite(pin, LOW);
    delay(cycle_time);
  }
}
void rigSoftwareReset() {
  // Leave the rig in a good state, just in case something with the
  // software reset method used does not do so
  flushRigOutputPins();

  // It is actually a hardware reset right now, driven by software. But
  // perhaps this can be changed for a software-only reset
  digitalWrite(PIN_RESET, HIGH);
}
void flushRigOutputPins() {
  // If we move to a software-based reset, we want to make sure pins
  // do not get stuck in a bad state
  digitalWrite(PIN_AIR_PUFF, LOW);
  digitalWrite(PIN_CAMERA, LOW);
  digitalWrite(PIN_MOUSE_LED, LOW);
  digitalWrite(PIN_RESET, LOW);
  digitalWrite(PIN_SECONDARY, LOW);
  digitalWrite(PIN_WATER_SOLENOID, LOW);

  noTone(PIN_TONE_POSITIVE);
  noTone(PIN_TONE_NEGATIVE);
}


/* SESSION MANAGEMENT
 *
 */
void printSessionParameters() {
  // Add variables defined in `trial.h` or `rig.h` (or other) here.
  // That way, everything that defines the trial is recorded in case an
  // issue comes up later in the analysis
  print("Session consists of six trial, three CS+, three CS- in the following order");
  print("0 is CS-, 1 is CS+");
  vprint("trialTypes", trialTypes);

  // print("Printing Adrduino or rig parameters");
  vprint("BAUD_RATE", BAUD_RATE);
  vprint("PIN_AIR_PUFF", PIN_AIR_PUFF);
  vprint("PIN_WATER_SOLENOID", PIN_WATER_SOLENOID);
  vprint("PIN_TONE_NEGATIVE", PIN_TONE_NEGATIVE);
  vprint("PIN_TONE_POSITIVE", PIN_TONE_POSITIVE);
  vprint("PIN_BUTTON", PIN_BUTTON);
  vprint("PIN_LICK", PIN_LICK);
  vprint("PIN_MOUSE_LED", PIN_MOUSE_LED);
  vprint("PIN_CAMERA", PIN_CAMERA);
  vprint("PIN_SECONDARY", PIN_SECONDARY);

  // print("Printing session parameters");
  vprint("DEBUGGING", DEBUGGING);
  vprint("IS_PRIMARY_RIG", IS_PRIMARY_RIG);
  vprint("NUMBER_OF_TRIALS", NUMBER_OF_TRIALS);
  vprint("INTER_TRIAL_DEBUG_WAIT_INTERVAL", INTER_TRIAL_DEBUG_WAIT_INTERVAL);
  vprint("TRIAL_DURATION", TRIAL_DURATION);
  vprint("LICK_TIMEOUT", LICK_TIMEOUT);
  vprint("LICK_COUNT_TIMEOUT", LICK_COUNT_TIMEOUT);
  vprint("WATER_REWARD_AVAILABLE", WATER_REWARD_AVAILABLE);
  vprint("WATER_DISPENSE_TIME", WATER_DISPENSE_TIME);
  vprint("WATER_DISPENSE_ON_NUMBER_LICKS", WATER_DISPENSE_ON_NUMBER_LICKS);
  vprint("WATER_TIMEOUT", WATER_TIMEOUT);
  vprint("USING_AUDITORY_CUES", USING_AUDITORY_CUES);
  vprint("AIR_PUFF_START_TIME", AIR_PUFF_START_TIME);
  vprint("AIR_PUFF_DURATION", AIR_PUFF_DURATION);
  vprint("INTER_PUFF_PAUSE_TIME", INTER_PUFF_PAUSE_TIME);
  vprint("AIR_PUFF_TOTAL_TIME", AIR_PUFF_TOTAL_TIME);
  vprint("AUDITORY_START", AUDITORY_START);
  vprint("AUDITORY_STOP", AUDITORY_STOP);
  vprint("POSITIVE_FREQUENCY", POSITIVE_FREQUENCY);
  vprint("POSITIVE_DURATION", POSITIVE_DURATION);
  vprint("AUDITORY_BUFFER", AUDITORY_BUFFER);
  vprint("NEGATIVE_FREQUENCY", NEGATIVE_FREQUENCY);
  vprint("NEGATIVE_PULSE_DURATION", NEGATIVE_PULSE_DURATION);
  vprint("NEGATIVE_CYCLE_DURATION", NEGATIVE_CYCLE_DURATION);
}


/* TRIAL MANAGEMENT
 *
 */
void trialStart() {
  print("Trial has started");
  trialHasStarted = true;

  // Lets mouse know water is available
  digitalWrite(PIN_MOUSE_LED, HIGH);

  // Check debugging
  if (DEBUGGING) {
    print("WARNING: DEBUGGING is set to true");
    print("This impacts the structure of the trial!!!!");
  }

  // At the start of each trial, define an inter-trial interval between 1min and 5min
  randomInterTrialInterval = random(MIN_ITI, MAX_ITI);

  // Prints out the trial-specific parameters. Other parameters are
  // printed at session start
  print("Printing trial parameters");
  vprint("randomInterTrialInterval", randomInterTrialInterval);
  // This strange subtraction is due to casting a char to an int,
  // where the char takes on its ASCII value but we subtract the ASCII
  // value of zero to give us the true numeric
  currentTrialType = trialTypes[currentTrial] - 48;
  vprint("currentTrialType", currentTrialType);

  trialStartTime = millis();
}
void checkForTrialEnd() {
  if (millis() - trialStartTime > TRIAL_DURATION) {
    print("Trial has ended");
    trialHasEnded = true;
    digitalWrite(PIN_MOUSE_LED, LOW);
    trialEndTime = millis();
  }
}
void flushTrialMetaData() {
  currentTrial++;
  trialHasStarted = false;
  trialStartTime = __LONG_MAX__;
  trialHasEnded = false;
  trialEndTime = 0;
}


/* LICK MANAGEMENT
 * This includes dispensing water.
 *
 */
void checkLick () {
  int lickState = digitalRead(PIN_LICK);
  long currentLickTime = millis();
  long sinceLastLickTime = currentLickTime - lastLickTime;
  if (sinceLastLickTime > LICK_TIMEOUT) {
    if (lickState == HIGH) {
      lastLickTime = currentLickTime;
      isLicking = true;
      lickCount++;
      print("Lick");
      if (DEBUGGING) {
        vprint("lickCount", lickCount);
      }
    }
    if (lickState == LOW) {
      isLicking = false;
    }
  }
  if (sinceLastLickTime > LICK_COUNT_TIMEOUT) {
    if (lickCount > 0) {
      print("Resetting lick count");
      lickCount = 0;
    }
  }
}
void checkWater() {
  int waterState = digitalRead(PIN_WATER_SOLENOID);
  long currentWaterTime = millis();
  long sinceLastWaterTime = currentWaterTime - lastWaterTime;
  if (isLicking && (lickCount >= WATER_DISPENSE_ON_NUMBER_LICKS) && (waterState == LOW)) {
    if (sinceLastWaterTime > WATER_TIMEOUT) {
      // Only turn the water back on if the timeout has passed since the
      // last water turn on time
      digitalWrite(PIN_WATER_SOLENOID, HIGH);
      lastWaterTime = currentWaterTime;
      print("Water on");
    }
  } else if (waterState == HIGH) {
    if (sinceLastWaterTime > WATER_DISPENSE_TIME) {
      // Wait for the dispense time before turning it off
      digitalWrite(PIN_WATER_SOLENOID, LOW);
      print("Water off");
    }
  }
}
void flushLickMetaData() {
  lastLickTime = 0;
  isLicking = false;
  lastWaterTime = 0;

  digitalWrite(PIN_WATER_SOLENOID, LOW);
  print("Water off via trial flush");
}


/* AIR PUFF MANAGEMENT
 * Only on during CS+, but managed separate from auditory cue
 *
 */
void checkAir() {
  bool isPuffing = digitalRead(PIN_AIR_PUFF);
  long currentTime = millis();
  long trialTime = currentTime - trialStartTime;
  if ((trialTime >= AIR_PUFF_START_TIME) && (trialTime < AIR_PUFF_TOTAL_TIME + AIR_PUFF_START_TIME)) {
    if (!isPuffing && ((currentTime - puffStopTime) > INTER_PUFF_PAUSE_TIME)) {
      digitalWrite(PIN_AIR_PUFF, HIGH);
      print("Puff start");
      puffStartTime = currentTime;
    }
    if (isPuffing && ((currentTime - puffStartTime) > AIR_PUFF_DURATION)) {
      digitalWrite(PIN_AIR_PUFF, LOW);
      print("Puff stop");
      puffStopTime = currentTime;
    }
  } else {
    // Makes sure we are not puffing
    if (isPuffing) {
      digitalWrite(PIN_AIR_PUFF, LOW);
      print("Puff stop, catch block");
      puffStopTime = currentTime;
    }
  }
}
void flushAirPuffMetaData() {
  puffStartTime = __LONG_MAX__;
  puffStopTime = 0;

  digitalWrite(PIN_AIR_PUFF, LOW);
  print("Puff stop via trial flush");
}


/* POSITIVE SIGNAL
 *
 */
void checkPositiveSignal() {
  long trialTime = millis() - trialStartTime;
  if (!positiveSignalPlaying && (trialTime > AUDITORY_START) && (trialTime < (AUDITORY_STOP - AUDITORY_BUFFER))) {
    // Should only hit this code once per trial.
    // The buffer tries to prevent entering a second time, since:
    //
    //    POSITIVE_DURATION = AUDITORY_STOP - AUDITORY_START
    //
    tone(PIN_TONE_POSITIVE, POSITIVE_FREQUENCY, POSITIVE_DURATION);
    positiveSignalPlaying = true;
    positiveSignalStart = trialTime;
    print("Positive signal start");
  } else if (positiveSignalPlaying && ((trialTime - positiveSignalStart) > POSITIVE_DURATION)) {
    noTone(PIN_TONE_POSITIVE);
    positiveSignalPlaying = false;
    print("Positive signal stop");
  }
}
void flushPositiveSignalMetaData() {
  positiveSignalPlaying = false;
  positiveSignalStart = __LONG_MAX__;
  noTone(PIN_TONE_POSITIVE);
  print("Positive signal stop via trial flush");
}


/* NEGATIVE SIGNAL
 * This needs to pulse the tone, unlike positive. It only prints start
 * and stop during debugging because of the time prints can take
 *
 */
void checkNegativeSignal() {
  long trialTime = millis() - trialStartTime;
  if ((trialTime > AUDITORY_START) && (trialTime < (AUDITORY_STOP - AUDITORY_BUFFER))) {
    if (!negativeSignalPlaying && ((trialTime - negativeSignalStart) > NEGATIVE_CYCLE_DURATION)) {
      // This uses positive duration to see if the `noTone` below can turn the signal off
      tone(PIN_TONE_NEGATIVE, NEGATIVE_FREQUENCY, NEGATIVE_PULSE_DURATION);
      negativeSignalPlaying = true;
      negativeSignalStart = trialTime;
      print("Negative signal start");
    } else if (negativeSignalPlaying && ((trialTime - negativeSignalStart) > NEGATIVE_PULSE_DURATION)) {
      noTone(PIN_TONE_NEGATIVE);
      negativeSignalPlaying = false;
      negativeSignalStop = trialTime;
      print("Negative signal stop");
    }
  }
}
void flushNegativeSignalMetaData() {
  negativeSignalPlaying = false;
  negativeSignalStart = 0;
  negativeSignalStop = 0;
  noTone(PIN_TONE_NEGATIVE);
  print("Negative signal stop via trial flush");
}


/* PRINTING HELPER FUNCTIONS
 * 
 *  - `print` prints a string to the serial port with a timestamp
 *  - `vprint` does so with a variable name
 *
 */
void prePrint() {
  Serial.print(currentTrial);
  Serial.print(": ");
  Serial.print(millis());
  Serial.print(": ");
  long trialTime = millis() - trialStartTime;
  if (trialTime < millis()) {
    // Only print true trial time if it is less than the current time
    // since we reset trial time to long max between trials
    Serial.print(millis() - trialStartTime);
    Serial.print(": ");
  } else {
    Serial.print(0);
    Serial.print(": ");
  }
}
void print(int x) {
  prePrint();
  Serial.println(x);
}
void print(long x) {
  prePrint();
  Serial.println(x);
}
void print(String x) {
  prePrint();
  Serial.println(x);
}
void vprint (char* x, int y) {
  char s[50];
  sprintf(s, "%s: %d", x, y);
  print(s);
}
void vprint (char* x, long y) {
  char s[50];
  sprintf(s, "%s: %ld", x, y);
  print(s);
}
void vprint (char* x, char* y) {
  char s[50];
  sprintf(s, "%s: %s", x, y);
  print(s);
}
