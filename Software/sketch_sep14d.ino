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
int WaterSolenoidPin = 5; //Define water pin. 
int tonePin = 10; //Define Auditory cue pin.
int AirpuffPin = 4; //Air puff pin. 
const int LickPin = 12; // Define lick pin.

const unsigned long waterInterval = 500; 
unsigned long previousTime = 0; 
const unsigned long preAuditoryCue = 10000; //Wait 10 seonds at the begining of the trial before playing auditory cue. 
const unsigned long airpuffStartTime = 35000; //air puff starts 35 seconds in the trials. 
const unsigned long airpuffDur = 5000; //air puff duration 5 seconds. 
unsigned long currentTime = millis();

int oldLickState = 0;
int sessStart = 0;

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
unsigned long currentTime = millis();

  //1.Water droplits to the lickport ---------------------------------------------------------------------------------------------------------------------------------------------------------------
  digitalWrite(WaterSolenoidPin, HIGH);  //Turn water solenoid on and off every 0.5 seconds. 
  if (currentTime - previousTime >= waterInterval){
    digitalWrite(WaterSolenoidPin, LOW);
    if (WaterSolenoidPin == LOW){
      WaterSolenoidPin = HIGH;
    } else {
      WaterSolenoidPin = LOW;
    }
  }                          
  
  //2.Autidoty cue---------------------------------------------------------------------------------------------------------------------------------------------------------------
  if (currentTime - previousTime >= preAuditoryCue) {
    int randomValue = random(2); // Generate a random integer between 0 and 1.
    if (randomValue == 1) {
      tone(tonePin, 2000, 20000); // Play auditory cue for 20 seconds
      Serial.println("CS-");
    } else {
      tone(tonePin, 10000, 20000); // Play auditory cue for 20 seconds
      Serial.println("CS+");
      airPuff();
    }
    noTone(tonePin); // Stop playing after 20s
  }

  //3.Air Puff---------------------------------------------------------------------------------------------------------------------------------------------------------------
 
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

//Air Puff---------------------------------------------------------------------------------------------------------------------------------------------------------------
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




// void checkAirpuff() {
//   if(airOn == 1 && millis()-airpuffStartTime>airpuffDur) {
//     digitalWrite(Airpuff, LOW);
//   }
// }

