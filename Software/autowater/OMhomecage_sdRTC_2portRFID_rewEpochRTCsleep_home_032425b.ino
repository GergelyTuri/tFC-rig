/*
  Clay 2022
  Homecage liquid consumption/licking:
  Simple script to activate a 5v Lee solenoid valve upon licking
  while logging licks and RTC time
  (latent OLED screen and WiFi)

  Requires libraries:
  - RTClib from adafruit
  - Adafruit_GFX and Adafruit_SSD1306 for OLED screen
  - Adafruit BusIO also necessary for I2C (for some reason)
  - Adafruit Neopixel for LED stimulus

  Notes:
  - have to convert string to char array to use esp32 SD write
  functions, so made subfunction for this
  - SD write functions take around 16ms, so don't try to catch
  licks faster than that (but licks from single mouse <10Hz=100ms?)
  - hacked button#1 to pin14 on OMwSmall boards (13 can't pullup)
  - temp from RTC rises as board heats up but should stabilize at
  some point and reflect basic diff in room temp

  Done:
  - set filename based upon RTC
  - log RTC time to SD occasionally
  - log temp from RTC too
  - require new lick for reward
  - start recording with buttonpress if set to toStart=0;
  - RFID tag/read for individual mouse data while group housed
  (uses serial2example)

  ToDo:
  - write some more header info at startup (rewDur, timeout, relThresh)
  - go to sleep if no licks, then wake with new lick, reset time with RTC
  - start new filename with button press?
  - add vars for including RFID, OLED (and Wifi?)

*/

/////////////////////////
/////////////////////////
// changeable vars
int boxNum = 1; // put in box number if desired
int rewDur1 = 50;//80; // rew time in ms
int rewDur2 = 50;//80;
long timeout = 500; //1000; // min time (ms) between rewards on one port
long printTimeIntvMs = 10000;//30000; // how often RTC is read
int toStart = 1; // set to 0 if starting with button press
int useRTC = 1; // real-time clock
int useOLED = 1;
int useSD = 1; // use SD card (or else just outputs serial)
int useESP = 1; // choose whether to use ESP or MPR121 touch sensing
int useMPR = 0;
int numPorts = 2; // num lick ports
int resetRTC =0; // this resets RTC from PC at compile (take off for normal run)

// RTC rew epochs
int useRTCrewEpoch=1; // 032225 for rew epoch
int rewActive = 0; // 032225 for rew epoch
int rewOnHr = 23; // hour at which rews available (24h time via RTC)
int rewOffHr = 24;

// sleep
int useSleep = 1;
#define SLEEP_DURATION 10000 //300000

// lick/touch settings
int touchThresh1 = 57; //1;//55;// value doesn't matter because now auto setup
int touchThresh2 = 57; //1;//55;
int maxNumReadings = 3;
int relThresh = 8;//4; // (used in initial baselining) should be around 4? (make low enough to trigger with mouse lick but not so low to get cross-port interaction)
long lastLick = 0;
int lickTimeout = 50;

// sync pulse params
int syncDur = 1000;  // duration of pulse
int syncIntv = 10000;  // interval of pulse train

//////////////////////////
//////////////////////////
// pin numbers
int lickPin1 = T2;//36;//25;//T3; // Left port/solenoid (from outside)
int lickPin2 = T0;//39;//27;//T7;  // Right port/solenoid
int solPin1 = 25; // 0;
int solPin2 = 26; // 12;
int ledPin = 27;
int buttonPin = 14;
int syncPin = 33; //4;//25; // pin for video sync
// int servoPin = 26;

int lickPort1 = 0; // lick port inputs on MPR121
int lickPort2 = 2;
//////////////////////////
//// Library setup

#define RXD2 16  // pins for Serial2 on the ESP32
#define TXD2 17

#include "FS.h" // SD
#include "SD.h" // SD
#include "SPI.h" // SD

// Date and time functions using a DS3231 RTC connected via I2C and Wire lib
#include "RTClib.h"
RTC_DS3231 rtc;

