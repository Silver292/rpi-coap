#!/usr/bin/env python3
"""
Script to get sensor data from DHT22 and provide the data through a 
CoAP endpoint
"""

__author__ = "Tom Scott"

import Adafruit_DHT
from json import dumps
from socket import gethostbyname, gaierror
from time import sleep

from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri

_SENSOR = Adafruit_DHT.AM2302
_GPIO_PIN = 4
HOST = "demo.thingsboard.io"
DEVICE_AUTH_TOKEN = "9tQn151djuEdRX0ucu0k"
PORT = 5683 # Default CoAP port
SLEEP_INTERVAL = 5

class SensorData(object):
    """
    Data object containing humidity and temperature data.
    """

    def __init__(self, humidity, temperature):
        """
        Set humidity and temperature
        """
        self.humidity = humidity
        self.temperature = temperature

    def has_data(self):
        """
        Returns True if humidity and temperature are not None.
        """
        return self.humidity is not None and \
               self.temperature is not None

    def as_json(self):
        """
        Returns the humidity and temperature data as a JSON string.
        """
        return dumps({'humidity': self.humidity, \
                'temperature': self.temperature})

    def __str__(self):
        humidity_string = 'Humidity={0:.1f}%'.format(self.humidity)
        temperature_string = 'Temp={0:.1f}*C'.format(self.temperature)
        return humidity_string + ' ' + temperature_string

def get_sensor_data():
    """
    Returns a SensorData object containing the latest data 
    from the DHT22 sensor.
    The method will 15 times to get data, if there is still no 
    data available it will return an empty SensorData object
    """

    # Try to grab a sensor reading.  Use the read_retry method 
    # which will retry up to 15 times to get a sensor reading 
    # (waiting 2 seconds between each retry).
    humidity, temperature = Adafruit_DHT.read_retry(_SENSOR, _GPIO_PIN)

    return SensorData(humidity, temperature)

def main():
    """ Main entry point of the app """

    # build endpoint URI to ThingsBoard platform
    path = "api/v1/" + DEVICE_AUTH_TOKEN + "/telemetry"

    # create CoAP client
    client = HelperClient(server=(HOST, PORT))

    try:
        while True:

            # Note that sometimes you won't get a reading and
            # the results will be null (because Linux can't
            # guarantee the timing of calls to read the sensor).
            sensor_data = get_sensor_data()

            if sensor_data.has_data():
                print(sensor_data)
                payload = sensor_data.as_json()
                print(payload)
                response = client.post(path, payload)
                print(response.pretty_print())
            
            sleep(SLEEP_INTERVAL)

    except KeyboardInterrupt:
        print("Interrupted by keyboard, stopping client")
        client.stop()
        exit(0)

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()