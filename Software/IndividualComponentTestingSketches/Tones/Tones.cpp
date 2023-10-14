#include "Arduino.h"
#include "Tones.h"

Tones::Tones(int pin, int frequency, bool isCont) {   
    pinMode(pin, OUTPUT);
    previousMillis = 0;
    dutyCycle = 75;
    halfPeriod = (1000 / frequency)*(dutyCycle/100.0);
    isHigh = false;
    Serial.print("Created Tone ");
    Serial.println(pin);
}

void Tones::play() {    
    if (isCont) {
        Serial.println("isCont");
        tone(pin, frequency); // this is the standard Arduino tone function
    } else {
        Serial.println("!isCont"); 
        int value = digitalRead(pin);       
        unsigned long currentMillis = millis();
        if (currentMillis - previousMillis >= halfPeriod) {
        previousMillis = currentMillis;
        if (isHigh) {
        Serial.println("pin state isHigh: " +String(value));
        digitalWrite(pin, LOW);

        isHigh = false;
        } else {
        Serial.println("pin state isLow: " +String(value));
        digitalWrite(pin, HIGH);
        isHigh = true;
        }
  }
}
}
// Compare this snippet from Software/IndividualComponentTestingSketches/tone/tone.cpp:

// Sine wave modulation works

// 
//         const int amplitude = 127;          
//         unsigned long currentTime = millis();
//         int sineValue = static_cast<int>(amplitude * sin(2 * PI * frequency * currentTime / 1000));
//         int pwmValue = map(sineValue, -amplitude, amplitude, 0, 255);
  
//         analogWrite(pin, pwmValue);