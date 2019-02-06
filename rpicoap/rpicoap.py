#!/usr/bin/env python3
"""
Script to get sensor data from DHT22 and provide the data through a 
CoAP endpoint
"""

__author__ = "Tom Scott"

import click
from json import dumps
from socket import gethostbyname, gaierror
from time import sleep
import configparser
from shutil import copy
import os
import types
import pkg_resources
import subprocess
import sys
from coapthon.client.helperclient import HelperClient
import logging

# Set default logging level for imported module
logging.getLogger('coapthon').setLevel(logging.WARNING)

# load Adafruit library if available (on RPi) else load mocks
try:
    import Adafruit_DHT as sensor_lib
    LIBRARY_MESSAGE = 'Adafruit library found - data will be sent from sensor.'
except ImportError:
    # If running on windows create a mock library
    LIBRARY_MESSAGE = 'Adafruit library not found; creating mock library.'
    LIBRARY_MESSAGE += '\nData sent is test data - not from sensor.'
    # Create a mock static method to return test data, 
    # this will always return 20% humidity and 25C temperature
    sensor_lib = types.SimpleNamespace(
        read_retry = lambda sensor, gpio_pin: (20, 25),
        AM2302 = 1)



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

def get_sensor_data(sensor, gpio_pin):
    """
    Returns a SensorData object containing the latest data 
    from the DHT22 sensor.
    The method will 15 times to get data, if there is still no 
    data available it will return an empty SensorData object.
    If the Adafruit library is not installed, 
    mock results will be returned.
    """

    # Try to grab a sensor reading.  Use the read_retry method 
    # which will retry up to 15 times to get a sensor reading 
    # (waiting 2 seconds between each retry).
    humidity, temperature = sensor_lib.read_retry(sensor, gpio_pin)

    return SensorData(humidity, temperature)

def get_coap_client(host, port):
    """
    Procedure for creating the CoAP client.
    Attempts to get IP address for host from the host name.
    Returns CoAP HelperClient
    """
    _host = host

    # Try to get ip address
    try:
        tmp = gethostbyname(_host)
        _host = tmp
    except gaierror:
        # use domain if cannot get ip
        pass

    # create CoAP client
    return HelperClient(server=(_host, port))

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
    click.echo(response.pretty_print())

@click.command()
@click.option('--edit', is_flag=True, help='open config file')
def main(edit):
    """ Main entry point of the app """

    # Get configuration file
    config = get_config(edit)

    # Print information about adafruit library loading
    click.echo(LIBRARY_MESSAGE)

    # Create path that the data will be sent to
    auth_token = config.get('custom', 'device_auth_token')

    # Raise an error if the auth token is not defined in config file
    if not auth_token:
        raise ValueError('Device auth token not present, please update config.ini by running rpicoap --edit')

    path = "api/v1/" + auth_token + "/telemetry"

    # Create a CoAP client
    client = get_coap_client(
        config.get('custom', 'host'),
        config.getint('custom', 'port'))

    # Make sure sleep interval is at least one second
    sleep_interval = config.getint('custom', 'sleep_interval')
    sleep_interval = sleep_interval if sleep_interval >= 1 else 1 

    try:
        while True:

            # Note that sometimes you won't get a reading and
            # the results will be null (because Linux can't
            # guarantee the timing of calls to read the sensor).
            sensor_data = get_sensor_data(
                sensor_lib.AM2302,
                config.getint('custom', 'gpio_pin'))

            if sensor_data.has_data():
                # Format the data to JSON to be sent
                send_data(sensor_data, client, path)
            
            # Wait specified time and repeat
            sleep(sleep_interval)

    # Allow Ctrl + C to stop the script
    except KeyboardInterrupt:
        click.echo("Interrupted by keyboard, stopping client")
        client.stop()
        exit(0)

def get_config(edit):
    """
    Gets the config settings form config.ini
    if config.ini does not exist, create config.ini
    from example file.
    """
    # get example file from package
    config_example = pkg_resources.resource_filename(__name__, "config.ini.example")
    config_ini = os.path.join(os.path.dirname(config_example), 'config.ini')

    # Check of config.ini exists
    if not os.path.exists(config_ini):
        # if example exists, copy to config.ini
        if os.path.exists(config_example):
            copy(config_example, config_ini)
            click.echo('Created config.ini at {}'.format(config_ini))
        else:
            # Error, no example or config found
            raise FileNotFoundError('No config.ini or config.ini.example found.')
        
    # If edit flag is passed at the command line open the config
    # file with the default text editor for the OS
    if(edit):
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', config_ini))
        elif os.name == 'nt': # For Windows
            os.startfile(config_ini)
        elif os.name == 'posix': # For Linux, Mac, etc.
            subprocess.call(('vi', config_ini))
        exit()

    # create the config dictionary
    config = configparser.ConfigParser()
    config.read(config_ini)
    return config
