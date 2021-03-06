#!/usr/bin/env python3
"""
Script to get sensor data from DHT22 and provide the data through a 
CoAP endpoint
"""

__author__ = "Tom Scott"

import click
import json
from socket import gethostbyname, gaierror
from time import sleep
from datetime import datetime
import types
from coapthon.client.helperclient import HelperClient
import logging
import csv
from rpicoap.sensordata import SensorData
from rpicoap.config import Config

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

def get_coap_client(config):
    """
    Procedure for creating the CoAP client.
    Attempts to get IP address for host from the host name.
    Returns CoAP HelperClient
    """
    _host = config.host

    # Try to get ip address
    try:
        tmp = gethostbyname(_host)
        _host = tmp
    except gaierror:
        # use domain if cannot get ip
        pass

    # create CoAP client
    return HelperClient(server=(_host, config.port))

def send_data(sensor_data, client, path, verbose):
    """
    Takes a SensorData object as an argument,
    formats the data to JSON and sends to
    ThingsBoard CoAP endpoint.
    """
    # Format the data to JSON to be sent
    payload = sensor_data.as_json()
    # Send POST message with payload to endpoint
    response = client.post(path, payload)

    # Print data transmitted
    if verbose:
        click.echo(str(datetime.now()) + '\tData sent:\t' + str(sensor_data))

def send_test_data(file, client, path, verbose, sleep_interval):
    """
    Reads data from csv file passed at the command line and sends
    the data to the CoAP endpoint in the configuration file.
    Data is expected to be in the format humidity,temperature and
    can optionally contain a header row.
    """
    print('Sending data from file: {}'.format(file))

    with open(file, 'r') as data_file:
        # check for header
        has_header = csv.Sniffer().has_header(data_file.read(1024))

        # rewind
        data_file.seek(0)

        # skip headers
        if has_header:
            next(data_file)

        # read data into ordered dictionary using fieldnames
        # read all non quoted fields as floats
        csv_reader = csv.DictReader(data_file, 
                                    fieldnames=('humidity', 'temp'),
                                    quoting=csv.QUOTE_NONNUMERIC)
        
        # send the test data to coap endpoint
        for row in csv_reader:
            send_data(SensorData(row['humidity'], row['temp']), 
                      client, 
                      path, 
                      verbose)

            # Wait specified time and repeat
            sleep(sleep_interval)

@click.command()
@click.option('-e', '--edit', is_flag=True, help='open config file')
@click.option('-v', '--verbose', is_flag=True, help='show data transmitted')
@click.option('-f', '--file', type=str, help='csv file to use as data\nExpects humidity,temperature format.')
def main(edit, verbose, file):
    """ Main entry point of the app """

    # Get configuration file
    config = Config()

    # If edit flag is passed open config file and exit program
    if edit:
        config.open()
        exit()

    # Print information about adafruit library loading
    click.echo(LIBRARY_MESSAGE)

    # Create a CoAP client
    client = get_coap_client(config)

    try:
        print('Starting CoAP server.\nPress Ctrl + C to stop.')

        # Send test data if provided
        if file:
            send_test_data(file, client, config.path, verbose, config.sleep_interval)
        # Else read from sensor
        else:
            while True:
                # Note that sometimes you won't get a reading and
                # the results will be null (because Linux can't
                # guarantee the timing of calls to read the sensor).
                sensor_data = get_sensor_data(
                    sensor_lib.AM2302,
                    config.gpio_pin)

                if sensor_data.has_data():
                    # Format the data to JSON to be sent
                    send_data(sensor_data, client, config.path, verbose)
                    # client.send_data(sensor_data)
                
                # Wait specified time and repeat
                sleep(config.sleep_interval)

    # Allow Ctrl + C to stop the script
    except KeyboardInterrupt:
        click.echo("Interrupted by keyboard, stopping client")
    except ValueError as config_error:
        click.echo(config_error)
    finally:
        client.stop()
        exit(0)