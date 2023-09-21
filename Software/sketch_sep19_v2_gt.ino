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
const unsigned long airpuffStartTime = 35000;  //air puff starts 35 seconds in the trials.
const unsigned long airpuffDur = 200;          //air puff duration 0.2 seconds.
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
int toneNon = 0;        //indicate whether CS- is playing or not.
int waterOn = 0;

const unsigned long paulsedToneOnDuration = 500;
const unsigned long paulsedToneOffDuration = 500;
int toneState = LOW;  //Initialize the tone state to LOW (Off)
int count = 0;        //Initialize the counter.
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

    if (count < 50) {  //check if the count is less than 5

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
        if (LickState == 1) {
          Serial.println("Lick, ms=" + String(millis()));  //report the time when licking stops.
        }
        oldLickState = LickState;
      }
      //Serial.print(currentTime);
      if (trialStart == 0 && millis() - trialEndTime > ITI) {  // to start new trial
        trialStart = 1;
        Serial.println("new Trial");
        trialStartTime = millis();
      }

      if (trialStart == 1 && millis() - trialStartTime > trialDur) {
        trialEndTime = millis();
        trialStart = 0;
      }

      //Auditory cue and airpuff ---------------------------------------------------------------------------------------------------------------------------------------------
      if (trialStart == 1 && millis() - trialStartTime >= preAuditoryCue) {
        Serial.println("Auditory Cue Start");


        Cue();
        airPuff();

        count++;  // Increment the counter
      }
    }
  }
}


//Auditory cue---------------------------------------------------------------------------------------------------------------------------------
void Cue() {
  int randomValue = random(2);  // Generate a random integer between 0 and 1.
  Serial.println(randomValue);
  if (randomValue == 1) {  //CS-
    do {
      Serial.println("CS-");
      noTone(tonePinPositive);
      tone(tonePinNegative, 2000, toneDur);
      toneNon = 1;
      //Pulsed tones CS-
      if (toneNon == 1 && currentTime - previousTime >= (toneState == LOW ? paulsedToneOffDuration : paulsedToneOnDuration)) {  //if tone off, compare with paulsed off duration, else, pulsed on duration
        toneState = (toneState == LOW) ? HIGH : LOW;
        digitalWrite(tonePinNegative, toneState);
        previousTime = currentTime;
      }

    } while (millis() - trialStartTime < toneDur);
  } else if (randomValue == 0) {  //CS+ + US
    do {
      Serial.println("CS+");
      noTone(tonePinNegative);
      tone(tonePinPositive, 10000, toneDur);
    } while (millis() - trialStartTime < toneDur);
  }
  trialOn = 1;
}

// if (millis() - trialStartTime > trialDur) {
//   noTone(tonePinNegative);
//   noTone(tonePinPositive);
//   trialEndTime = millis();
// }


//Air Puff---------------------------------------------------------------------------------------------------------------------------------------------------------------
void airPuff() {
  if (currentTime - previousTime >= airpuffStartTime) {
    digitalWrite(AirpuffPin, HIGH);
    Serial.println("US");
    previousTime = currentTime;
  }
  if (currentTime - previousTime >= airpuffDur) {
    digitalWrite(AirpuffPin, HIGH);
    previousTime = currentTime;  //15s after auditory cue, turn on Airpuff for .2s
  }
}
