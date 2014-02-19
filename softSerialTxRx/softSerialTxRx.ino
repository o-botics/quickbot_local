
/*
 -------------------------------------------------------------------------------
 softSerialTxRx.ino
 QuickBot Project
 
 A simple little program to read and write serial data via soft serial.
 
 Initially created by Rowland O'Flaherty (rowlandoflaherty.com) on 05/24/2012.
 
 Version 1.0
 
 Copyright (C) 2014, Georgia Tech Research Corporation see
 the LICENSE file included with this software (see LINENSE file)
 -------------------------------------------------------------------------------
 */
 
#include <SoftwareSerial.h>
SoftwareSerial SoftSerial(2,3); // RX, TX

char incomingByte;
char outgoingByte;
int sentFlag = false;

void setup() {
    long serialBaud = 9600;
    long softSerialBaud = 9600;
    
    Serial.begin(serialBaud);
    SoftSerial.begin(softSerialBaud);
    pinMode(13, OUTPUT);
    
    Serial.println("------------------------------------");
    Serial.println("Ready to read/write from soft serial");
    Serial.print("Serial baud rate: "); Serial.println(serialBaud);
    Serial.print("Soft serial baud rate: "); Serial.println(softSerialBaud);
}

void loop() {
    while (Serial.available() > 0) {
	outgoingByte = Serial.read();
        SoftSerial.print(outgoingByte);
        Serial.print(outgoingByte);
        digitalWrite(13, HIGH);
        sentFlag = true;
    }
    if (sentFlag) {
        SoftSerial.println("");
        Serial.println("");
        sentFlag = false;
    }
    if (SoftSerial.available() > 0) {
        incomingByte = SoftSerial.read();
        Serial.print(incomingByte);
    }
}
