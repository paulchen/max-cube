#!/usr/bin/python3

import rest, database, os, configparser

path = os.path.dirname(os.path.abspath(__file__)) + '/'

settings = configparser.ConfigParser()
settings.read(path + 'max.ini')

database.init_db(settings['max_db'])

rest.run_api()

