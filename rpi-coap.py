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
from socket import gethostbyname, gaierror

from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri

_SENSOR = Adafruit_DHT.AM2302
_GPIO_PIN = 4
_HOST = "demo.thingsboard.io"
_DEVICE_AUTH_TOKEN = "9tQn151djuEdRX0ucu0k"
_PORT = 5683 # Default CoAP port
_SLEEP_INTERVAL = 5

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

def get_coap_client():
    """
    Procedure for creating the CoAP client.
    Attempts to get IP address for host from the host name.
    Returns CoAP HelperClient
    """
    host = _HOST

    # Try to get ip address
    try:
        tmp = gethostbyname(host)
        host = tmp
    except gaierror:
        # use domain if cannot get ip
        pass

    # create CoAP client
    return HelperClient(server=(host, _PORT))

def send_data(sensor_data, client, path):
    """
    Takes a SensorData object as an argument,
    formats the data to JSON and sends to
    ThingsBoard CoAP endpoint.
    """
    # Format the data to JSON to be sent
    payload = sensor_data.as_json()
    # Send POST message with payload to endpoint
    response = client.post(path, payload)
    # Print response from cloud to console
    print(response.pretty_print())

def main():
    """ Main entry point of the app """

    # Create path that the data will be sent to
    path = "api/v1/" + _DEVICE_AUTH_TOKEN + "/telemetry"
    # Create a CoAP client
    client = get_coap_client()

    try:
        while True:

            # Note that sometimes you won't get a reading and
            # the results will be null (because Linux can't
            # guarantee the timing of calls to read the sensor).
            sensor_data = get_sensor_data()

            if sensor_data.has_data():
                # Format the data to JSON to be sent
                send_data(sensor_data, client, path)
            
            # Wait specified time and repeat
            sleep(_SLEEP_INTERVAL)

    # Allow Ctrl + C to stop the script
    except KeyboardInterrupt:
        print("Interrupted by keyboard, stopping client")
        client.stop()
        exit(0)

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()