//#include <Wire.h>
//#include <Adafruit_NeoPixel.h>
//#define PIN        25
//#define NUMPIXELS 1
//Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

// MPR121 setup
#include "mpr121.h"
#include <Wire.h>

int irqpin = 32;  // Digital 2
boolean touchStates[12]; //to keep track of the previous touch states

#include <Wire.h>  // if using OLED screen
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET     -1 // Reset pin # (4 from example, or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3C for amazon 128x64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

//#include <WiFi.h> // if using WiFi functionality
//const char* ssid     = "yourSSID";
//const char* password = "yourPwd";
//unsigned int port=2000; // port specified on PC
//IPAddress server(192,168,4,60); //PC
//WiFiClient client; // client is global so don't have to reinst.

//These two are for the sleep function
// Define in milliseconds (5 minutes)
//#define SLEEP_DURATION 10000 //300000 //the threshold for how long it will go before it sleeps
// Variable to store the timestamp of the last activity
unsigned long lastTouchTime = 0;

///////////////////////////
// other vars
long timeSec = 0;
long timeMs = 0;
int lickBase1 = 0;
int lickBase2 = 0;

int lickCount = 0;

int touchVal1 = 0;
int touchValSum1 = 0;
int numReading1 = 0;
int hasLicked1 = 0;
long lickTime1 = 0;
//long rewTime1 = 0;
int rewOn1 = 0;
int rewReset1 = 1;
int lastTouchSum1 = 0;

int touchVal2 = 0;
int touchValSum2 = 0;
int numReading2 = 0;
int hasLicked2 = 0;
long lickTime2 = 0;
//long rewTime2 = 0;
int rewOn2 = 0;
int rewReset2 = 1;
int lastTouchSum2 = 0;

int prevLick1 = 0; // for MPR
int prevLick2 = 0;
int justLicked1 = 0;
int justLicked2 = 0;

long syncStartTime = 0;
long prevSyncTime = 0;
int prevSync = 0;
long lastSyncTime = 0;

long rewTime = 0; // 082922 now making common reward time to prevent triggering rew on each port

//RFID
char tagString[12];
int ind = 0;
boolean reading = false;
int tagWritten = 0;

// vars for SD file
String filename1 = "/000000_box0_000000.txt"; // just basic format for filename, set in setup (RTC date_time, e.g. "220313_102355")
char filename[sizeof(filename1) + 1]; //str_len1];
// (do rest in void setup() once RTC is set up to make filename)


