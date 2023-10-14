#ifndef Tones_h
#define Tones_h

#include "Arduino.h"

class Tones { 
public:
  Tones(int pin, int frequency, bool isCont);

  void play();   

private:
  int pin;
  int frequency;
  bool isCont;
  bool isHigh;
  unsigned long previousMillis;
  unsigned long halfPeriod;
  float dutyCycle;    
};

#endif