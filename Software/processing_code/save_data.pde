// Saving arduino output to a file

String mouse_id = "mouse01"; // Mouse ID, change for each mouse
String serialPort = "COM3";  // Arduino serial port

// event names (to look for in each serial line- must be exact substring,
// typical format "event, ms=")
String event1string = "Session has started";
String event2string = "Cleaning up last trial";
String event3string = "Session has ended";
String event4string = "Trial has ended";
String event5string = "Lick";
String event6string = "Water on";
String event7string = "Water off";
String event8string = "Puff start";
String event9string = "Puff stop";
String event10string = "Positive signal start";
String event11string = "Positive signal stop";
String event12string = "Negative signal start";
String event13string = "Negative signal stop";


/////////////  
import processing.serial.*;    // import the Processing serial library
PrintWriter output;    // initialize the PrintWriter Java object (don't know much about this)

Serial behavSerPort;    // the serial port for behavioral input

long time=0;    // initialize variable for the current time since program started
int timeSec = 0; // current time in sec
String event;  // initialize variable for serial data from Arduino

int h = 0; // variable for recording hour of start/stop
int m = 0; // variable for recording minute of start/stop
int n = 0; 

int i = 0;  // variable for incrementing event strings and times
int j = 0;  // variable for incrementing time bins

void setup()
{
    checkFilename();
      // Create a new file in the sketch directory ready for writing text
    extension = ".txt";
    filename = animal.concat(extension);
    output = createWriter(filename);
    // set up serial port
    println(Serial.list());
    behavSerPort = new Serial(this, serialPort, 115200); // Serial baud rate with wheel rotary enc. Arduino (must agree with Arduino Serial.begin(baudRate);)
    behavSerPort.bufferUntil('\n');

    //print header
    // start time (PC)
    output.println(animal);
    h = hour();
    m = minute();
    output.println("START time");
    output.print(h);
    output.print(":");
    if (m<=9) {
    output.println("0"+m); 
    }
    else {
    output.println(m);
    }
    println("START time");
    print(h);
    print(":");
    println(m);
    behavSerPort.write("1\n"); // prompt behav arduino to print header 
                               // (instead of restarting for Processing 4)
}

void parseString() {
    i = i+1; // count the events

    if (event.contains(event1string)) {
        eventType = 1;
    }
    else if (event.contains(event2string)) {
        eventType = 2;
    }
    else if (event.contains(event3string)) {
        eventType = 3;
    }
    else if (event.contains(event4string)) {
        eventType = 4;
    }
    else if (event.contains(event5string)) {
        eventType = 5;
    }
    else if (event.contains(event6string)) {
        eventType = 6;
    }
    else if (event.contains(event7string)) {
        eventType = 7;
    }
    else if (event.contains(event8string)) {
        eventType = 8;
    }
    else if (event.contains(event9string)) {
        eventType = 9;
    }
    else if (event.contains(event10string)) {
        eventType = 10;
    }
    else if (event.contains(event11string)) {
        eventType = 11;
    }
    else if (event.contains(event12string)) {
        eventType = 12;
    }
    else if (event.contains(event13string)) {
        eventType = 13;
    } 
}

void serialEvent( Serial behavSerPort) {

    if (behavSerPort.available() > 0) {  // when serial data is sent from Arduino (when the animal does something)
    // read serial data of trigger times (since start of this script) from Arduino   
    event = behavSerPort.readStringUntil('\n');  // use readStringUntil() to make sure we get entire serial package
    // Write the Arduino data to a file
    output.print(event);  // write the output to .txt file as string (will just be number in text)
    print(event);  // print trigger times to this display
    
    // parse and plot things from incoming strings
    if (toPlot == 1) {
      if (int(event) == 0) {  // if this serial data is an event type
        parseString();
      } // end IF event is a string (prob not necessary now)    
    } // end IF to plot event data
    //      output.println(time);  // uncomment to also output Processing time
  }  // end IF for behavSerPort.available

}

void checkFilename() {
   String path = sketchPath();
   File file = new File(path);// + "/data");
   String names[]=file.list();
   //printArray(names);
   String dataFilename = animal + ".png"; // only checks for completed session with .png plot image file
   //println(dataFilename);
   for (int i=0;i<names.length;i++) {
     String thisFilename = names[i];
     if (thisFilename.equals(dataFilename)== true) {
       println("Session name " + animal + " repeated, so aborting to avoid copying over previous.");
       exit(); 
       //check = 0;
       //return check;
     }
   }
 
}

///// ends program and saves output TXT (and graph)  
void keyPressed() {
  if (key=='q') {
  endSession();
  }
}  // end keyPressed

void endSession() {
  h = hour();
  m = minute();
  output.println("END SESSION");
  output.print(h);
  output.print(":");
  if (m<=9) {
   output.println("0"+m); 
  }
  else {
  output.println(m);
  } 
  
  output.flush(); // Write the remaining data
  output.close(); // Finish the file
  println("END SESSION"); 
  
  exit(); // Stop the program
  
}