void setup() {
   Serial.begin(9600);
   pinMode(3, OUTPUT);
   pinMode(13, OUTPUT);
}

void loop() {
 if (Serial.available() > 0) {
    char command = Serial.read();
    
    // Check the received command
    if (command == 'H') {
      digitalWrite(3, HIGH);  // Set pin 3 to 5 volts
      digitalWrite(13, HIGH); 
      Serial.println("Pin 3 set to HIGH (5 volts)");
    } else if (command == 'L') {
      digitalWrite(3, LOW);  // Set pin 3 to 0 volts
      digitalWrite(13, LOW);
      Serial.println("Pin 3 set to LOW (0 volts)");
    }
  }
}
