// Block: 4-6 trials
// inter-trial interval: 1-5 minutes
// Trial:
//   10s: Pre-CS
//   20s: CS
//   15s: trace
//   5s: US
// CS+ continuous 10k HZ
// CS- Paulsed 2k HZ


// 1.Water droplit to the lick port
// 2.Auditory Cue + temporal delay
// 3.air puff solenoid valve
// 4.Lick port

int buttonPin = 11;
int WaterSolenoidPin = 5;  //Define water pin.
int tonePinPositive = 10;  //Define Auditory cue pin.CS+
int tonePinNegative = 9;   //CS-
int AirpuffPin = 4;        //Air puff pin.
const int LickPin = 12;    // Define lick Pin.

const unsigned long waterInterval = 5000;
unsigned long previousTime = 0;
const unsigned long preAuditoryCue = 10000;    //Wait 10 seonds at the begining of the trial before playing auditory cue.
const unsigned long airpuffStartTime = 10000;  //air puff starts. {sped up for testing}
const unsigned long airpuffDur = 5000;         //air puff duration.
unsigned long currentTime = 0;                 //millis();
unsigned long toneDur = 20000;                 //Tone duration.
int oldLickState = 0;
int sessStart = 0;

long waterOnTime = 0;
long waterOffTime = 0;
int IWI = 5000;  // Water interval
int trialStart = 0;
int ITI = 10000;  //trial interval
int trialOn = 0;
long trialStartTime = 0;
int trialEndTime = 0;
long trialDur = 50000;  //trial duration
int toneNeg = 0;        //indicate whether CS- is playing or not.
int waterOn = 0;

// const unsigned long paulsedToneOnDuration = 1000;
// const unsigned long paulsedToneOffDuration = 1000;
int PulseToneState = 0;
unsigned long PulsePreviousTime = 0;
const long PulseDuration = 500;
int toneState = 0;    //Initialize the tone state to LOW (Off)
int randomValue = 0;  //random(2);  // Generate a random integer between 0 and 1.

int trialNum = 0;


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
  if (sessStart == 1 && trialNum < 4) {
    currentTime = millis();
    checkTrial();
    checkLicks();
    checkWater();
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
    trialNum = trialNum + 1;
  }
  if (trialStart == 1 && millis() - trialStartTime > trialDur) {
    trialEndTime = millis();
    trialStart = 0;
  }
}

//Report Lick---------------------------------------------------------------------------------------------------------------------------------------------------------------
void checkLicks() {
  int LickState = digitalRead(LickPin);  // Assess lick state.
  if (LickState != oldLickState) {
    //Serial.print("Licking");
    if (LickState == 1) {
      Serial.println("Lick, ms=" + String(millis()));  //report the time when licking stops.
    }
    oldLickState = LickState;
  }
}

//Water droplets to the lickport ---------------------------------------------------------------------------------------------------------------------------------------------------------------
void checkWater() {
  if (waterOn == 0 && currentTime - waterOffTime > IWI) {
    Serial.println("rew ON");
    digitalWrite(WaterSolenoidPin, HIGH);  //Turn water solenoid on and off every 0.5 seconds.
    waterOn = 1;
    waterOnTime = millis();
  }
  if (waterOn == 1 && currentTime - waterOnTime >= waterInterval) {
    digitalWrite(WaterSolenoidPin, LOW);
    Serial.println("rew OFF");
    waterOffTime = millis();
    waterOn = 0;
    if (WaterSolenoidPin == LOW) {
      WaterSolenoidPin = HIGH;
    } else {
      WaterSolenoidPin = LOW;
    }
  }
}

//Auditory cue and airpuff ---------------------------------------------------------------------------------------------------------------------------------------------
void checkCue() {
  if (trialStart == 1 && millis() - trialStartTime >= preAuditoryCue) {  // just sets delay for cues in trial
    //Serial.println("Auditory Cue Start");
    Serial.print("toneCueOn, ms=");
    Serial.println(millis());
    Cue();
    airPuff();
  }
}

//Auditory cue---------------------------------------------------------------------------------------------------------------------------------
void Cue() {
  Serial.println(randomValue);
  if (randomValue == 1 && millis() - trialStartTime < toneDur) {
    Serial.println("CS-");
    if (millis() - PulsePreviousTime < PulseDuration) {
      tone(tonePinNegative, 200, PulseDuration);
      PulsePreviousTime = millis();
      PulseToneState = 1;
    } else if (millis() - PulsePreviousTime > PulseDuration) {
      noTone(tonePinNegative);
      PulseToneState = 0;
    } else (millis() - PulsePreviousTime > toneDur);
    {
      noTone(tonePinNegative);
      PulseToneState = 0;
    }
    previousTime = currentTime;
  } else if (randomValue == 0 && millis() - trialStartTime < toneDur) {  //CS+
    Serial.println("CS+");
    noTone(tonePinNegative);
    tone(tonePinPositive, 10000, toneDur);
  }
  trialOn = 1;
}
if (millis() - trialStartTime > trialDur) {
  noTone(tonePinNegative);
  noTone(tonePinPositive);
  trialEndTime = millis();
}

//Air Puff---------------------------------------------------------------------------------------------------------------------------------------------------------------
void airPuff() {
  static unsigned long airPuffLastChangeTime = 0;
  static int airPuffState = LOW;

  if (currentTime - previousTime >= airpuffStartTime) {
    Serial.println("US");
    if (airPuffState == LOW) {
      digitalWrite(AirpuffPin, HIGH);
      airPuffState = HIGH;
    } else {
      digitalWrite(AirpuffPin, LOW);
      airPuffState = LOW;
    }
    airPuffLastChangeTime = currentTime;
  }
  if (currentTime - previousTime >= airpuffDur) {
    digitalWrite(AirpuffPin, LOW);
    previousTime = currentTime;  //15s after auditory cue, turn on Airpuff for .2s
  }
}
