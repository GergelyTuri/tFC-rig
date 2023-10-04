
int AirpuffPin = 4;  //Air puff pin.

void setup() {
  pinMode(AirpuffPin, OUTPUT);  //Airpuff output.
}

void loop() {
digitalWrite(AirpuffPin, HIGH);
delay (500);
Serial.println("AirpuffOn");
digitalWrite(AirpuffPin, LOW);
delay(500);
Serial.println("AirpuffHigh");
}
