int tonePinPositive = 10;  //Define Auditory cue pin.CS+

void setup() {
  pinMode(tonePinPositive, OUTPUT);
}

void loop() {
  tone(tonePinPositive, 2000, 500);
  delay(1000);
  Serial.println("TuneOn");
}