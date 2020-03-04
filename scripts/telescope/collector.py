#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ =  'Felipe Fronchetti'
__contact__ = 'fronchetti@usp.br'

import requests
import time
from datetime import datetime
import json

class Collector:

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def request(self, path, parameters={}, headers={}):
        try:
            parameters['client_id'] = self.client_id
            parameters['client_secret'] = self.client_secret
            url = 'https://api.github.com/' + path
            print('Creating request for: ' + url)
            response = requests.get(url, params=parameters, headers=headers)
            self.verify_rate_limit(response.headers)
            return response.json()

        except requests.exceptions.HTTPError as error:
            with open('exceptions.log', 'a') as exceptions:
                exceptions.write('[HTTP] ' + error.text)
        except requests.exceptions.ConnectionError as error:
            with open('exceptions.log', 'a') as exceptions:
                exceptions.write('[CONNECTION] ' + error.text)
        except requests.exceptions.Timeout as error:
            with open('exceptions.log', 'a') as exceptions:
                exceptions.write('[TIMEOUT] ' + error.text)
        except requests.exceptions.RequestException as error:
            with open('exceptions.log', 'a') as exceptions:
                exceptions.write('[REQUEST] ' + error.text)

    def custom_request(self, url, parameters={}, headers={}, file_type='text'):
        try:
            print('Creating request for: ' + url)
            response = requests.get(url, params=parameters, headers=headers)

            if file_type == 'json':
                return response.json()
            if file_type == 'text':
                return response.text

        except requests.exceptions.HTTPError as error:
            with open('exceptions.log', 'a') as exceptions:
                exceptions.write('[HTTP] ' + error.text)
        except requests.exceptions.ConnectionError as error:
            with open('exceptions.log', 'a') as exceptions:
                exceptions.write('[CONNECTION] ' + error.text)
        except requests.exceptions.Timeout as error:
            with open('exceptions.log', 'a') as exceptions:
                exceptions.write('[TIMEOUT] ' + error.text)
        except requests.exceptions.RequestException as error:
            with open('exceptions.log', 'a') as exceptions:
                exceptions.write('[REQUEST] ' + error.text)

    def verify_rate_limit(self, headers):
        self.rate_limit_remaining = int(headers['x-ratelimit-remaining'])
        self.rate_limit_reset = int(headers['x-ratelimit-reset'])

        datetime_format = '%Y-%m-%d %H:%M:%S'
        reset_time = datetime.fromtimestamp(self.rate_limit_reset).strftime(datetime_format)
        current_time = datetime.now().strftime(datetime_format)

        print('[API] Requests Remaining:' + str(self.rate_limit_remaining))

        if self.rate_limit_remaining < 10:
            while(reset_time > current_time):
                print('The request limit is over. The process is sleeping until it can be resumed.')
                print('The limit will reset on: ' + reset_time)
                current_time = datetime.now().strftime(datetime_format)
                time.sleep(30)
