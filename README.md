# wx2arduino
Weather information to Arduino display

## Prerequisites

* python3 and pip3
* The [WeatherStation](https://github.com/mjlocat/WeatherStation) project running and writing weather data to a database

## Required Hardware

* [Arduino Uno](https://store.arduino.cc/usa/arduino-uno-rev3)
* [OSEPP LCD Keypad Shield](https://www.osepp.com/electronic-modules/shields/45-16-2-lcd-display-keypad-shield)
* USB Cable

## Required Arduino Libraries

* LCDKeypad for [OSEPP LCD Keypad Shield](https://www.osepp.com/electronic-modules/shields/45-16-2-lcd-display-keypad-shield)
* [ArduinoJson](https://arduinojson.org/)

## Hardware Setup

1. Plug the OSEPP LCD Keypad Shield into the Arduino Uno
1. Plug the USB cable into the Arduino Uno and your computer
1. Open the Arduino IDE and load the `wx2arduino/wx2arduino.ino` sketch
1. Upload the sketch to the Arduino Uno

## Sofrware Setup

1. Clone the repo and change into the project directory
1. Install the required libraries
    ``` shell
    pip3 install -r requirements.txt
    ```
1. Copy the `env.sample` file to `.env` and edit the file as specified
    ``` shell
    cp env.sample .env
    vi .env
    ```
1. Run the `wx2arduino.py` program
    ``` shell
    python3 wx2arduino.py
    ```
