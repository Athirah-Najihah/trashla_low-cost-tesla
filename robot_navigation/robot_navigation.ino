/*******************************************************************************
 * THIS SOFTWARE IS PROVIDED IN AN "AS IS" CONDITION. NO WARRANTY AND SUPPORT
 * IS APPLICABLE TO THIS SOFTWARE IN ANY FORM. CYTRON TECHNOLOGIES SHALL NOT,
 * IN ANY CIRCUMSTANCES, BE LIABLE FOR SPECIAL, INCIDENTAL OR CONSEQUENTIAL
 * DAMAGES, FOR ANY REASON WHATSOEVER.
 ********************************************************************************
 * DESCRIPTION:
 *
 * This example shows how to drive 2 motors using the PWM and DIR pins with
 * 2-channel motor driver.
 * 
 * 
 * CONNECTIONS:
 * 
 * Arduino D3  - Motor Driver PWM 1 Input
 * Arduino D4  - Motor Driver DIR 1 Input
 * Arduino D9  - Motor Driver PWM 2 Input
 * Arduino D10 - Motor Driver DIR 2 Input
 * Arduino GND - Motor Driver GND
 *
 *
 * AUTHOR   : Kong Wai Weng
 * COMPANY  : Cytron Technologies Sdn Bhd
 * WEBSITE  : www.cytron.io
 * EMAIL    : support@cytron.io
 *
 *******************************************************************************/

#include "CytronMotorDriver.h"

// Motor Driver Configuration
CytronMD motor1(PWM_DIR, 9, 10);  // Motor 1 = Pin 3, DIR 1 = Pin 4.
CytronMD motor2(PWM_DIR, 3, 5);   // Motor 2 = Pin 9, DIR 2 = Pin 10.

// Ultrasonic Sensor Configuration
const int trigPin = 6;
const int echoPin = 7;

// Motor Speed
int speed = 40;

// defines variables
long duration;
int distance;

// The setup routine runs once when you press reset.
void setup() {
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  Serial.begin(115200);
  //Serial.println("Hello");
  move_forward();
  move_backward();
}

// The loop routine runs over and over again forever.
void loop() {
  // Ultrasonic distance measurement
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;

  // Print the distance to Serial
  //Serial.println("Distance: " + String(distance));
  // Print the distance to Serialmmmm
  Serial.print("Distance: ");
  Serial.println(distance);

  // Robot navigation commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    Serial.println(command);
    if (command == "LEFT") {
      move_robot_left();
    } else if (command == "RIGHT") {
      move_robot_right();
    } else if (command == "FORWARD") {
      move_forward();
    } else if (command == "STOP") {
      stop_robot();
    } else if (command == "TURN_LEFT_AT_JUNCTION") {
      turn_left_at_junction();
    } else if (command == "TURN_RIGHT_AT_JUNCTION") {
      turn_right_at_junction();
    } else if (command == "REVERSE") {
      move_backward();
    }
  }
  delay(100);
}

void move_forward() {
  // Move both motors forward
  motor1.setSpeed(speed);
  motor2.setSpeed(speed);
  delay(1000);  // Adjust the delay as needed for the forward duration
  stop_robot();
}

void move_backward() {
  // Move both motors backward
  motor1.setSpeed(-speed);
  motor2.setSpeed(-speed);
  delay(1000);  // Adjust the delay as needed for the backward duration
  stop_robot();
}

void stop_robot() {
  // Stop both motors
  motor1.setSpeed(0);
  motor2.setSpeed(0);
}

void turn_left_at_junction() {
  // Turn left by rotating the right motor forward
  motor1.setSpeed(0);
  motor2.setSpeed(speed * 2);
  delay(1000);  // Adjust the delay as needed for the turn duration
  stop_robot();
}

void turn_right_at_junction() {
  // Turn right by rotating the left motor forward
  motor1.setSpeed(speed * 2);
  motor2.setSpeed(0);
  delay(1000);  // Adjust the delay as needed for the turn duration
  stop_robot();
}

void move_robot_left() {
  // Move left by reducing the speed of the left motor
  motor1.setSpeed(-5);
  motor2.setSpeed(speed);
  delay(1000);  // Adjust the delay as needed for the lateral movement duration
  stop_robot();
}

void move_robot_right() {
  // Move right by reducing the speed of the right motor
  motor1.setSpeed(speed);
  motor2.setSpeed(-5);
  delay(1000);  // Adjust the delay as needed for the lateral movement duration
  stop_robot();
}