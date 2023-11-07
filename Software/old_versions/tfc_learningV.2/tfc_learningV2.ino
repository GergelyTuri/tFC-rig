// Maintainers: 
// 1. @Linxmama
// 2. @GergelyTuri
// 
// This script is used in the learning phase of the task.
// Block: 4-6 trials
// inter-trial interval: 1-5 minutes
// Trial:
//   10s: Pre-CS      water on, report lick, no CS, no US
//   20s: CS          water on, report lick, CS on, no US
//   15s: trace       water on, report lick, no CS, no US
//   5s: US           water on, report lick, no CSk, US on
// CS+ continuous 10k HZ
// CS- Paulsed 2k HZ

// 1.Water droplit to the lick port
// 2.Auditory Cue + temporal delay
// 3.air puff solenoid valve
// 4.Lick port

int buttonPin = 11;        //Define button pin to start trial.
int WaterSolenoidPin = 5;  //Define water pin.
int tonePinPositive = 10;  //Define Auditory cue pin.CS+
int tonePinNegative = 9;   //CS-
int AirpuffPin = 4;        //Air puff pin.
const int LickPin = 12;    // Define lick Pin.

const unsigned long waterInterval = 50;  //Water turn on and off every 5 seconds.
unsigned long previousTime = 0;
const unsigned long preAuditoryCue = 1000;    //Wait 10 seonds at the begining of the trial before playing auditory cue.
const unsigned long airpuffStartTime = 1000;  //air puff starts. {sped up for testing}
const unsigned long airpuffDur = 50;         //air puff duration.
unsigned long currentTime = 0;                 //millis();
unsigned long toneDur = 2000;                //Tone duration.
int oldLickState = 0;
int sessStart = 0;

long waterOnTime = 0;
long waterOffTime = 0;
int IWI = 500;  // Water interval
int trialStart = 0;
int ITI = 1000;  //trial interval
int trialOn = 0;
long trialStartTime = 0;
int trialEndTime = 0;
long trialDur = 5000;  //trial duration
int toneNeg = 0;        //indicate whether CS- is playing or not.
int waterOn = 0;

int PulseToneState = 0;
unsigned long PulsePreviousTime = 0;
const long PulseDuration = 100;
int toneState = 0;    //Initialize the tone state to LOW (Off)
int randomValue = 0;  //Generate a random integer between 0 and 1.

int trialNum = 0;  //Initialize trial couner for trial counter.


//-------------------------------------------------------------------------------------------------------------------------------------------------------------------
void setup() {
  Serial.begin(9600);
  pinMode(buttonPin, INPUT_PULLUP);
  //1.
  pinMode(WaterSolenoidPin, OUTPUT);  //water output.
  //2.
  pinMode(tonePinNegative, OUTPUT);  //auditory cue output.
  pinMode(tonePinPositive, OUTPUT);
  //3.
  pinMode(AirpuffPin, OUTPUT);  //Airpuff output.
  //4.
  pinMode(LickPin, INPUT);  //input.
  randomSeed(A4);
}

//-------------------------------------------------------------------------------------------------------------------------------------------------------------------
void loop() {
  if (digitalRead(buttonPin) == LOW) {  // Start the trial when the button was pushed
    sessStart = 1;
    Serial.println("sess start");
  }
  if (sessStart == 1 && trialNum < 4) {  //Counter, 4 trails in one block.
    currentTime = millis();
    checkTrial();
    checkLicks();
    checkCue();
  }
}

//Trial start-----------------------------------------------------------------------------------------------------------------
void checkTrial() {
  //Serial.print(currentTime);
  if (trialStart == 0 && millis() - trialEndTime > ITI) {  // to start new trial
    trialStart = 1;
    randomValue = random(2);  // pick new rand num (0/1) each trial
    Serial.println("new Trial");
    Serial.print("trialStart, trialType=");
    Serial.print(randomValue);
    Serial.print(", ms=");
    Serial.println(millis());
    trialStartTime = millis();
    trialNum = trialNum + 1;  // Trial counter starts counting
    Serial.print(trialNum);
  }
  if (trialStart == 1 && millis() - trialStartTime > trialDur) {  //Ends trial after 50s
    trialEndTime = millis();
    trialStart = 0;
  }
}

