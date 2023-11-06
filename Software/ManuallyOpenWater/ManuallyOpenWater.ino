const int WaterSolenoidPin = 5;
const int buttonPin = 11;
bool buttonState = HIGH;
bool lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

void setup() {
  pinMode(WaterSolenoidPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  Serial.begin(9600); // Initialize serial communication
}

void loop() {
  int reading = digitalRead(buttonPin);
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;
      if (buttonState == LOW) {
        Serial.println("Button pressed");
        digitalWrite(WaterSolenoidPin, HIGH);
        delay(5000); // Keep the solenoid open for 5 seconds
        digitalWrite(WaterSolenoidPin, LOW);
        Serial.println("WaterOff");
      }
    }
  }
  lastButtonState = reading;
}
