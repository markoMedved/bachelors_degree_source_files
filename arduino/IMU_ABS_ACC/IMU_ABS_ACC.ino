/*
FSFV0@AU_v1 10.januar 2020
WiFi UDP IMU: ACC+GYRO+MAG , TEMP , BATT 

 */
 
#include <Wire.h>
#include <SPI.h>
#include <WiFi101.h>
#include <WiFiUdp.h>
#include <LSM6.h>
//#include <LIS3MDL.h>   
//magnetometer exc.!!


#define OUT_TEMP_L = 0x20
#define OUT_TEMP_H = 0x21

// Sensor define
const int chipSelect = 4;
LSM6 imu;
//LIS3MDL mag;
//vključitev magnetometra

// variable define
int counter;
int samplingTime;  //sampling time in microseconds
int startTime;
int endTime;

int AA1;


// WiFi define
int status = WL_IDLE_STATUS;

//char ssid[] = "SensorLog";  //  your network SSID (name)
//char pass[] = "SensorLog";       // your network password
//char ssid[] = "dd-wrt";         //  your network SSID (name)
//char pass[] = "e1t2m3m4n5";       // your network password
//char ssid[] = "Marko_access_point";         
//char pass[] = "Andrswnk1*";
char ssid[] = "LaIT";         
char pass[] = "lait1po2zraku3";


//char ssid[] = "Hotspot-Biofeedback";         //  your network SSID (name)
//char pass[] = "Biofeedback";       // your network password

//char ssid[] = "Hotspot-BF-Golf";         //  your network SSID (name)
//char pass[] = "Biofeedback-Golf";       // your network password

//char ssid[] = "TONEUmhs";         //  your network SSID (name)
//char pass[] = "tsetn2024";       // your network password


//char ssid[] = "SENSORLOG";  //  your network SSID (name)
//char pass[] = "SensorLog2";       // your network password

int keyIndex = 0;            // your network key Index number (needed only for WEP)

// Network define
unsigned int localPort = 2390;      // local port to listen for UDP packets

//IPAddress UDPServer(192, 168, 1, 239); // test server SENSORLOG2 to Yoga
//IPAddress UDPServer(192, 168, 100, 102); // test server dd-wrt to ToneP52

IPAddress UDPServer(192,168,10,196); // test server dd-wrt to P52S
//IPAddress UDPServer(192, 168, 137, 1); // test to Yoga VAL
// A UDP instance to let us send and receive packets over UDP
WiFiUDP Udp;

#define VBATPIN A7

void setup()
{
  //Configure pins for Adafruit ATWINC1500 Feather
  WiFi.setPins(8,7,4,2);
 // Open serial communications and wait for port to open:
 // Serial.begin(9600);
 // while (!Serial) {
 //   ; // wait for serial port to connect. Needed for native USB port only
 // }
  
  Serial.println("Starting feather , kuku 5x");
  
  Wire.begin();
  pinMode(10, OUTPUT);
  
  // Set the I2C Clock speed to 3.4 MHz
  // Set the I2C Clock speed to 0.4 MHz
  Wire.setClock(3400000);
    
  if (!imu.init())
  {
    Serial.println("Failed to detect and initialize IMU!");
    while (1);
  }

// if (!mag.init())
// {
//   Serial.println("Failed to detect and initialize magnetometer!");
//   while (1);
// }
//  mag.enableDefault();
  imu.enableDefault();

  // check for the presence of the shield:
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

    // wait 5 seconds for connection:
    delay(5000);
  }

  Serial.println("Connected to wifi");
  printWiFiStatus();

  Serial.println("\nStarting connection to server...");
  Udp.begin(localPort);
}
// SETUP END

// Packet define
//char  payload[120];           // packet payload DEC + tekst Acc + Gyro + Mag
//char  payload[114];           // packet payload DEC + tekst Acc + Gyro
//char  payload[112];             // packet payload DEC + tekst Acc + Gyro+TEMP+BAT
//char  payload[147];             // packet payload DEC + tekst Acc + Gyro + Mag +TEMP+BAT
char  payload[50];             // abs acc payload
// START main loop
void loop()
{
   counter=0;
   startTime=millis();
   samplingTime=5000;
   int Vbat = analogRead(VBATPIN);
   for (int i=0; i < 1000; i++){
      imu.read();
      AA1=int(sqrt(sq(imu.a.x)+sq(imu.a.y)+sq(imu.a.z)));
     // mag.read();
      // Acc + Gyro + Temp + VBatt
      //snprintf(payload, sizeof(payload), "6DIMUTB T: %8d Ax: %6d Ay: %6d Az: %6d Gx: %6d Gy: %6d Gz: %6d Mx: %6d My: %6d Mz: %6d TP: %6d VB: %6d END" ,
      //snprintf(payload, sizeof(payload), "eBALL@AU_v1 T: %8d Ax: %6d Ay: %6d Az: %6d Gx: %6d Gy: %6d Gz: %6d Mx: %6d My: %6d Mz: %6d TP: %6d VB: %6d END" ,
      //snprintf(payload, sizeof(payload), "FSFV2@AU T: %8d Ax: %6d Ay: %6d Az: %6d Gx: %6d Gy: %6d Gz: %6d Mx: %6d My: %6d Mz: %6d TP: %6d VB: %6d END" ,
      snprintf(payload, sizeof(payload), "AbsAcc1 T: %8d Ax: %6d Ay: VB: %6d END" ,
        millis(),
        AA1, 
     /*   imu.a.y, imu.a.z,
        imu.g.x, imu.g.y, imu.g.z,
        imu.g.x, imu.g.y, imu.g.z,
        imu.u.x,
        */ 
        Vbat);
    //mag.m.x, mag.m.y, mag.m.z);
  delayMicroseconds(samplingTime-(micros()%samplingTime));   
   sendPacket(UDPServer); // send a packet to a server
       counter++;
   }
   endTime=millis();
}
// END main loop

void sendPacket(IPAddress& address)
{
  Serial.println(payload);
  //Serial.println("3");
   Udp.beginPacket(address,1236); //requests are to port 1234
  //Serial.println("4");
  Udp.write(payload, sizeof(payload));
  //Serial.println("5");
  Udp.endPacket();
 
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