/////////////////////////////
// the setup function runs once when you press reset or power the board
void setup() {

  // initialize digital pins
  pinMode(solPin1, OUTPUT);
  pinMode(solPin2, OUTPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(syncPin, OUTPUT);

  pinMode(lickPin1, INPUT);
  pinMode(lickPin2, INPUT);

  // MPR121
  pinMode(irqpin, INPUT);
  digitalWrite(irqpin, HIGH); //enable pullup resistor
  Wire.begin();
  mpr121_setup();


  Serial.begin(115200); // Serial at 115200 baud
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2); // for RFID reader
  delay(1000); // wait a sec for serial (and for esp32 to spit out boot info)
  /////////////////
    // OLED
  if (useOLED) {
    if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
      Serial.println(F("SSD1306 allocation failed"));
      for (;;); // Don't proceed, loop forever
    }
    display.display();
    delay(2000);
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(WHITE, BLACK);
//    display.setCursor(0, 0);
//    display.println("noLicks");
//    display.display();
  }
  //////////////
  // using RTC for filename so put first
  if (useRTC == 1) {
    if (!rtc.begin()) { // wait until RTC found, else doesn't start
      Serial.println("Couldn't find RTC");
      Serial.flush();
      display.setCursor(0, 0);
      display.println("noRTC");
      display.display();
      while (1) delay(10);
    }

    // NOTE: don't use this or it will reset every reboot z(keeps resetting to last upload computer time)
    // // NOTE: small RTC not keeping time well so do this every upload. NO then will happen every reset
//        if (rtc.lostPower()) {  // don't use this- just set beforehand
//          Serial.println("RTC lost power, let's set the time!");
//          display.setCursor(0, 16);
//          display.println("RTC lost power");
//          display.display();
//          // When time needs to be set on a new device, or after a power loss, the
//          // following line sets the RTC to the date & time this sketch was compiled
//          rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
//        }
    //}

    if (resetRTC==1) {
      rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    }
    
    //char b = boxNum;
    char date[] = "/YYMMDD_box0_hhmmss.txt";
    //date[11] = b;
    rtc.now().toString(date);
    date[11] = boxNum + '0'; // convert int to char
    //Serial.println(date);
    filename1 = date;
  }
  filename1.toCharArray(filename, sizeof(filename) + 11); //str_len1); // have to be in function to use method (i.e. not above)

  display.setCursor(0, 16);
  display.println(filename);
  display.display();
  
  if (!SD.begin()) { // begin SD communication
    Serial.println("Card Mount Failed");
    display.setCursor(0, 0);
    display.println("SD problem");
    display.display();
    return;
  }
  writeFile(SD, filename, "\r\n");
  /////////////////



  // WiFi stuff for later
  //  WiFi.begin(ssid, password);
  //  while (WiFi.status() != WL_CONNECTED) {
  //        delay(500);
  //        Serial.print(".");
  //  }
  //  Serial.println("");
  //  Serial.println("WiFi connected");
  //  Serial.println("IP address: ");
  //  Serial.println(WiFi.localIP());

  // Write some initial header data to SD
  if (toStart == 1) {
    String mess = "START, box=" + String(boxNum) + ", ms=" + String(millis()) + "\r\n";
    appendStrToSD(mess);
  }

  if (useRTC == 1) {
    char date2[] = "date=YYMMDD, time=hh:mm:ss"; // date[10] = "hh:mm:ss";
    rtc.now().toString(date2);
    String mess2 = String(date2) + ", temp=" + String(rtc.getTemperature()) + ", ms=" + String(millis()) + "\r\n"; //+ String(timeSec) + "\r\n";
    appendStrToSD(mess2);
  }

  // calc baseline for lick detection on ESP32 touch pins
  if (useESP == 1) {
    //setLickBaseline();
  }

  timeMs = millis();

  Wire.begin();
  //  pixels.begin(); // INITIALIZE NeoPixel strip
  //  delay(1000);
  //  pixels.setPixelColor(0, pixels.Color(0, 0, 10)); // this doesn't work in setup() for some reason
  //  pixels.show();   // Send the updated pixel colors to the hardware.

  display.setCursor(0, 0);
  display.println("START");
  display.display();

  // In deep sleep, the sketch never reaches the loop() statement
  //Configure Touchpad as wakeup source
  if (useSleep==1) {
    esp_sleep_enable_touchpad_wakeup();
  
    // Attach interrupt for touch pad 1
    touchAttachInterrupt(lickPin1, callback, touchThresh1);
    // Attach interrupt for touch pad 2
    touchAttachInterrupt(lickPin2, callback, touchThresh2);
  }
}

//////////////////////////////////
// the loop function runs over and over again forever
void loop() {
  if (toStart == 1) {
    // check for RFID reads
    checkRfid();

    // check for licks
    if (useMPR == 0) {
      checkLicks1(); // reads about every 2ms
      if (numPorts==2) {
        checkLicks2();
      }
    }
    else {
      checkLicksMPR();
    }

    // check reward state

    // following was giving problems 102123 so I commented out (may need to fix after)
//    if (millis() - rewTime < timeout) { // to require new lick after ITI to get reward (112922 for MPR)
//      hasLicked1 = 0;
//      hasLicked2 = 0;
//    }

    if (rewActive==1) { // 032225 for rew epoch time
      checkRew1();
      checkRew2();
    }
    
    checkSyncState();
    
    if (useRTC == 1) {
      checkTime();
    }

    // Update lastActivityTime when touch sensor is activated
    //though this is technically updated in the checklicks1 and 2 functions
    
    if (useSleep==1) {
      if (hasLicked1 || hasLicked2) {
          lastTouchTime = millis();
      }
      // Modify loop function to include touch detection (bella)
      //last touch time will be the time in every milli ever recorded during the running program
      if (millis() - lastTouchTime >= SLEEP_DURATION) {
        goToSleep();
      }
    }
    
  }
  else {
    checkButton(); // check button to start
  }
}

