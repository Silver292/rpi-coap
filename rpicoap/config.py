import os
import pkg_resources
import subprocess
import sys
import shutil

import click
import configparser

class Config(object):
    """
    Class to hold config data from rpicoap package.
    """
    def __init__(self):
        # Read the config file
        self._read_config()

    @property
    def auth_token(self):
        # Create path that the data will be sent to
        temp = self._config.get('custom', 'device_auth_token')

        # Raise an error if the auth token is not defined in config file
        if not temp:
            raise ValueError('Device auth token not present, please update config.ini by running rpicoap --edit')
        return temp

    @property
    def gpio_pin(self):
        return self._getint('gpio_pin')

    @property
    def host(self):
        return self._get('host')

    @property
    def path(self):
        return 'api/v1/' + self.auth_token + '/telemetry'

    @property
    def port(self):
        return self._getint('port')

    @property
    def sleep_interval(self):
        # Make sure sleep interval is at least one second
        sleep_interval = self._getint('sleep_interval')
        return sleep_interval if sleep_interval >= 1 else 1 

    def _get(self, property):
        return self._config.get('custom', property)

    def _getint(self, property):
        return self._config.getint('custom', property)

    def _read_config(self):
        """
        Gets the config settings from config.ini
        if config.ini does not exist, create config.ini
        from example file.
        """
        # get example file from package
        config_example = pkg_resources.resource_filename(__name__, "config.ini.example")
        self._config_ini_path = os.path.join(os.path.dirname(config_example), 'config.ini')

        # Check if config.ini exists
        if not os.path.exists(self._config_ini_path):
            # if not and example exists, copy to config.ini
            if os.path.exists(config_example):
                shutil.copy(config_example, self._config_ini_path)
                click.echo('Created config.ini at {}'.format(self._config_ini_path))
            else:
                # Error, no example or config found
                raise FileNotFoundError('No config.ini or config.ini.example found.')

        # create the config dictionary
        self._config = configparser.ConfigParser()
        self._config.read(self._config_ini_path)

    def open(self):
        """
        Opens the config file with the default text editor.
        If edit flag is passed at the command line open the config
        file with the default text editor for the OS
        """
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', self._config_ini_path))
        elif os.name == 'nt': # For Windows
            os.startfile(self._config_ini_path)
        elif os.name == 'posix': # For Linux, Mac, etc.
            subprocess.call(('vi', self._config_ini_path))