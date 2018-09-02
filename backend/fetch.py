#!/usr/bin/python3

import database, time, MySQLdb, urllib3, requests
from pymax.cube import Cube
from datetime import datetime


# TODO serious code duplication
def submit_value(db_settings, server, sensor_parts, what_parts, value_parts):
    start_time = time.time()

    sensor_string = ';'.join(sensor_parts)
    what_string = ';'.join(what_parts)
    value_string = ';'.join(value_parts)

    url = server['url'] + '/api/'
    s = requests.session()
    s.auth = (server['username'], server['password'])

    try:
        db = MySQLdb.connect(host=db_settings['hostname'], user=db_settings['username'], passwd=db_settings['password'], db=db_settings['database'], autocommit=True)

        curs = db.cursor()
        curs.execute('INSERT INTO cache (`server`, `sensors`, `whats`, `values`) VALUES (%s, %s, %s, %s)', (server['name'], sensor_string, what_string, value_string))
        rowid = curs.lastrowid

        # logger.info('Submitting values: sensors=%s, whats=%s, values=%s', sensor_string, what_string, value_string)
        print('Submitting values: sensors=%s, whats=%s, values=%s' % (sensor_string, what_string, value_string))
        resp = s.get(url, params={'action': 'submit', 'sensors': sensor_string, 'whats': what_string, 'values': value_string}, timeout=30)
        content = resp.text
        print('content: %s' % (content, ))
        if content != 'ok':
            raise requests.exceptions.RequestException

        curs.execute('UPDATE cache SET submitted = NOW() WHERE id = %s', (rowid, ))
        curs.close()
        db.close()
        
    except urllib3.exceptions.ConnectTimeoutError:
#        logger.error('Timeout during update')
        print('Timeout during update')
        return

    except urllib3.exceptions.ReadTimeoutError:
#        logger.error('Timeout during update')
        print('Timeout during update')
        return

    except requests.exceptions.RequestException:
#        logger.error('Error during update')
        print('Error during update')
        return

    end_time = time.time()


def submit_temperature(settings, cube_device):
    try:
        print('1: %s' % (cube_device.device_type, ))
        if cube_device.device_type != 3:
            return
        print('2')
        room_id = cube_device.room_id
        temperature = cube_device.settings.actual_temperature
    except AttributeError:
        # fuck the cube
        return

    # TODO make this mapping configurable
    print('3')
    if room_id == 1:
        sensor = 38
    elif room_id == 2:
        sensor = 37
    elif room_id == 3:
        sensor = 36
    elif room_id == 4:
        sensor = 35

    # TODO support multiple servers
    submit_value(settings['sensors_db'], settings['server'], (str(sensor), ), ('temp', ), (str(temperature), ))


def update_cube(settings):
    # TODO configurable hostname/ip address
    cube = Cube('evn-cube')
    cube.connect()

    for cube_room in cube.rooms:
        database.save_or_update_room(cube_room)

    for cube_device in cube.devices:
        database.save_or_update_device(cube_device)

        submit_temperature(settings, cube_device)

    cube.disconnect()


def update_room(settings, room_id, temperature):
    print(temperature)

    cube = Cube('evn-cube')
    cube.connect()

    rf_address = database.get_room_rf_address(room_id)

    cube.set_mode_manual(room_id, rf_address, temperature)

    cube.disconnect()


