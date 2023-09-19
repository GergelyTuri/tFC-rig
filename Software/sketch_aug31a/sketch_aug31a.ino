// 1.Water droplit to the lick port
// 2.Auditory Cue + temporal delay
// 3.air puff solenoid valve
// 4.Lick port


const int LickPin = 11; // Define lick pin.
int WaterSolenoidPin = 5; //Define water pin. 
int CS = 12; //Define Auditory cue pin.
int Airpuff = 4; //Air puff pin. 

void setup() {
  Serial.begin(9600);
 
  //1.
  pinMode(WaterSolenoidPin, OUTPUT); //Set pin 5 as water output. 

  //2. 
  pinMode(CS, OUTPUT); //Set pin 12 as auditory cue output. 

  //3.
  pinMode(Airpuff, OUTPUT);//Set Pin4 as Airpuff output.

  //4.
  pinMode (LickPin, INPUT); //Set pin 11 as input. 

}

void loop() {

  //1.---------------------------------------------------------------------------------------------------------------------------------------------------------------
  digitalWrite(WaterSolenoidPin, HIGH);  //Switch water solenoid ON
  delay(500);                            //Wait 0.5 second
  digitalWrite(WaterSolenoidPin, LOW);   //Switch water solenoid OFF
  delay(500);                            //Wait 0.5 second

  //2.---------------------------------------------------------------------------------------------------------------------------------------------------------------
  tone(CS, 2000, 20000); //Play auditory cue for 20 seconds
  
  //3.---------------------------------------------------------------------------------------------------------------------------------------------------------------
  delay (35000);
  digitalWrite(Airpuff, HIGH); 
  delay (1000);
  digitalWrite(Airpuff, LOW); //15s after auditory cue, turn on Airpuff for 1s
  
  
  
  //4.---------------------------------------------------------------------------------------------------------------------------------------------------------------
  static int LickState = LOW; 
  int Time = millis ();

  LickState = digitalRead(LickPin);             // Assess lick state.


//Compare lick signals and report, did not work -----------------------------------------------------
  if (LickState != oldLickState) {
    if (LickState == LOW)}                      //compare current lick state with past lick state, determine if licking stopped.
    Serial.println ("Lick state stops" + Time); //report the time when licking stops. 
    
//Another attempt, also didn't work-----------------------------------------------------  
    x = 0;
  for (LickState = LOW;){
    x = x - 1;
  }
  for (LickState = HIGH){
    x = x + 1;
  }
  if (x == -5){                                 //determine if licking stopped
    Serial.println ("Lick state stops" + Time); //report the time when licking stops.
    x = 0;
  }
}   



