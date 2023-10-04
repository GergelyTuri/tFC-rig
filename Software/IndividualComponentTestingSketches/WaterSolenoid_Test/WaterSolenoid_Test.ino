int WaterSolenoidPin = 5;  //Define water pin.

void setup() {
  pinMode(WaterSolenoidPin, OUTPUT);  //water output.
}

void loop() {
  digitalWrite(WaterSolenoidPin, HIGH);
  delay(500);
  Serial.println("WaterOn");
  digitalWrite(WaterSolenoidPin, LOW);
  delay(500);
  Serial.println("WaterOff");
}