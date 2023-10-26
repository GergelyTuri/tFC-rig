/* Does pressing the button connected to pin 11 cause a message to be
 * sent to the serial port?
 *
 * You'll likely notice that pressing the button "once" actually prints
 * multiple messages to the serial port. This is less likely to happen
 * the "busier" our `loop` gets, but you might want to consider the
 * following structure when you want a human (or animal) input to
 * do something:
 *
 *  - Listen for the input
 *  - When it is detected, set a switch or change some state
 *  - Later, check for whatever condition will reset that switch
 *
 * The "stop condition" might be another manual input, or it might be
 * that some time has passed
 *
 */
const int buttonPin = 11;

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() {
  if (digitalRead(buttonPin) == LOW) {
    Serial.print("Button pushed at: ");
    Serial.println(millis());
  }
}
