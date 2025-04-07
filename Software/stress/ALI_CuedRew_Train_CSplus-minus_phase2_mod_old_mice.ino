
//Adapted from ALI_CuedRew_Train_CSplus-minus.ino
//CS+/- cued reward task with 1.5 second cue and 2 seconds to lick
//variable ITI 
//By US 9/24/22


String programName = "ALI_CuedRew_Train_CSplus-minusUPDATED.ino";

int Lick;
int solenoidPin = 29; 
int SpeakerPin = 7;
int IRPin = 34;
int LickIR;

int test = 0;
int prev = 0;
int fauxPrev = 0;

int safe = 0;
int cue;
int freq; 

//TTL outputs

int LickTTL = 14;
int RewardTTL = 15; //for cheetah
int ITITTL = 16;
int CSplusTTL = 17;
int CSminusTTL = 18;
int RewTTL = 20;   //for fiber


unsigned long t0 = millis(); //initial value, for timing sessions (resets each trial)
unsigned long t1 = millis(); //for checking licks while solenoid is open
unsigned long t2 = millis(); //for timing reward
unsigned long t3 = millis(); //for timing ITI
unsigned long lickCount = 0;
unsigned long responseCount = 0;
unsigned long lickt;

int trialNum = 0;
int rewSize = 50; //solenoid open time in ms = ~6ul
int ITI_array = 0;
int ITI[] = {24,21,30,26,25,24,21,30,24,24,20,22,25,28,28,23,24,24,25,18,27,22,28,25,26,29,31,22,23,29,28,23,25,22,16,25,27,23,23,19,25,27,25,20,27,22,19,25,22,27,25,25,24,27,23,21,26,21,26,25,22,26,23,30,27,22,25,27,25,25,26,19,23,24,21,24,19,28,26,21,25,31,28,22,25,21,23,24,23,22,27,26,21,22,19,24,26,19,29,24,27,25,23,31,26,27,25,25,22,26,25,30,25,25,31,23,24,22,26,23,19,27,20,28,25,21,29,25,27,26,24,20,22,29,23,29,20,24,29,25,30,26,27,29,22,30,23,28,19,21,32,28,26,24,28,17,25,26,27,27,22,22,28,26,26,22,19,27,25,27,21,25,26,27,21,21,27,26,23,24,21,28,24,25,23,24,28,20,25,22,25,29,27,22,28,20,23,20,23,32,25,21,30,23,21,21,23,20,27,18,25,24,27,22,27,27,23,28,32,26,23,22,26,25,19,25,28,26,17,23,21};
int CueLength = 2000; // cue duration in ms (1.5 or 2s)

unsigned long RewTime = 2000; //duration of checking for licks
unsigned long SessionTime = 1800000;  //30 min or 45 min  
unsigned long startTime = 0;
int WhiteNoiseLength = 10; //in ms (for white noise)

int CSplus = 1000; //Frequency of CS+
int CSplusCount = 0;
int CSplusResponseCount = 0;
int CSminusCount = 0;
int CSminusResponseCount = 0;

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(A13)); //initialize RNG by reading analog pin 13

  pinMode(solenoidPin, OUTPUT);
  pinMode(SpeakerPin, OUTPUT);
  
  pinMode(IRPin, INPUT);

pinMode (CSplusTTL, OUTPUT);
pinMode (CSminusTTL, OUTPUT);
pinMode (LickTTL, OUTPUT);
pinMode (RewardTTL, OUTPUT);
pinMode (ITITTL, OUTPUT);
pinMode (RewTTL, OUTPUT);



}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void LickCheck() {
  Lick = digitalRead(IRPin);
  //Use HIGH for capacitance lickometer, LOW for IR lickport
  if (Lick == LOW) {
    //IR port blocked
    if (prev == 1 & fauxPrev == 1) {
      //Last lick never ended
      if ((millis() - lickt) > 100) {
        //If beam broken for >100ms, probably still licking
        fauxPrev = 0;
      }
    }
    else {
      lickCount = lickCount + 1;
      digitalWrite(LickTTL,HIGH);
      Serial.print("Lick ");
      Serial.println(millis());
      digitalWrite(LickTTL,LOW);
      test = 1;
      prev = 1;
      fauxPrev = 1;
      lickt = millis();
    }
  }
  else {
    //IR port not blocked
    prev = 0;
    fauxPrev = 0;
  }
}

