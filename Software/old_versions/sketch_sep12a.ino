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

const unsigned long airpuffStartTime = 35000; //air puff starts 35 seconds in the trials. 
const unsigned long airpuffDur = 5000; //air puff duration 5 seconds. 

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

if (digitalRead(buttonPin)==LOW) {
  sessStart=1;
}
if (sessStart==1){
unsigned long currentTime = millis();

  //1.---------------------------------------------------------------------------------------------------------------------------------------------------------------
  digitalWrite(WaterSolenoidPin, HIGH);  //Turn water solenoid on and off every 0.5 seconds. 
  if (currentTime - previousTime >= waterInterval){
    digitalWrite(WaterSolenoidPin, LOW);
    if (WaterSolenoidPin == LOW){
      WaterSolenoidPin = HIGH;
    } else {
      WaterSolenoidPin = LOW;
    }
  }                          
  

  //2.---------------------------------------------------------------------------------------------------------------------------------------------------------------
  tone(tonePin, 2000, 20000); //Play auditory cue for 20 seconds
  
  //3.---------------------------------------------------------------------------------------------------------------------------------------------------------------
  if (currentTime - previousTime >= airpuffStartTime){
    digitalWrite(AirpuffPin, HIGH);
    previousTime = currentTime;
  }
  if (currentTime - previousTime >= airpuffDur){
    digitalWrite(AirpuffPin,HIGH);
    previousTime = currentTime;
  }
 //15s after auditory cue, turn on Airpuff for 1s
  
}
  
  
  //4.---------------------------------------------------------------------------------------------------------------------------------------------------------------
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


// void checkAirpuff() {
//   if(airOn == 1 && millis()-airpuffStartTime>airpuffDur) {
//     digitalWrite(Airpuff, LOW);
//   }
// }

