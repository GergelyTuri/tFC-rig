  
const int LickPin = 12;    // Define lick Pin.
const int WaterSolenoidPin = 5;

const unsigned long duration = 200;

unsigned long lastLickTime = 0;
bool isDispensing = false;

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
    timeOut(lickTime, timeOutDuration, LickPin);    
    return true;
  } else {
    return false;
  }
}

void waterDispensing(bool isDispensing) { 
    if (isDispensing) {
      unsigned long timeOutDuration = 200;
      unsigned long waterOn = millis();
      digitalWrite(WaterSolenoidPin, HIGH);
      Serial.println("water on, ms " + String(waterOn));
      timeOut(waterOn, timeOutDuration, WaterSolenoidPin);
      digitalWrite(WaterSolenoidPin, LOW);
      Serial.println("water off, ms " + String(millis()));
      isDispensing = false;
  }
}
// void waterDispensing(bool isDispensing) { 
//     if (isDispensing) {
//       unsigned long on = millis();
//       unsigned long duration = on + 200;
//       while (millis() < duration) {        
//           digitalWrite(WaterSolenoidPin, HIGH);
//           Serial.println("water on, ms " + String(on));
//           break;
//       }      
//       digitalWrite(WaterSolenoidPin, LOW);
//       Serial.println("water off, ms " + String(millis()));
//       isDispensing = false;
//     } else {
//       digitalWrite(WaterSolenoidPin, LOW);
//     }    
// }

void timeOut(unsigned long startTime, unsigned long duration, int pin) {
  unsigned long endTime = startTime + duration;
  while (millis() < endTime) { // do i need that +5?
    digitalWrite(pin, LOW);
  }
}