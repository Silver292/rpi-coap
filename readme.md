# Raspberry Pi Sensor to ThingsBoard using Constrained Application Protocol <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->
- [Introduction](#introduction)
- [Installation](#installation)
  - [Connecting the sensor](#connecting-the-sensor)
  - [Downloading the script](#downloading-the-script)
  - [Configuration](#configuration)
  - [Config.ini](#configini)
- [Usage](#usage)
  
## Introduction

This script is designed to be run on Raspberry Pi 3 Model B hardware running the Raspbian 9.6 operating system. It is also assumed that a DHT22 temperature and humidity sensor is connected to the Raspberry Pi (RPi) using GPIO 4 pin. The process of connecting the sensor is described [here](#connecting-the-sensor).

The script creates a Constrained Application Protocol (CoAP) client on the RPi and repeatedly polls the attached DHT22 sensor for temperature and humidity data. This data is then formatted to JavaScript Object Notation (JSON) and is sent to a CoAP endpoint provided by the ThingsBoard Cloud Platform. This data is then displayed on the ThingsBoard dashboard that shows the current temperature and humidity as well as historical readings in a graph form.

## Installation

### Connecting the sensor

![Diagram showing sensor connection to RPi](https://user-images.githubusercontent.com/5542588/52054623-0c47f100-2555-11e9-8996-eca1224aa146.png)

To connect the DHT22 sensor to the RPi:

  1. Connect the ``-`` output on the sensor the pin 6 on the RPi.
  2. Connect the ``+`` input on the sensor to pin 2 on the RPi.
  3. Connect the ``output`` pin on the sensor to pin 7 on the RPi.

### Downloading the script

Clone the repository:
```bash
$ git clone https://github.com/Silver292/rpi-coap.git
$ cd rpi-coap/
```
Create a virtual environment if needed:

```bash
$ virtualenv .env
$ source .env/bin/activate
```

Install the application:

```bash
$ pip install .
```

Application is run using:

```bash
$ rpicoap
```

### Configuration

Settings are kept in the ``config.ini`` file. You can copy ``config.ini.example`` to create your own or this file will be created the first time you run the script.

Most of the default settings should be fine, unless you are using a different GPIO port on the Raspberry Pi.

You will need to update the ``host`` and ``device_auth_token`` settings in the ``config.ini``. 
These can be retrieved from the Thingsboard you wish to send the sensor data to.

![Where to get auth token](https://user-images.githubusercontent.com/5542588/52054622-0c47f100-2555-11e9-82c7-e7303507d851.png)

The auth token can be obtained by clicking the button highlighted in yellow above.

### Config.ini


``SLEEP_INTERVAL = 5``  - Amount of time between each sensor reading and sending of data.

``GPIO_PIN = 4`` - GPIO pin on the RPi used to connect to the DHT22 sensor. Defaults to 4, shown in [installation](#connecting-the-sensor).

``PORT = 5683`` - Port for CoAP endpoint, defaults to 5683.

``HOST = demo.thingsboard.io`` - Host of the Thingsboard. Defaults to using the Thingsboard live demo.

``DEVICE_AUTH_TOKEN =`` - Auth token for device. This is retrieved from the Thingsboard devices section.

## Usage

To start recording and sending data to the Thingsboard platform run:

```bash
$ rpi-coap
```

To stop the script press ``Ctrl + Z``.
