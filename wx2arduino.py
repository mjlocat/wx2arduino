import json
import math
import os
import time
from dotenv import load_dotenv
import mysql.connector
import serial

def getEnvironment():
    load_dotenv()


def getData(cnx, query):
    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    return result[0]


def main():
    getEnvironment()
    tempquery = "SELECT temperature FROM temperature ORDER BY id DESC LIMIT 1"
    windquery = "SELECT windspeed FROM windspeed ORDER BY id DESC LIMIT 1"
    humidityquery = "SELECT humidity FROM humidity ORDER BY id DESC LIMIT 1"
    rainquery = "SELECT rain FROM rain ORDER BY id DESC LIMIT 1"
    dbconfig = {
        'user': os.getenv('DBUSER'),
        'password': os.getenv('DBPASS'),
        'host': os.getenv('DBHOST'),
        'database': os.getenv('DBDATABASE')
    }
    cnx = mysql.connector.connect(**dbconfig)
    ser = serial.Serial(os.getenv("SERIAL_PORT"))
    
    while True:
        temperature = getData(cnx, tempquery)
        windspeed = getData(cnx, windquery)
        humidity = getData(cnx, humidityquery)
        rain = getData(cnx, rainquery)

        result = {
            "T": "{:3d}".format(math.trunc(temperature)),
            "W": "{:2d}".format(math.trunc(windspeed)),
            "H": "{:3d}".format(humidity),
            "R": "{:2d}".format(rain)
        }

        ser.write(json.dumps(result).encode('utf-8'))
        cnx.commit() # Results get cached without this
        time.sleep(float(os.getenv("REFRESH")))

if __name__ == "__main__":
    main()
