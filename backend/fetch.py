#!/usr/bin/python3

import database, time, MySQLdb, urllib3, requests
from pymax.cube import Cube
from datetime import datetime


last_run = None
skip_temperature_changes = 0


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
        actual_temperature = cube_device.settings.actual_temperature
        target_temperature = cube_device.settings.temperature
    except AttributeError:
        # fuck the cube
        return

    # TODO make this mapping configurable
    print('3')
    if room_id == 1:
        actual_sensor = 38
        target_sensor = 42
    elif room_id == 2:
        actual_sensor = 37
        target_sensor = 41
    elif room_id == 3:
        actual_sensor = 36
        target_sensor = 40
    elif room_id == 4:
        actual_sensor = 35
        target_sensor = 39
    elif room_id == 5:
        actual_sensor = 44
        target_sensor = 45
    else:
        # TODO
        return

    # TODO support multiple servers
    submit_value(settings['sensors_db'], settings['server1'], (str(actual_sensor), str(target_sensor)), ('temp', 'temp'), (str(actual_temperature), str(target_temperature)))
    submit_value(settings['sensors_db'], settings['server2'], (str(actual_sensor), str(target_sensor)), ('temp', 'temp'), (str(actual_temperature), str(target_temperature)))


def update_cube(settings):
    cube_wait1()

    # TODO configurable hostname/ip address
    cube = Cube('evn-cube')
    cube.connect()

    cube_rooms = cube.rooms
    for cube_room in cube_rooms:
        database.save_or_update_room(cube_room)

    problems = []
    for cube_device in cube.devices:
        database.save_or_update_device(cube_device)

        submit_temperature(settings, cube_device)

        problems.extend(check_for_problems(cube_device, cube_rooms))

    cube.disconnect()
    
    cube_wait2()

    return problems


def update_rooms(settings, update_data):
    for update_item in update_data:
        update_room(settings, update_item[0], update_item[1])


def change_temperature_twice(settings, problems):
    global skip_temperature_changes

    if skip_temperature_changes > 0:
        skip_temperature_changes -= 1
        return

    room_ids = []

    update_data1 = []
    update_data2 = []

    for problem in problems:
        cube_room = problem[2]
        cube_device = problem[3]
        link_ok = problem[4]

        if link_ok:
            continue

        room_id = cube_room.room_id
        if room_id in room_ids:
            continue

        temperature = cube_device.settings.actual_temperature
        # TODO use a dict here
        update_data1.append((room_id, temperature + .5))
        update_data2.append((room_id, temperature))
        room_ids.append(room_id)


    update_rooms(settings, update_data1)

    time.sleep(120)

    update_rooms(settings, update_data2)

    # TODO make this configurable
    skip_temperature_changes = 120


def write_status_file(problems):
    status = 0
    description = 'No problems detected'
    if len(problems) > 0:
        status = max([p[0] for p in problems])
        description = 'Problems: ' + '; '.join([p[1] for p in problems])

    status_file = open('icinga.status', 'w')
    status_file.write(str(status) + '\n')
    status_file.write(description + '\n')
    status_file.close()


def update_and_check_cube(settings):
    problems = update_cube(settings)

    if len(problems) > 0:
        change_temperature_twice(settings, problems)
        problems = update_cube(settings)

    write_status_file(problems)


def check_for_problems(cube_device, cube_rooms):
    try:
        room_id = cube_device.room_id
    except AttributeError:
        # the cube itself
        return []

    if cube_device.room_id == 0:
        # ECO key
        return []

    link_ok = cube_device.settings.link_ok
    battery_low = cube_device.settings.battery_low

    problem = not link_ok or battery_low
    if problem:
        cube_room = find_cube_room(cube_rooms, room_id)

        if cube_room is None:
            # TODO wtf
            print("This is wrong!")

        status = 0
        if battery_low:
            status = 1
        if not link_ok:
            status = 2

        message = "Room=%s,device=%s/%s,link_ok=%s,battery_low=%s" % (cube_room.name, cube_device.name, cube_device.serial, link_ok, battery_low)
        # TODO use a dict here
        return [(status, message, cube_room, cube_device, link_ok, not battery_low)]

    return []


def find_cube_room(cube_rooms, room_id):
    for cube_room in cube_rooms:
        if cube_room.room_id == room_id:
            return cube_room

    return None


def update_room(settings, room_id, temperature):
    print(temperature)

    cube_wait1()

    cube = Cube('evn-cube')
    cube.connect()

    rf_address = database.get_room_rf_address(room_id)

    cube.set_mode_manual(room_id, rf_address, temperature)

    cube.disconnect()

    cube_wait2()



