  
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
  int LickState = digitalRead(LickPin);  // Read the lick sensor state.

  if (LickState == HIGH) {  // Lick sensor is active HIGH (change this if your sensor is different).
    if (!isDispensing && (millis() - lastLickTime >= duration)) {
      // Lick detected and not dispensing water, and enough time has passed since the last lick.
      Serial.println("Lick Detected - Dispensing Water");
      digitalWrite(WaterSolenoidPin, HIGH);  // Open the water solenoid valve.
      lastLickTime = millis();  // Update the last lick time.
      isDispensing = true;  // Set the flag to indicate water is being dispensed.
    }
  }

  if (isDispensing && (millis() - lastLickTime >= 200)) {
    // Water has been dispensing for 1 second. You can adjust this duration as needed.
    digitalWrite(WaterSolenoidPin, LOW);  // Close the water solenoid valve.
    isDispensing = false;  // Reset the flag.
  }
}

// void loop() {
//   int LickState = digitalRead(LickPin);  // Assess lick state.
//   if (LickState == 1) {
//     lickTime = millis();
//     Serial.println("Lick, ms=" + String(millis()));  //report the time when licking.
//     Serial.println("Water on, ms=" + String(millis()));  //report the time when licking.
//     LickState = 1;
//     while (LickState == 1 && !timeOut(lickTime, duration)) {    
//       digitalWrite(WaterSolenoidPin, HIGH);      
//       if (timeOut(lickTime, duration)) {
//         digitalWrite(WaterSolenoidPin, LOW);
//         LickState = 0;
//         Serial.println("Water off, ms=" + String(millis()));                    
//         }
//     }
//   }
// }

// bool timeOut(unsigned long startTime, unsigned long duration) {
//   if (millis() - startTime > duration) {
//     return true;
//   }
//   else {
//     return false;
//   }
// }