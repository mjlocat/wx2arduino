#include <LiquidCrystal.h>
#include <LCDKeypad.h>
#include <ArduinoJson.h>
#include <string.h>

#define T 3,0
#define W 10,0
#define H 3,1
#define R 10,1
#define LEN1 4
#define LEN2 6
#define BUF_SIZE 512
#define FILL " "

LCDKeypad lcd;
String buf;
StaticJsonDocument<BUF_SIZE> doc;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  lcd.begin(16,2);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.write("T:     W:");
  lcd.setCursor(0,1);
  lcd.write("H:     R:");

  
}

void loop() {
  if (Serial.available() > 0) {
    buf = Serial.readString();
    deserializeJson(doc, buf);
    lcd.setCursor(T);
    lcd.write(doc["T"].as<char*>());
    for (int i=0; i < LEN1 - strlen(doc["T"].as<char*>()); i++) {
      lcd.write(FILL);
    }
    lcd.setCursor(W);
    lcd.write(doc["W"].as<char*>());
    for (int i=0; i < LEN2 - strlen(doc["W"].as<char*>()); i++) {
      lcd.write(FILL);
    }
    lcd.setCursor(H);
    lcd.write(doc["H"].as<char*>());
    for (int i=0; i < LEN1 - strlen(doc["H"].as<char*>()); i++) {
      lcd.write(FILL);
    }
    lcd.setCursor(R);
    lcd.write(doc["R"].as<char*>());
    lcd.write("\"");
    for (int i=0; i < LEN2 - strlen(doc["R"].as<char*>()) - 1; i++) {
      lcd.write(FILL);
    }
    doc.clear();
  }
}

// {"T":" 47","W":" 0","H":" 77","R":"0.00"}
