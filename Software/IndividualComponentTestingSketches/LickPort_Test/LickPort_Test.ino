int buttonPin = 11;   
const int LickPin = 12;    // Define lick Pin.
unsigned long currentTime = 0;      
int oldLickState = 0;

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(LickPin, INPUT);  //input.
}

void loop() {
  if (digitalRead(buttonPin) == LOW) {  // Start the trial when the button was pushed
    Serial.println("start");
    currentTime = millis();

    checkLicks();

  }
}

void checkLicks() {
  int LickState = digitalRead(LickPin);  // Assess lick state.
  Serial.print(LickState);
  if (LickState != oldLickState) {
    if (LickState == 1) {
      Serial.println("Lick, ms=" + String(millis()));  //report the time when licking.
    }
    oldLickState = LickState;
  }
}