//////////////////
void checkLicksMPR() {

  readTouchInputs();
//
}  // END checkLicksMPR()

////////////////////
void checkLicks1() {

  if (useESP == 1) {
    touchVal1 = touchRead(lickPin1); // pre-read reduces noise spikes (found this online)
    delayMicroseconds(10);
    touchVal1 = touchRead(lickPin1); // real read
  }
  else {
    touchVal1 = digitalRead(lickPin1);
  }
  //Serial.println(touchVal1);
  numReading1++;
  //Serial.println(numReading1);
  touchValSum1 = touchValSum1 + touchVal1;

  if (numReading1 >= maxNumReadings) {
    //Serial.println(touchValSum1);
    if (touchValSum1 < touchThresh1 * maxNumReadings && hasLicked1 == 0 && millis()-lickTime1>=lickTimeout && touchValSum1<lastTouchSum1) { //touchVal1<touchThresh1 && hasLicked1==0) { // beginning of lick
      digitalWrite(ledPin, HIGH);
      hasLicked1 = 1;
      lickTime1 = millis();
      String mess = "lick1, ms=" + String(millis()) + "\r\n";
      appendStrToSD(mess);
      lickCount++;

      if (useOLED) {
        display.setCursor(0, 0);
        display.print("lick");
        display.println(lickCount);
        display.display();
      }
    }
    else if (hasLicked1 == 1 && touchValSum1 > touchThresh1*maxNumReadings) {//== 0) { // < touchThresh1*5) {
      digitalWrite(ledPin, LOW);
      hasLicked1 = 0;
      rewReset1 = 1;
    }
    lastTouchSum1 = touchValSum1; numReading1 = 0; touchValSum1 = 0; 
  }
}
//////////////////
void checkLicks2() {

  if (useESP == 1) {
    touchVal2 = touchRead(lickPin2); // pre-read reduces noise spikes (found this online)
    delayMicroseconds(10);
    touchVal2 = touchRead(lickPin2); // real read
  }
  else {
    touchVal2 = digitalRead(lickPin2);
  }
//  Serial.println(touchVal2);
//  Serial.println(millis());

  numReading2++;
  touchValSum2 = touchValSum2 + touchVal2;

  if (numReading2 >= maxNumReadings) {
    //Serial.println(touchValSum2);
    if (touchValSum2 < touchThresh2 * maxNumReadings && hasLicked2 == 0 && millis()-lickTime2>=lickTimeout && touchValSum2<lastTouchSum2) { //touchVal1<touchThresh1 && hasLicked1==0) { // beginning of lick
      digitalWrite(ledPin, HIGH);
      hasLicked2 = 1;
      lickTime2 = millis();
      String mess = "lick2, ms=" + String(millis()) + "\r\n";
      appendStrToSD(mess);
      lickCount++;
      //numReading2 = 0; touchValSum2 = 0;
      if (useOLED) {
        display.setCursor(0, 0);
        display.print("lick");
        display.println(lickCount);
        display.display();
      }
    }
    else if (hasLicked2 == 1 && touchValSum2 > touchThresh2*maxNumReadings) {//== 0) { //< touchThresh2*5) {
      digitalWrite(ledPin, LOW);
      hasLicked2 = 0;
      rewReset2 = 1;
    }
    lastTouchSum2 = touchValSum2; numReading2 = 0; touchValSum2 = 0;
  }
}
/////////////////////
void checkRew1() {
  if (hasLicked1 == 1 && rewOn1 == 0 && rewReset1 == 1 && millis() - rewTime > timeout) {
    digitalWrite(solPin1, HIGH);
    //digitalWrite(ledPin, HIGH);
    rewTime = millis(); // NOTE: using same rewTime for both ports for global timeout
    rewOn1 = 1;
    rewReset1 = 0; // rewReset is set to 0 when reward started, then reset to 1 when lick =0 (thus another reward shouldn't be triggered if port still touched)
    String mess = "reward1, ms=" + String(rewTime) + "\r\n";
    appendStrToSD(mess);
  }
  else if (rewOn1 == 1 && millis() - rewTime > rewDur1) {
    digitalWrite(solPin1, LOW);
    //digitalWrite(ledPin, LOW);
    rewOn1 = 0;
  }
}
/////////////////////
void checkRew2() {
  if (hasLicked2 == 1 && rewOn2 == 0 && rewReset2 == 1 && millis() - rewTime > timeout) {
    digitalWrite(solPin2, HIGH);
    //digitalWrite(ledPin, HIGH);
    rewTime = millis(); // NOTE: using same rewTime for both ports for global timeout
    rewOn2 = 1;
    rewReset2 = 0;
    String mess = "reward2, ms=" + String(rewTime) + "\r\n";
    appendStrToSD(mess);
  }
  else if (rewOn2 == 1 && millis() - rewTime > rewDur2) {
    digitalWrite(solPin2, LOW);
    //digitalWrite(ledPin, LOW);
    rewOn2 = 0;
  }
}

