int tonePinNegative = 9;  //Define Auditory cue pin.CS-

void setup() {
  pinMode(tonePinNegative, OUTPUT);
}

void loop() {
  tone(tonePinNegative, 4000, 500);
  delay(1000);
  Serial.println("TuneOn");
}