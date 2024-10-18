#include <Wire.h>
#include <WiFi101.h>
#include <WiFiUdp.h>
#include <LSM6.h>
#include <WiFiUdp.h>
#define JUMPS_NUM_SEND 10 //number of previous jumps that udp packets send to pc 
#define SAVED_JUMPS 30 //number of jumps saved on the microcontroller
#define SENSOR_ID 6 
#define VBATPIN A7
#define SEND_TIME  1000 //time between sending packets in millis

//SPREMEMBE !!!!!!!!!!, MEJE FILTRIRANEGA PRED SKOKOM (0.8 - 1.4), BOUNDARY ZA SKOKE Z UDARCEM(PREJ NA 3,7), JERK (3,7), 

//function declarations
void updatePayload(char buff[20 + JUMPS_NUM_SEND*21], char *newVal);
void packetInfo(char buff[21 + JUMPS_NUM_SEND*21], unsigned long packetTime, char ID, int bat);
void fifoUpdate(float *arr, int len, float newVal);
void sendPacket(IPAddress& address);
void printWiFiStatus();


// Sensor define
const int chipSelect = 4;
LSM6 imu;

// WiFi define
int status = WL_IDLE_STATUS;

//wifi network data
char ssid[] = "Marko_access_point";         
char pass[] = "Andrswnk1*";


unsigned int localPort = 2390;      // local port to listen for UDP packets

IPAddress UDPServer(192, 168, 0, 50); // test server dd-wrt to P52S
//IPAddress UDPServer(192,168,10,196);

// A UDP instance to let us send and receive packets over UDP
WiFiUDP Udp;


//payload, size is Deviceid -> 2 + 2 only once , packet timestamp -> 2 + 8  only once together = 14 ;;;; , jump id 2 + 3, jump timestamp 2 + 8, fly time 2 + 4, together = 21
char payload[20 + JUMPS_NUM_SEND*21];


void setup() {
 
  for(int k = 0; k < 20 + JUMPS_NUM_SEND*21; k++){
  payload[k] = ' ';
}
  //Configure pins for Adafruit ATWINC1500 Feather
  WiFi.setPins(8, 7, 4, 2);

   Wire.begin();
  pinMode(10, OUTPUT);

 
  // Set the I2C Clock speed to 0.4 MHz
  Wire.setClock(400000);
  if (!imu.init())
  {
    Serial.println("Failed to detect and initialize IMU!");
    while (1);
  }

  imu.enableDefault();

  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue:
    while (true);
  }
  // attempt to connect to WiFi network:
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);
    Serial.println(status);
    // wait 5 seconds for connection:
    delay(5000);
  }

  Serial.println("Connected to wifi");
  printWiFiStatus();

  Serial.println("\nStarting connection to server...");
  Udp.begin(localPort);

}

//absolute acceleration
float a;


char newVal[22];

//matrix for saved values 30 previous jumps: jumpid, jumptime, jump height 
int jumpIDs[SAVED_JUMPS] = {0};
int jumpFlightTimes[SAVED_JUMPS] = {0};
unsigned long jumpTimes[SAVED_JUMPS];

//time of jump
int flightTime = 0;

//jump counter
int counter = 1;

//timer for elimenating errors because of fluctuations
int timer = 0;
//state before the jump event, this state is used for the state machine
int jump = 0;

//jump start time
unsigned long startTime;
unsigned long endTime;


//sampling
unsigned long startTimeSampling = 0;
unsigned long endTimeSampling = 0;
int samplingTime = 5;

//moving average
float movAvg = 0;
//prevVal for calculating moving average
float prevVal[10] = {0};
//buffer for storing previous values
//you have to go back 215 in ms
//length is 215/samplingTime
float prevValMovAvg[45] = {0};
int tmpCnt = 0;

//bool to validate takeoff
bool validBeforeState = true;

//bool to validate landing 
bool validLandState = true;

//jerk = accel derivative
float jerk = 0;
//for only reading takoff time once 
bool firstTime = true;

//avgacc during flight depending on the begining of the flight the boundary is chosen
float boundary = 3;
bool decisionMade = false;

//timers for sending packets every 5s
long unsigned sendStartTime = 0;
long unsigned sendEndTime = 0;

int Vbat;

