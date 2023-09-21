// Block: 4-6 trials
// inter-trial interval: 1-5 minutes
// Trial:
//   10s: Pre-CS
//   20s: CS
//   15s: trace
//   5s: US
// CS+ continuous 10 kHZ
// CS- Paulsed 2 kHZ


// 1.Water droplet to the lick port
// 2.Auditory Cue + temporal delay
// 3.air puff solenoid valve
// 4.Lick port -- We could use ESP32 board for this.
#include <Arduino.h>
#include <lickport.h>

int buttonPin = 11;
int WaterSolenoidPin = 5; //Define water pin. 
int tonePin = 10; //Define Auditory cue pin.
int AirpuffPin = 4; //Air puff pin. 
const int LickPin = 12; // Define lick pin.
char cueType[] = {'CS-', 'CS+'}; //Define cue type.

const unsigned long waterInterval = 500;  
const unsigned long preAuditoryCue = 10000; //Wait 10 seonds at the begining of the trial before playing auditory cue. 
const unsigned long airpuffStartTime = 35000; //air puff starts 35 seconds in the trials. 
const unsigned long airpuffDur = 200; //air puff duration 5 seconds. <-this seems too much. 200ms five 3-5 times is enough. 
unsigned long currentTime = millis();
unsigned long previousTime = 0;

int oldLickState = 0;
int sessStart = 0;

//2.Audidory cue-------------------------------------
void cueStimulus(cueType);{ //Define cue stimulus function.
  if (cueType == "CS-") {
    Serial.println("CS-");      
    tone(tonePin, 2000, 20000);
  }
  else if (cueType == "CS+"){
    Serial.println("CS+");
    tone(tonePin, 10000, 20000);
  }
  noTone(tonePin);    
}

//3.Air Puff---------------------------------------
void airPuff(){
  if (currentTime - previousTime >= airpuffStartTime){
    digitalWrite(AirpuffPin, HIGH);
    previousTime = currentTime;
  }
  if (currentTime - previousTime >= airpuffDur){
    digitalWrite(AirpuffPin,HIGH);
    previousTime = currentTime;
  }
 //15s after auditory cue, turn on Airpuff for 5s
}
void setup() {
  Serial.begin(9600);
 
  //1.
  pinMode(WaterSolenoidPin, OUTPUT); //Set pin 5 as water output. 

  //2. 
  pinMode(tonePin, OUTPUT); //Set pin 12 as auditory cue output. 

  //3.
  pinMode(AirpuffPin, OUTPUT);//Set Pin4 as Airpuff output.

  //4.
  pinMode (LickPin, INPUT); //Set pin 11 as input. 

  pinMode(buttonPin, INPUT_PULLUP);

}

void loop() {

// Start the trial when the button was pushed
if (digitalRead(buttonPin)==LOW) {
  sessStart=1;
}
if (sessStart==1){
  currentTime = millis();
  //1.Water droplets to the lickport ---------------------------------------------------------------------------------------------------------------------------------------------------------------
  // don't we need to turn this on after the cue?
  digitalWrite(WaterSolenoidPin, HIGH);  //Turn water solenoid on and off every 0.5 seconds. 
  if (currentTime - previousTime >= waterInterval){
    digitalWrite(WaterSolenoidPin, LOW);
    if (WaterSolenoidPin == LOW){
      WaterSolenoidPin = HIGH;
    } else {
      WaterSolenoidPin = LOW;
    }
  }                          
  
  if (currentTime - previousTime >= preAuditoryCue) {
    int randomValue = random(2); // Generate a random integer between 0 and 1.
    if (randomValue == 1) {
      cueStimulus("CS-");      
    } else {
      cueStimulus("CS+");      
      airPuff(); // <- this is not ok. we need a function that will turn on the airpuff for 5s
      // also we need a controller for determining whether we need the puff at all. e.g.
      //during training we do no need it, but we will need it during the learning and post-reinforcing phase.
      // this also seems like an undefined function here
    }     
  }  
 
  //4.Report Lick---------------------------------------------------------------------------------------------------------------------------------------------------------------
  static int LickState = LOW; 
  int Time = millis ();

  LickState = digitalRead(LickPin);             // Assess lick state.
  //Serial.println(LickState);

//Compare lick signals and report -----------------------------------------------------
  if (LickState != oldLickState) {
    if (LickState == HIGH) {                      //compare current lick state with past lick state, determine if licking stopped.
      Serial.println("Lick, ms=" + String(millis())); //report the time when licking stops. 
    }
    oldLickState=LickState;
  }

}   


}

// void checkAirpuff() {
//   if(airOn == 1 && millis()-airpuffStartTime>airpuffDur) {
//     digitalWrite(Airpuff, LOW);
//   }
// }

