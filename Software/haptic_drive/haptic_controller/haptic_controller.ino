#include <Wire.h>
#include "Adafruit_DRV2605.h"

Adafruit_DRV2605 drv;

void setup() {
  Serial.begin(9600);
  Serial.println("Adafruit DRV2605 Basic test");
  if (! drv.begin()) {
    Serial.println("Could not find DRV2605");
    while (1) delay(10); 
  }
    drv.selectLibrary(1);
  
  // I2C trigger by sending 'go' command 
  // default, internal trigger when sending GO command
  drv.setMode(DRV2605_MODE_INTTRIG); 
}

uint8_t effect = 1;

void loop() {
   if (effect == 1) {
    Serial.println("11.2 Waveform Library Effects List");
  }
  drv.setWaveform(0, effect);  // play effect 
  drv.setWaveform(1, 0);       // end waveform

  // play the effect!
  drv.go();

  // wait a bit
  delay(5500);
}
