#!/usr/bin/env python3
"""
Script to get sensor data from DHT22 and provide the data through a 
CoAP endpoint
"""

__author__ = "Tom Scott"

import Adafruit_DHT
import json

_SENSOR = Adafruit_DHT.AM2302
_GPIO_PIN = 4

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
        return json.dumps({'humidity': self.humidity, \
                'temperature': self.temperature})

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

    # Note that sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).
    sensor_data = get_sensor_data()

    if sensor_data.has_data():
        humidity_string = f'Humidity={sensor_data.humidity:.1f}%'
        temperature_string = f'Temp={sensor_data.temperature:.1f}*'
        print(humidity_string + ' ' + temperature_string)
        print(sensor_data.as_json())


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()