//////////////////////////////////
void checkSyncState() {
  if (prevSync == 1 && millis() - syncStartTime >= syncDur) {
    digitalWrite(syncPin, LOW);
    //digitalWrite(syncPin2, LOW);
    prevSync = 0;
  }
  else if (millis() - lastSyncTime >= syncIntv) {
    digitalWrite(syncPin, HIGH);
    //digitalWrite(syncPin2, HIGH);
    syncStartTime = millis();
    //    Serial.print("syncOut, millis = ");
    //    Serial.println(syncStartTime);
    String mess = "syncOn, ms=" + String(millis()) + "\r\n";
    appendStrToSD(mess);
    lastSyncTime = syncStartTime;
    prevSync = 1;
  }
}
/////////////////////////////
void checkRfid() { // from Bildr example
  if (Serial2.available() > 1) {
    int readByte = Serial2.read(); //read next available byte
    if (readByte == 2) reading = true; // beginning of tag
    if (readByte == 3) reading = false; // end of tag
    if (reading && readByte != 2 && readByte != 10 && readByte != 13 && ind < 12) { // NOTE: ASCII 10 is newline and 13 is carriage return
      tagString[ind] = readByte; // add byte to char arr if not control char
      ind++;
    }
    if (ind == 12 && tagWritten == 0) {
      //ind=0;
      //Serial.println(tagString);
      String tag;
      tag = tagString; // just to convert char arr to string
      String mess = "rfid=" + tag.substring(0,12) + ", ms=" + String(millis()) + "\r\n"; // I may want to substring tag to cut off occasional extra chars
      appendStrToSD(mess);
      tagWritten = 1; // added to prevent multiple prints

      if (useOLED) {
        display.setCursor(0, 16);
        display.println(mess);
        display.display();
      }
    }
    if (readByte == 10) { //073022 adding check for newline at end of tag to reset ind
      ind = 0;
      tagWritten = 0;
    }
  }
}


