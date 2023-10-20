/* Given that the Arduino is connected to components at the following pins:
 *
 *  -  4: Air puff
 *  -  5: Water solenoid
 *  -  9: Auditory cue (CS-)
 *  - 10: Auditory cue (CS+)
 *  - 11: Button to start trial
 *  - 12: Lick
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
 *  - (So they are not re-used in flush functions)
 *  - Per-session randomization for
 *    - Order of set of cues {CS+, CS+, CS+, CS-, CS-, CS-}
 *    - Inter-trial interval length (e.g. 1-5min)
 *
 */
#include "rig.h"
#include "trial.h"

bool sessionHasStarted = false;
long sessionStartTime = __LONG_MAX__;
bool sessionHasEnded = false;
long sessionEndTime = 0;

int currentTrial = 0;
bool trialHasStarted = false;
long trialStartTime = __LONG_MAX__;
bool trialHasEnded = false;
long trialEndTime = 0;

long lastLickTime = 0;
bool isLicking = false;
long waterStartTime = 0;

bool isPuffing = false;
long puffStopTime = 0;
long puffStartTime = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(PIN_AIR_PUFF, OUTPUT);
  pinMode(PIN_WATER_SOLENOID, OUTPUT);
  pinMode(PIN_TONE_NEGATIVE, OUTPUT);
  pinMode(PIN_TONE_POSITIVE, OUTPUT);
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(PIN_LICK, INPUT);
}

void loop() {
  if ((digitalRead(PIN_BUTTON) == LOW) && (!sessionHasStarted) && (!sessionHasEnded)) {
    print("Session has started");
    sessionHasStarted = true;
    sessionStartTime = millis();
  }

  // The session loop. It executes all `N_TRIALS` trials with the
  // `INTER_TRIAL_WAIT_INTERVAL` wait period between trials.
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
        if (DELIVER_AIR_PUFFS) {
          checkAir();
        }

        // Inter-trial interval
        if (trialHasEnded) {
          print("Cleaning up last trial");
          flushTrialMetaData();
          flushLickMetaData();
          print("Waiting the inter-trial interval");
          delay(INTER_TRIAL_WAIT_INTERVAL);
        }
      }
    }
  } else if (!sessionHasStarted) {
    print("Waiting for session to start...");
    delay(100);
  } else {
    print("Your session has ended, but a sketch cannot stop Arduino.");
    print("Waiting a minute...");
    delay(60000);
  }

  if (currentTrial > NUMBER_OF_TRIALS) {
    print("Session has ended");
    sessionHasEnded = true;
    sessionEndTime = millis();
  }
}

/* TRIAL MANAGEMENT
 *
 */
void trialStart() {
  print("Trial has started");
  trialHasStarted = true;

  // Prints out the trial parameters.
  // These will be the same for each trial, taken from a list (defined
  // for each trial separately), or randomly generated.
  print("Printing trial parameters");
  vprint("TRIAL_DURATION", TRIAL_DURATION);

  trialStartTime = millis();
}
void checkForTrialEnd() {
  if (millis() - trialStartTime > TRIAL_DURATION) {
    print("Trial has ended");
    trialHasEnded = true;
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
      print("Lick");
    }
    if (lickState == LOW) {
      isLicking = false;
    }
  }
}
void checkWater() {
  int waterState = digitalRead(PIN_WATER_SOLENOID);
  if (isLicking && (waterState == LOW)) {
    waterStartTime = millis();
    digitalWrite(WaterSolenoidPin, HIGH);
    print("Water on");
  } else if (waterState == HIGH) {
    if ((millis() - waterStartTime) > WATER_DISPENSE_TIME) {
      digitalWrite(WaterSolenoidPin, LOW);
      print("Water off");
    }
  }
}
void flushLickMetaData() {
  lastLickTime = 0;
  isLicking = false;
  waterStartTime = 0;

  digitalWrite(WaterSolenoidPin, LOW);
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