void loop() {
  if(WiFi.status()==6){
    status = WL_IDLE_STATUS;
      while ( status != WL_CONNECTED) {
        Serial.print("Attempting to connect to SSID: ");
        Serial.println(ssid);
        // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
        status = WiFi.begin(ssid, pass);
        Serial.println(status);
        // wait 5 seconds for connection:
        delay(5000);
  }
   Serial.println("Connected to wifi");
  printWiFiStatus();

  Serial.println("\nStarting connection to server...");
  Udp.begin(localPort);
    
  }
 
  
  endTimeSampling = millis();
  
  //sampling
  if (endTimeSampling - startTimeSampling >= samplingTime){
    startTimeSampling = endTimeSampling;
  

  //reading and calculating absolute acceleration
    Vbat = analogRead(VBATPIN);
  
    imu.read();
    a = sqrt(sq(imu.a.x) + sq(imu.a.y) + sq(imu.a.z));
   
    a = a/2060;

    //moving average for last 10 samples
    if(tmpCnt > 10){
      movAvg = 0;
      for(int i = 0; i < 10; i++){
        movAvg += prevVal[i];
      }
      movAvg /= 10; 
    }

    //jerk, tmpCnt > 1 to not go into negative indices
    if(tmpCnt > 1){
      jerk = (a - prevVal[0])/(samplingTime/10.0); //10 is not important just to get values around 1 -10
      
    }

    //remember the first time when the acc > 5 - for more correct height
    if(a >= 6 && jump == 0 && timer > 100 && validBeforeState == true && firstTime == true){
       startTime = millis();
       firstTime = false;
       
    }

    //if it takes the jerk to long to be high enough go back
    if(firstTime == false && (millis() - startTime) > 20){
      firstTime = true;
    }

    //go to takeoff state, acc has to be high enough, before jump avgacc had to be quite constant
    if(a >= 6 && jump == 0 && timer > 100  && validBeforeState == true && jerk >= 1){
      jump = 1;
      //startTime = millis();
      timer = 0;
      firstTime = true;
      decisionMade = false;
    }

    //when acc is low enough go from tekoff to fly state
    else if (a <= 6 && jump == 1 && timer > 30){
      jump = 2;
      timer = 0;
    }

    //go from fly to landing state, acc has to be high, jerk has to be high
    else if (a >= 10 && jump == 2 && timer > 200 && jerk >= 3){
      jump = 3;
      //flight time is current time(landing) - the time when event was triggered
      endTime = millis();
      flightTime = endTime - startTime;
      timer = 0;

      //avg before landing has to be quite low, go 3 samples back and check 40 samples before that
      validLandState = true;
      for(int j = 3; j < 43; j++){
        if (prevValMovAvg[j] > boundary){
          //bool which has to be true for the jump to count
          validLandState = false;
        }
      }
    }
    //go from landing to before jump state, acc has to be low enough
    else if (a <= 2 && jump == 3 && timer > 30){
        
        
         //update the buffers for saved jumps
         fifoUpdateInt(jumpIDs, SAVED_JUMPS,counter);
         fifoUpdateInt(jumpFlightTimes, SAVED_JUMPS,flightTime);
         fifoUpdateUnLong(jumpTimes, SAVED_JUMPS,endTime);
        
         //write the last jump into the buffer for sending
          snprintf(newVal, sizeof(newVal), "JI%3dJT%8dFT%4d", counter, endTime, flightTime);
          updatePayload(payload, newVal);
          //pošlji ob eventu
           packetInfo(payload, millis(), SENSOR_ID, Vbat);
             sendPacket(UDPServer);
        
        //increase jump counter
        counter++;
        //go to before state
        jump = 0;
        timer = 0;
    }
  
  //if jump is longer that 1.1s -- too long 
    if(jump == 2 && millis() - startTime > 1100){
      jump = 0;
      
    }

  //if landing takes to long it's not a jump
  if (jump == 3 && timer > 100){
    jump = 0;
    timer = 0; 
  }

   //if takeoff takes too long, it is not a jump
    if (jump == 1 && timer > 200){
        jump = 0;
        timer = 0;
    }

//if during first part of fly avgacc is high, set  the limit for second part of fly higher
if (jump == 2 && decisionMade == false){
  if(timer < 150 and timer > 50 && movAvg > 5){
    boundary = 7;
    decisionMade = true;
  }
  boundary = 3;
}
 
  
    timer = timer + samplingTime;
  
    //write values into buffers
    fifoUpdate(prevVal, 10, a);
    fifoUpdate(prevValMovAvg, 45, movAvg);
    tmpCnt++;
  }

//checking if the filtered signal is withing boundaries before takeoff
  if(jump == 0){
    validBeforeState = true;
    //go back for 80 ms -> 20 samples, start 15ms before takeoff - 3 samples
    for(int j = 3; j <= 3 + 20; j++){
      if(prevValMovAvg[j] < 0.6 || prevValMovAvg[j] > 1.6){
        validBeforeState = false;
      }
    }
  }
sendEndTime = millis();

  //sending packet every 5 seconds
  if(sendEndTime - sendStartTime > SEND_TIME){

    //appending packet specific information
    packetInfo(payload, millis(), SENSOR_ID, Vbat);
    sendPacket(UDPServer);
    sendStartTime = sendEndTime;

    for(int i = 0; i < 30; i++){
    Serial.print(jumpFlightTimes[i]);
  }
  Serial.println("");
  }



  
  
}


//updating payload buffer, 5 jumps  
void updatePayload(char buff[21 + JUMPS_NUM_SEND*21], char *newVal){
    for(int i = 1; i < JUMPS_NUM_SEND; i++){
       for(int j = 0; j < 21; j++){
          buff[(i-1)*21 + j+ 20] = buff[i*21 + j+ 20];
          
       }
    }
     for(int j = 0; j < 21; j++){
          buff[j+ JUMPS_NUM_SEND*21 -1] = newVal[j];
          
       }
}

//for packet specific information
void packetInfo(char buff[21 + JUMPS_NUM_SEND*21], unsigned long packetTime, char ID,int bat){
  char newVal[21];
  snprintf(newVal, sizeof(newVal), "BT%4dID%2dTP%8d",bat ,ID, packetTime);
  for(int i = 0; i < 20; i++){
    buff[i] = newVal[i];
  }
}

//function to ensure first in first out
void fifoUpdate(float *arr, int len, float newVal){
    for(int i = len-2; i >= 0; i--){
      arr[i + 1] = arr[i];
    }
    arr[0] = newVal;
}

void fifoUpdateInt(int *arr, int len, int newVal){
    for(int i = len-2; i >= 0; i--){
      arr[i + 1] = arr[i];
    }
    arr[0] = newVal;
}

void fifoUpdateUnLong(unsigned long *arr, int len, unsigned long newVal){
    for(int i = len-2; i >= 0; i--){
      arr[i + 1] = arr[i];
    }
    arr[0] = newVal;
}



//send packet to ip adress in network
void sendPacket(IPAddress& address)
{
  
  Udp.beginPacket(address, 2000); //requests are to port 2000
  Udp.write(payload, sizeof(payload));
  Udp.endPacket();
  Serial.println(payload);
}


void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}
