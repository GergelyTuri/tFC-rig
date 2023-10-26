/* The "positive" tone is referred to a "CS+" and should be connected to
 * pin 10 for this rig. You should be able to alter the frequency and
 * duration of the tone. Note that this does not produce a symmetrical
 * square wave (the duration of the absence of the tone is not equivalent
 * to the duration of the tone)
 *
 */
const int tonePinPositive = 10;
const int toneFrequency = 2000;     // [Hz]
const int toneDuration = 500;       // [ms]

void setup() {
  pinMode(tonePinPositive, OUTPUT);
}

void loop() {
  Serial.print(millis());
  Serial.print(": starting ");
  Serial.print(toneFrequency);
  Serial.print(" Hz tone for ");
  Serial.print(toneDuration);
  Serial.println(" ms");
  tone(tonePinPositive, toneFrequency, toneDuration);
  delay(2000);
}
