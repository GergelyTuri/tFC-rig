/**
 * @brief TimerControl class for setting timeouts and time-on durations.
 * 
 * @file TimerControl.h 
 * @date 10/13/2023
 * @author Gergely Turi
 * This is a simple class which allows the user to set a timeout or 
 * time-on duration for a given pin.
 * The implementation is in TimerControl.cpp
 * 
*/

#ifndef TimerControl_h
#define TimerControl_h

#include "Arduino.h"

class TimerControl {
public:
  TimerControl(int pin, int mode);

  void timeOut(unsigned long duration) {
    unsigned long endTime = millis() + duration;
    while (millis() < endTime) {
      digitalWrite(pin, LOW);
    }
  }

  void timeOn(unsigned long duration) {
    unsigned long endTime = millis() + duration;
    while (millis() < endTime) {
      digitalWrite(pin, HIGH);
    }
  }

private:
  int pin;
};

#endif