/////////////////////////////////////////////////////////////////////////////////////create white noise, call back to it later
void WhiteNoise() {
  noTone(SpeakerPin);
  freq = random(5000, 10000);
  tone(SpeakerPin, freq);
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void loop() { 

if (trialNum == 0) {
  delay(10000);
  startTime = millis();
    Serial.print("Starting session"); 
    Serial.print(", Start Time: ");   //Print  this to the serial port
    Serial.println(startTime);
  t0=millis();
  trialNum = trialNum + 1; //sets trialNum from 0 to 1
  while ((millis()-t0) < 5000){
    LickCheck();
  }
}

if (millis() >  SessionTime) {  //End Program
    Serial.println("Program done!");
    Serial.print(CSplusResponseCount); Serial.print(" of "); Serial.print(CSplusCount); Serial.println(" CS+ trials responded to");
    Serial.print(CSminusResponseCount); Serial.print(" of "); Serial.print(CSminusCount); Serial.println(" CS- trials responded to");
    Serial.print(lickCount); Serial.println(" licks overall");
    Serial.print(trialNum-1); Serial.print (" number of trials");
    while (1) {
    }
  }
  
 //Initiate Trial 
 if (trialNum >= 1) {
 Serial.print("Trial ");
 Serial.println(trialNum);
 }

//Play tone + delay + LickCheck
    cue = random(1, 6); //1-3 CS+, 4-5 CS-
    if (cue <= 3) {
        //CS+
        digitalWrite(CSplusTTL,HIGH);
        Serial.print("CS+ ");
        Serial.println(millis());
        digitalWrite(CSplusTTL,LOW);
        CSplusCount = CSplusCount + 1;
        tone(SpeakerPin, CSplus); //start tone
        t0 = millis();
        while ((millis() - t0) < CueLength) {
          LickCheck();
        }
        noTone(SpeakerPin); //ends tone
        
 //Open solenoid + LickCheck
       test = 0; 
      t1 = millis(); 
      while ((millis() - t1) < RewTime) { //Time for mouse to lick to get rew
        LickCheck();
 
        if (test == 1) {
        t1 = -20000; //To exit loop
        digitalWrite(RewardTTL,HIGH);
        digitalWrite(RewTTL,HIGH);
        Serial.print("Reward "); Serial.println(millis());
        digitalWrite(RewardTTL,LOW);
        digitalWrite(solenoidPin, HIGH);
        t2 = millis();
        while ((millis() - t2) < (rewSize)) { 
            //lick check while solenoid is open 
         LickCheck();
        }
        digitalWrite(solenoidPin, LOW); //solenoid is closed
        digitalWrite(RewTTL,LOW);
     
     t3 = millis();
     digitalWrite(ITITTL,HIGH);
     Serial.print("ITI "); Serial.println(millis());
     digitalWrite(ITITTL,LOW);
     Serial.print("Pause = ");  Serial.println(ITI[ITI_array]);
     while ((millis() - t3) < (ITI[ITI_array]*1000)) {
          LickCheck();
         }  
     CSplusResponseCount = CSplusResponseCount + 1;       
      }
    }   
  if (test == 0) { //mouse never licked
      t3 = millis();
     digitalWrite(ITITTL,HIGH);
     Serial.print("ITI "); Serial.println(millis());
     digitalWrite(ITITTL,LOW);
      Serial.print("Pause = ");  Serial.println(ITI[ITI_array]);
      while ((millis() - t3) < (ITI[ITI_array]*1000)) {
          LickCheck();
         }
    }
  }    
else { //CS-
       digitalWrite(CSminusTTL,HIGH);
  Serial.print("CS- ");
  Serial.println(millis());
  digitalWrite(CSminusTTL,LOW);
  CSminusCount = CSminusCount + 1;
  t0 = millis();
  while ((millis() - t0) < CueLength) {
     WhiteNoise();
     test = 0;
     t1 = millis();
     while ((millis() - t1) < WhiteNoiseLength) {
        LickCheck();
        }
     }
  noTone(SpeakerPin);
  test = 0;
  t0 = millis();
  while ((millis() - t0) < (RewTime)) {
     LickCheck();
     if (test == 1) {
        t0 = 0; //to exit loop
        CSminusResponseCount = CSminusResponseCount + 1;
        }
 }
 
 t3 = millis();
 
     digitalWrite(ITITTL,HIGH);
     Serial.print("ITI "); Serial.println(millis());
     digitalWrite(ITITTL,LOW);
 Serial.print("Pause = ");  Serial.println(ITI[ITI_array]);
 while ((millis() - t3) < (ITI[ITI_array]*1000)) {
          LickCheck();
         }
    }

trialNum = trialNum + 1;
ITI_array = ITI_array + 1;
}
