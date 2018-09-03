#!/usr/bin/python3

import rest, database, os, configparser, fetch, time
from threading import Timer, Lock

path = os.path.dirname(os.path.abspath(__file__)) + '/'

settings = configparser.ConfigParser()
settings.read(path + 'max.ini')

database.init_db(settings['max_db'])

t = None

lock = Lock()

last_run = None


def current_milli_time():
    return int(round(time.time() * 1000))


def cube_wait1():
    global last_run

    if last_run is None:
        return

    diff = current_milli_time() - last_run
    # TODO configurable time span
    if diff < 5000:
        time.sleep(5 - diff/1000)


def cube_wait2():
    global last_run

    last_run = current_milli_time()


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def update_data():
    global t
    print('abc')
    lock.acquire()
    try:
        cube_wait1()
        fetch.update_cube(settings)
        cube_wait2()
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
        cube_wait1()
        fetch.update_room(settings, room_id, temperature)
        cube_wait2()
    finally:
        lock.release()


def execute_api_update():
    global t

    if t is not None:
        t.cancel()
    update_data()


update_data()

rest.run_api(execute_api_update, room_update)

