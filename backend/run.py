#!/usr/bin/python3

import rest, database, os, configparser, fetch
from threading import Timer

path = os.path.dirname(os.path.abspath(__file__)) + '/'

settings = configparser.ConfigParser()
settings.read(path + 'max.ini')

database.init_db(settings['max_db'])

t = None

def update_data():
    global t
    print('abc')
    fetch.update_cube(settings)
    print('def')
    # TODO configurable time
    t = Timer(300.0, update_data)
    t.start()


def execute_api_update():
    global t

    if t is not None:
        t.cancel()
    update_data()


update_data()

rest.run_api(execute_api_update)

