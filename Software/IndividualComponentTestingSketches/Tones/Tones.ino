#include "Tones.h"

Tones csPlus(10, 1000, true);
int buttonPin = 11;

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin, INPUT);
  const int tonePin = 10;
  digitalWrite(tonePin, LOW);
}

void loop() {
  if (digitalRead(buttonPin) == LOW) {
    tone(10, 1000);
  }
}
