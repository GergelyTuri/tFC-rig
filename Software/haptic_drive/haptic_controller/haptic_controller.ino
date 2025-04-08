#include <Wire.h>
#include "Adafruit_DRV2605.h"

Adafruit_DRV2605 drv;

const uint8_t EFFECT_ID = 1;
const unsigned long START_DELAY_MS = 1000;       // 10 seconds before first effect
const unsigned long EFFECT_INTERVAL_MS = 5550;    // Interval between effects

unsigned long startTime;
unsigned long lastEffectTime = 0;
bool effectStarted = false;

void setup() {
  Serial.begin(9600);
  Serial.println("Adafruit DRV2605 Haptic Motor Test");

  if (!drv.begin()) {
    Serial.println("Could not find DRV2605");
    while (true) delay(10);
  }

  drv.selectLibrary(1);
  drv.setMode(DRV2605_MODE_INTTRIG);

  startTime = millis();
}

void loop() {
  unsigned long currentTime = millis();

  // Wait for start delay to pass before beginning the effect cycle
  if (!effectStarted) {
    if (currentTime - startTime >= START_DELAY_MS) {
      Serial.println("Start delay elapsed. Beginning effect loop...");
      effectStarted = true;
      lastEffectTime = currentTime;
    }
    return;
  }

  // Once started, trigger the effect on interval
  if (currentTime - lastEffectTime >= EFFECT_INTERVAL_MS) {
    Serial.print("Playing effect: ");
    Serial.println(EFFECT_ID);

    drv.setWaveform(0, EFFECT_ID);
    drv.setWaveform(1, 0);
    drv.go();

    lastEffectTime = currentTime;
  }
}