//////////////////
void setLickBaseline() {
  int val1 = 0; int val2 = 0; int val = 0;
  for (int i = 0; i < 50; i++) {
    val = touchRead(lickPin1);
    val = touchRead(lickPin2);
    delayMicroseconds(10);
    val1 = val1 + touchRead(lickPin1);
    val2 = val2 + touchRead(lickPin2);
  }
  lickBase1 = val1 / 50; // takes avg of 50 reads for baseline
  lickBase2 = val2 / 50;
  touchThresh1 = lickBase1 - relThresh; //lickBase1-lickBase1/relThresh;
  touchThresh2 = lickBase2 - relThresh; //lickBase2-lickBase2/relThresh;
  Serial.print("touchThresh1=");
  Serial.println(touchThresh1);
  Serial.print("touchThresh2=");
  Serial.println(touchThresh2);
}

//////////////////
void checkButton() {
  if (toStart == 0 && digitalRead(buttonPin) == 0) {
    //if (toStart==0) {
    toStart == 1;
    String mess = "START, ms=" + String(millis()) + "\r\n";
    appendStrToSD(mess);

    if (useRTC == 1) {
      char date2[] = "date=YYMMDD, time=hh:mm:ss"; // date[10] = "hh:mm:ss";
      rtc.now().toString(date2);
      String mess2 = String(date2) + ", temp=" + String(rtc.getTemperature()) + ", ms=" + String(millis()) + "\r\n"; //+ String(timeSec) + "\r\n";
      appendStrToSD(mess2);
    }
    //}
  }
}

//////////////////
// print out RTC time (and temp) every so often
void checkTime() {

  if (millis() - timeMs > printTimeIntvMs) { //(millis()-timeSec*1000>10000) {
    timeMs = millis();//timeSec = millis()/1000;

    //Serial.println(timeSec);

    // print current time
    char date[] = "date=YYMMDD, time=hh:mm:ss"; // date[10] = "hh:mm:ss";
    rtc.now().toString(date);

    String mess = String(date) + ", temp=" + String(rtc.getTemperature()) + ", ms=" + String(millis()) + "\r\n"; //+ String(timeSec) + "\r\n";
    appendStrToSD(mess);

    //  display.setCursor(0, 0);
    //  display.print("sec=");
    //  display.println(timeSec);
    //  display.display();

    if (useRTCrewEpoch==1) {
      checkRewEpochRTC();
    }
    else {rewActive=1;}
  }
}

//////////////////////////////////////

void checkRewEpochRTC() {
  
    // time check to activate reward 032225
//    DateTime time = rtc.now();
//    String ts = time.timestamp(DateTime::TIMESTAMP_TIME);

    //char date1[10] = "hh:mm:ss";
    char hr[4] = "hh";
    rtc.now().toString(hr);
    //Serial.println(hr);//[1]);
    
    //String ts1 = ts[1];
    //Serial.println(ts[0:1]); //String("DateTime::TIMESTAMP_TIME:\t")+
    //Serial.println("\n");
    int ts1 = atoi(hr);
    if (ts1>=rewOnHr && ts1<rewOffHr) {//(ts1.toInt()>0 && ts1.toInt()<2) {
      if (rewActive==0){
      digitalWrite(ledPin, HIGH);
      rewActive = 1;

      String mess = "rewActive, ms=" + String(millis()) + "\r\n"; //+ String(timeSec) + "\r\n";
      appendStrToSD(mess);  
      }
    }
    else {
      if (rewActive==1) {
      digitalWrite(ledPin, LOW);
      digitalWrite(solPin1, LOW); // just make sure valves off
      digitalWrite(solPin2, LOW);
      rewActive = 0;
      String mess = "rewInactive, ms=" + String(millis()) + "\r\n"; //+ String(timeSec) + "\r\n";
      appendStrToSD(mess);
      }
    }
    
  }
//}
///////////////// MPR121 functions

