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
int tonePinPositive = 10;          //Define Auditory cue pin.CS+
int tonePinNegative = 9;            //CS-
int AirpuffPin = 4;        //Air puff pin.
const int LickPin = 12;    // Define lick Pin.

const unsigned long waterInterval = 5000;
unsigned long previousTime = 0;
const unsigned long preAuditoryCue = 10000;    //Wait 10 seonds at the begining of the trial before playing auditory cue.
const unsigned long airpuffStartTime = 35000;  //air puff starts 35 seconds in the trials.
const unsigned long airpuffDur = 200;          //air puff duration 0.2 seconds.
unsigned long currentTime = 0;                 //millis();

int oldLickState = 0;
int sessStart = 0;

long waterOnTime = 0;
long waterOffTime = 0;
int IWI = 5000;                // Water interval
int trialStart = 0;
int ITI = 10000;              //trial interval
int trialOn = 0;
long trialStartTime = 0;
int trialEndTime = 0;
long trialDur = 20000;
int waterOn=0;

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

  if (sessStart == 1) {
    currentTime = millis();
    //Water droplets to the lickport ---------------------------------------------------------------------------------------------------------------------------------------------------------------
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
    //Report Lick---------------------------------------------------------------------------------------------------------------------------------------------------------------
    int LickState = digitalRead(LickPin);  // Assess lick state.
    if (LickState != oldLickState) {
      //Serial.print("Licking");
      if (LickState == 1) {                           //compare current lick state with past lick state, determine if licking stopped.
        Serial.println("Lick, ms=" + String(millis()));  //report the time when licking stops.
      }
      oldLickState = LickState;
    }
    //Serial.print(currentTime);
    if (trialStart == 0  && millis()-trialEndTime>ITI) { // to start new trial
      trialStart = 1;
      Serial.println("new Trial");
      trialStartTime = millis();
    }

    if (trialStart ==1 && millis()-trialStartTime>trialDur) {
      trialEndTime = millis();
      trialStart = 0;
    }

    //Auditory cue and airpuff ---------------------------------------------------------------------------------------------------------------------------------------------
    if (trialStart == 1 && millis() - trialStartTime >= preAuditoryCue) {
      Serial.println("Auditory Cue Start");
      int randomValue = random(2);  // Generate a random integer between 0 and 1.
      Serial.println(randomValue);
      // if (trialOn == 1) {
     
      if (randomValue == 1) {
        cueStimulus("CS-");
      } else {
        cueStimulus("CS+");
        airPuff();
      }
      //}
      trialOn = 1;
    }

    if (millis()-trialStartTime>trialDur) {
      noTone(tonePinNegative);
      noTone(tonePinPositive);
      trialEndTime = millis();
    }

  }
}

// Auditory Cue -------------------------------------------------------------------------------
void cueStimulus(const char* cueType) {
  if (strcmp(cueType, "CS-") == 0) {
    Serial.println("CS-");
    tone(tonePinNegative, 2000, 20000);  // Play auditory cue- for 20 seconds
  } else {//if (strcmp(cueType, "CS+") == 0) {
    Serial.println("CS+");
    tone(tonePinPositive, 10000, 20000);  // Play auditory cue+ for 20 seconds
  }
  //noTone(tonePin);
}

//Paused tone.


//Air Puff---------------------------------------------------------------------------------------------------------------------------------------------------------------
void airPuff() {
  if (currentTime - previousTime >= airpuffStartTime) {
    digitalWrite(AirpuffPin, HIGH);
    previousTime = currentTime;
  }
  if (currentTime - previousTime >= airpuffDur) {
    digitalWrite(AirpuffPin, HIGH);
    previousTime = currentTime;  //15s after auditory cue, turn on Airpuff for .2s
  }
}

//2.Autidoty cue---------------------------------------------------------------------------------------------------------------------------------------------------------------
// if (currentTime - previousTime >= preAuditoryCue) {
//   int randomValue = random(2); // Generate a random integer between 0 and 1.
//   if (randomValue == 1) {
//     tone(tonePin, 2000, 20000); // Play auditory cue for 20 seconds
//     Serial.println("CS-");
//   } else {
//     tone(tonePin, 10000, 20000); // Play auditory cue for 20 seconds
//     Serial.println("CS+");
//     airPuff();
//   }
//   noTone(tonePin); // Stop playing after 20s
// }



// void checkAirpuff() {
//   if(airOn == 1 && millis()-airpuffStartTime>airpuffDur) {
//     digitalWrite(Airpuff, LOW);
//   }
// }
