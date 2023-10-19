/* This is the most basic Arduino sketch. It can be useful to use this
 * sketch to setup your environment. There are a few things you can
 * check to get it working:
 * 
 *   - Did you choose the correct board?
 *   - Are you uploading your sketch without error?
 *   - During upload, did the default baud rate change?
 *
 */

void setup() {
  Serial.begin(9600);
}

void loop() {
  Serial.println("Hello, Arduino");
  delay(1000);
}