void readTouchInputs() {
  if (!checkInterrupt()) {

    //read the touch state from the MPR121
    Wire.requestFrom(0x5A, 2);

    byte LSB = Wire.read();
    byte MSB = Wire.read();

    uint16_t touched = ((MSB << 8) | LSB); //16bits that make up the touch states


    for (int i = 0; i < 12; i++) { // Check what electrodes were pressed. Go through all inputs 0-11
      if (touched & (1 << i)) { // if that pin was touched (=1)

        if (touchStates[i] == 0) { // if it wasn't previously touched, then new touch
          //pin i was just touched
          //          Serial.print("pin ");
          //          Serial.print(i);
          //          Serial.println(" was just touched");
          if (i == lickPort1 && justLicked1 == 0) { // if this is one of the lick port inputs
            justLicked1 = 1; // I don't think this variable is necessary with MPR121
            //prevLick = 1;
            hasLicked1 = 1;

            String mess = "lick1, ms=" + String(millis()) + "\r\n";
            appendStrToSD(mess);
          }
          else if (i == lickPort2 && justLicked2 == 0) {
            hasLicked2 = 1;
            justLicked2 = 1;

            String mess = "lick2, ms=" + String(millis()) + "\r\n";
            appendStrToSD(mess);
          }

          //appendStrToSD(mess);

          lickCount++;

          if (useOLED) {
            display.setCursor(0, 16);
            display.print("licks=");
            display.println(lickCount);
            display.display();
          }

        } // end IF new touch
        else if (touchStates[i] == 1) {
          //pin i is still being touched
        }

        touchStates[i] = 1; // record pin state
      } // end IF pin i being touched
      
      else { // else if pin not being touched
        if (touchStates[i] == 1) { // if was touched previously
          //Serial.print("pin ");
          //Serial.print(i);
          //Serial.println(" is no longer being touched");

          if (i == lickPort1) {
            justLicked1 = 0;
//            prevLick1 = 0;
            hasLicked1 = 0;
            rewReset1 = 1;  // rewReset is set to 0 when reward started, then reset to 1 when corresponding lick pin is no longer touched

            String mess = "lick1off, ms=" + String(millis()) + "\r\n";
            appendStrToSD(mess);
          }
          else if (i == lickPort2) {
            justLicked2 = 0;
//            prevLick2 = 0;
            hasLicked2 = 0;
            rewReset2 = 1;

            String mess = "lick2off, ms=" + String(millis()) + "\r\n";
            appendStrToSD(mess);
          }
          //pin i is no longer being touched
        }
        touchStates[i] = 0; // record pin state
      }
    }
  }
}
//////////////////////////
void mpr121_setup(void) {

  set_register(0x5A, ELE_CFG, 0x00);

  // Section A - Controls filtering when data is > baseline.
  set_register(0x5A, MHD_R, 0x01);
  set_register(0x5A, NHD_R, 0x01);
  set_register(0x5A, NCL_R, 0x00);
  set_register(0x5A, FDL_R, 0x00);

  // Section B - Controls filtering when data is < baseline.
  set_register(0x5A, MHD_F, 0x01);
  set_register(0x5A, NHD_F, 0x01);
  set_register(0x5A, NCL_F, 0xFF);
  set_register(0x5A, FDL_F, 0x02);

  // Section C - Sets touch and release thresholds for each electrode
  set_register(0x5A, ELE0_T, TOU_THRESH);
  set_register(0x5A, ELE0_R, REL_THRESH);

  set_register(0x5A, ELE1_T, TOU_THRESH);
  set_register(0x5A, ELE1_R, REL_THRESH);

  set_register(0x5A, ELE2_T, TOU_THRESH);
  set_register(0x5A, ELE2_R, REL_THRESH);

  set_register(0x5A, ELE3_T, TOU_THRESH);
  set_register(0x5A, ELE3_R, REL_THRESH);

  set_register(0x5A, ELE4_T, TOU_THRESH);
  set_register(0x5A, ELE4_R, REL_THRESH);

  set_register(0x5A, ELE5_T, TOU_THRESH);
  set_register(0x5A, ELE5_R, REL_THRESH);

  set_register(0x5A, ELE6_T, TOU_THRESH);
  set_register(0x5A, ELE6_R, REL_THRESH);

  set_register(0x5A, ELE7_T, TOU_THRESH);
  set_register(0x5A, ELE7_R, REL_THRESH);

  set_register(0x5A, ELE8_T, TOU_THRESH);
  set_register(0x5A, ELE8_R, REL_THRESH);

  set_register(0x5A, ELE9_T, TOU_THRESH);
  set_register(0x5A, ELE9_R, REL_THRESH);

  set_register(0x5A, ELE10_T, TOU_THRESH);
  set_register(0x5A, ELE10_R, REL_THRESH);

  set_register(0x5A, ELE11_T, TOU_THRESH);
  set_register(0x5A, ELE11_R, REL_THRESH);

  // Section D
  // Set the Filter Configuration
  // Set ESI2
  set_register(0x5A, FIL_CFG, 0x04);

  // Section E
  // Electrode Configuration
  // Set ELE_CFG to 0x00 to return to standby mode
  set_register(0x5A, ELE_CFG, 0x0C);  // Enables all 12 Electrodes


  // Section F
  // Enable Auto Config and auto Reconfig
  /*set_register(0x5A, ATO_CFG0, 0x0B);
    set_register(0x5A, ATO_CFGU, 0xC9);  // USL = (Vdd-0.7)/vdd*256 = 0xC9 @3.3V   set_register(0x5A, ATO_CFGL, 0x82);  // LSL = 0.65*USL = 0x82 @3.3V
    set_register(0x5A, ATO_CFGT, 0xB5);*/  // Target = 0.9*USL = 0xB5 @3.3V

  set_register(0x5A, ELE_CFG, 0x0C);

}
///////////////////////////
boolean checkInterrupt(void) {
  return digitalRead(irqpin);
}
///////////////////////////////
void set_register(int address, unsigned char r, unsigned char v) {
  Wire.beginTransmission(address);
  Wire.write(r);
  Wire.write(v);
  Wire.endTransmission();
}

