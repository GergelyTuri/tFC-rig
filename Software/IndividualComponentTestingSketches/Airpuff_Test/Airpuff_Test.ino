/* This should turn the air puff on and off in `duration` intervals,
 * it is useful to ensure the output is working as expected.
 */
const int airPuffPin = 4;
const int duration = 1000;

void setup() {
  pinMode(airPuffPin, OUTPUT);
}

void loop() {
  Serial.print(millis());
  Serial.println(": on");
  digitalWrite(airPuffPin, HIGH);
  delay(duration);

  Serial.print(millis());
  Serial.println(": on");
  digitalWrite(airPuffPin, LOW);
  delay(duration);
}
