  
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
  int LickState = digitalRead(LickPin);  // Read the lick sensor state.

  if (LickState == HIGH) {  // Lick sensor is active HIGH (change this if your sensor is different).
    Serial.println("lick, ms " + String(millis()));
    return true;
  }
}

void waterDispensing(bool isDispensing) { 
    if (isDispensing) {
    unsigned long on = millis();
    unsigned int duration = on + 200;
    while (duration > millis()) {        
        digitalWrite(WaterSolenoidPin, HIGH);
        Serial.println("water on, ms " + String(on));
    }
    unsigned long off = millis();
    digitalWrite(WaterSolenoidPin, LOW);
    Serial.println("water off, ms " + String(off));
    }
}