//////////////////////////////////
// made subfunc to format strings for SD write
void appendStrToSD(String mess) {
  int str_len = mess.length() + 1; // this is all to make char array for write function
  char mess_char[str_len];
  mess.toCharArray(mess_char, str_len);
  appendFile(SD, filename, mess_char);
  Serial.print(mess);
}

/////////SD write funcs- DON'T CHANGE
//////////////////
void writeFile(fs::FS &fs, const char * path, const char * message) {
  Serial.printf("Writing file: %s\n", path);

  File file = fs.open(path, FILE_WRITE);
  if (!file) {
    Serial.println("Failed to open file for writing");
    return;
  }
  if (file.print(message)) {
    Serial.println("File written");
  } else {
    Serial.println("Write failed");
  }
  file.close();
}
///////////////////
void appendFile(fs::FS &fs, const char * path, const char * message) {
  //Serial.printf("Appending to file: %s\n", path);

  File file = fs.open(path, FILE_APPEND);
  if (!file) {
    Serial.println("Failed to open file for appending");
    return;
  }
  if (file.print(message)) {
    //Serial.println("Message appended");
  } else {
    Serial.println("Append failed");
  }
  file.close();
}


/////////////SLEEP
void goToSleep() {

    if (useOLED && useRTC) {
        char hm[6] = "hh:mm";
        rtc.now().toString(hm);
        display.setCursor(0, 0);
        display.print("SLP@ ");
        display.println(hm);
        //display.println(lickCount);
        display.display();
    }
    
    //Serial.print("esp sleepy");
    String mess = "espSleep, ms=" + String(millis()) + "\r\n";
    appendStrToSD(mess);
    delay(1000);
    esp_deep_sleep_start();
    
    //maybe also find a way to record and send the number of licks before it sleeps
    //since every time it wakes back up it resets the darn lick count
}

void callback() {
  lastTouchTime = millis();
}

////////////sleep code integrated
// sleep duration defined
//lastTouchTime variable stores the last activity recorded
//loop program updated to go to deep sleep if last touch is longer than sleep threshold.
// Modify checkLicks1() and checkLicks2() functions to update lastTouchTime when a touch is detected