//Lick and water--------------------------------------------------------------------------------------------------------------------
void checkLicks() {
  int LickState = digitalRead(LickPin);  // Assess lick state.
  if (LickState != oldLickState) {
    if (LickState == 1) {
      Serial.println("Lick, ms=" + String(millis()));  //report the time when licking.
      digitalWrite(WaterSolenoidPin, HIGH);
    } else {
      digitalWrite(WaterSolenoidPin, LOW);
    }
    oldLickState = LickState;
  }
}


//Auditory cue and airpuff ---------------------------------------------------------------------------------------------------------------------------------------------
void checkCue() {
  if (trialStart == 1 && millis() - trialStartTime >= preAuditoryCue) {
    //Serial.print("toneCueOn, ms=");  //indicate when cue starts playing.
    // Serial.println(millis());        //indicate when cue starts playing
    Cue();
    airPuff();
  }
}

//Auditory cue---------------------------------------------------------------------------------------------------------------------------------
void Cue() {
  // Serial.println(randomValue);
  if (randomValue == 1 && millis() - trialStartTime < toneDur) {  //CS-, Pulsed 2K Hz
                                                                  // Serial.println("CS-");
    // if (millis() - PulsePreviousTime < PulseDuration) {
    //   tone(tonePinNegative, 2000, PulseDuration);
    //   PulsePreviousTime = millis();
    //   PulseToneState = 1;
    // } else if (millis() - PulsePreviousTime > PulseDuration) {
    //   noTone(tonePinNegative);
    //   PulseToneState = 0;
    // } else (millis() - PulsePreviousTime > toneDur);
    // {
    //   noTone(tonePinNegative);
    //   PulseToneState = 0;
    // }
    // PulsePreviousTime = currentTime;

    if (millis() - PulsePreviousTime > 2 * PulseDuration) {
      tone(tonePinNegative, 2000, PulseDuration);
      PulsePreviousTime = millis();
      Serial.print("pulse");
      Serial.print(millis());
    }

  } else if (randomValue == 0 && millis() - trialStartTime < toneDur) {  //CS+, continuous 10K Hz
                                                                         // Serial.println("CS+");
    noTone(tonePinNegative);
    tone(tonePinPositive, 10000, toneDur);
  }
  trialOn = 1;

  if (millis() - trialStartTime > trialDur) {  //stops tone after playing for 20s.
    noTone(tonePinNegative);
    noTone(tonePinPositive);
    trialEndTime = millis();
  }
}
//Air Puff---------------------------------------------------------------------------------------------------------------------------------------------------------------
void airPuff() {
  static int trialStartTime = 0;  // For example
  static int allPuffsStartTime = 35000;
  static int nPuffs = 5;
  static int puffDuration = 200;
  static int puffPauseTime = 1000;
  static int airpuffTotalDuration = puffDuration * nPuffs + puffPauseTime * (nPuffs - 1) + 100;
  bool puffing = false;
  int puffStopTime = 0;
  int puffStartTime = 0;
  if (currentTime - trialStartTime >= allPuffsStartTime && currentTime - trialStartTime < airpuffTotalDuration + allPuffsStartTime) {
      if (puffing == false && currentTime - puffStopTime > puffPauseTime) {
        digitalWrite(AirpuffPin, HIGH);
        puffing = true;
        puffStartTime = currentTime;
      }
      if (puffing == true && currentTime - puffStartTime > puffDuration) {
        digitalWrite(AirpuffPin, LOW);
        puffing = false;
        puffStopTime = currentTime;
      }
    }
  else {
    // Make sure we are not puffing
    if (puffing == true) {
      digitalWrite(AirpuffPin, LOW);
      puffing = false;
      puffStopTime = currentTime;
    }
  }
}
