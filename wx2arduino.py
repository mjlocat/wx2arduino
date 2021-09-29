from datetime import datetime
import json
import math
import os
import time
from dotenv import load_dotenv
import mysql.connector
from scipy.signal import medfilt
import serial

rainquery = "SELECT rain FROM rain WHERE ts BETWEEN %(mints)s AND %(maxts)s GROUP BY rain, ts ORDER BY ts"
window_size = 5

def getEnvironment():
    load_dotenv()


def getData(cnx, query):
    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    return result[0]


def get_rain_last_hour(cnx):
    timestamp = datetime.now().timestamp()
    data = {
        'mints': timestamp - 3600,
        'maxts': timestamp
    }
    cursor = cnx.cursor()
    cursor.execute(rainquery, data)
    readings = []
    row = cursor.fetchone()
    while row is not None:
        readings.append(row[0])
        row = cursor.fetchone()

    cursor.close()
    if len(readings) < window_size:
        return None

    smooth_readings = medfilt(readings, window_size)

    count = 0
    last = smooth_readings[0]
    for reading in smooth_readings:
        if last < reading:
            count = count + (reading - last)
            last = reading
        elif last > 900 and reading < 100:
            count = count + (100 + reading - last)
            last = reading
        elif last > reading:
            # Bad reading in there, bail out
            return None

    return count/100


def main():
    getEnvironment()
    tempquery = "SELECT temperature FROM temperature ORDER BY id DESC LIMIT 1"
    windquery = "SELECT windspeed FROM windspeed ORDER BY id DESC LIMIT 1"
    humidityquery = "SELECT humidity FROM humidity ORDER BY id DESC LIMIT 1"
    dbconfig = {
        'user': os.getenv('DBUSER'),
        'password': os.getenv('DBPASS'),
        'host': os.getenv('DBHOST'),
        'database': os.getenv('DBDATABASE')
    }
    cnx = mysql.connector.connect(**dbconfig)
    try:
        ser = serial.Serial(os.getenv("SERIAL_PORT"))
    except serial.SerialException:
        print("Unable to open port")
        cnx.close()
        exit(1)
    
    while True:
        temperature = getData(cnx, tempquery)
        windspeed = getData(cnx, windquery)
        humidity = getData(cnx, humidityquery)
        rain = get_rain_last_hour(cnx)
        if rain is None:
            rain = 0

        result = {
            "T": "{:d}".format(math.trunc(temperature)),
            "W": "{:d}".format(math.trunc(windspeed)),
            "H": "{:d}".format(humidity),
            "R": "{:1.2f}".format(rain)
        }

        try:
            ser.write(json.dumps(result).encode('utf-8'))
        except serial.SerialException:
            cnx.close()
            exit(1)

        cnx.commit() # Results get cached without this
        time.sleep(float(os.getenv("REFRESH")))

if __name__ == "__main__":
    main()
