#!/usr/bin/python3

import rest, database, os, configparser, fetch, time, logging
from threading import Timer, Lock
from log import logger

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
    logger.info('Starting update')
    lock.acquire()
    try:
        fetch.update_and_check_cube(settings)
        logger.info('Update completed succssfully')
        # TODO configurable file
        touch('last_cube_update')
    finally:
        lock.release()
        # TODO configurable time
        t = Timer(300.0, update_data)
        t.start()


def room_update(room_id, temperature):
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

