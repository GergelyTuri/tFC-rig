  
const int LickPin = 12;    // Define lick Pin.
unsigned long currentTime = 0;      
int oldLickState = 0;

void setup() {
  Serial.begin(9600);
  pinMode(LickPin, INPUT);  //input.
}

void loop() {
  int LickState = digitalRead(LickPin);  // Assess lick state.
  // Serial.print(LickState);
  if (LickState != oldLickState) {
    if (LickState == 1) {
      Serial.println("Lick, ms=" + String(millis()));  //report the time when licking.
    }
    oldLickState = LickState;
  }
}