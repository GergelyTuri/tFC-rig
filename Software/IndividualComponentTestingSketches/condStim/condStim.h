#ifndef condStim_h
#define condStim_h

#include "Arduino.h"
#include "TimerControl.h"

TimerControl csPlus(10, OUTPUT);

class condStim {
public:
  condStim(int pin, const char* name) {
    this-> pin = pin;
    this -> name = name;
    pinMode(pin, OUTPUT);
    Serial.print("Created condStim ");
    Serial.println(name);
  }

  void condTone() {
    if (strcmp(name, "csPlus") == 0) {
      Serial.println("csPlus");      
      csPlus.timeOn(1000);
      digitalWrite(pin, LOW);
    }
    else if (strcmp(name, "csMinus") == 0) {
      Serial.println("csMinus");
      digitalWrite(pin, HIGH);
      delay(1000);
      digitalWrite(pin, LOW);
    }
    else {
      Serial.println("No such condStim");
    }
    digitalWrite(pin, HIGH);
    }

private:
    int pin;
    const char* name;
    };

#endif
