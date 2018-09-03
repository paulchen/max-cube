#!/usr/bin/python3

import rest, database, os, configparser, fetch
from threading import Timer, Lock

path = os.path.dirname(os.path.abspath(__file__)) + '/'

settings = configparser.ConfigParser()
settings.read(path + 'max.ini')

database.init_db(settings['max_db'])

t = None

lock = Lock()

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def update_data():
    global t
    print('abc')
    lock.acquire()
    try:
        fetch.update_cube(settings)
        print('def')
        # TODO configurable file
        touch('last_cube_update')
    finally:
        lock.release()
        # TODO configurable time
        t = Timer(300.0, update_data)
        t.start()


def room_update(room_id, temperature):
    print(temperature)
    lock.acquire()
    try:
        fetch.update_room(settings, room_id, temperature)
    finally:
        lock.release()


def execute_api_update():
    global t

    if t is not None:
        t.cancel()
    update_data()


update_data()

rest.run_api(execute_api_update, room_update)

