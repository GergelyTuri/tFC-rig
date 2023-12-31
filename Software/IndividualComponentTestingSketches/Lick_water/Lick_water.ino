#include "TimerControl.h"

TimerControl lickControl(12, INPUT);
TimerControl waterControl(5, OUTPUT);

const int LickPin = 12;    // Define lick Pin.
const int WaterSolenoidPin = 5;

bool isDispensing = false; // shoudl this go to the fuction?

void setup() {
  Serial.begin(9600);
  pinMode(LickPin, INPUT);
  pinMode(WaterSolenoidPin, OUTPUT);
  digitalWrite(WaterSolenoidPin, LOW);
  digitalWrite(LickPin, LOW);
}

void loop() {
    isLicking();
    waterDispensing(isLicking());
  
}

bool isLicking() {
  unsigned long timeOutDuration = 100;
  int LickState = digitalRead(LickPin);  // Read the lick sensor state.
  if (LickState == HIGH) {
    unsigned long lickTime = millis();
    Serial.println("Lick on, ms " + String(lickTime));
    lickControl.timeOut(timeOutDuration);
    return true;
  } else {
    return false;
  }
}

void waterDispensing(bool isDispensing) { 
    if (isDispensing) {
      unsigned long timeOnDuration = 200;
      unsigned long waterOn = millis();
      digitalWrite(WaterSolenoidPin, HIGH);
      Serial.println("water on, ms " + String(waterOn));
      waterControl.timeOn(timeOnDuration);
      digitalWrite(WaterSolenoidPin, LOW);
      Serial.println("water off, ms " + String(millis()));
      isDispensing = false;
  }
}