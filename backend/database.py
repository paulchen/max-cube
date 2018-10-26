#!/usr/bin/python3

from datetime import datetime
from pony.orm import *
from decimal import Decimal
from log import logger


db = Database()


class Room(db.Entity):
    id = PrimaryKey(int)
    name = Required(str, 255)
    rf_address = Required(str, 6)
    devices = Set('Device')
    timestamp = Required(datetime)
    version = Required(int)

class HtRoom(db.Entity):
    _table_ = 'ht_room'
    id = Required(int)
    version = Required(int)
    name = Required(str, 255)
    rf_address = Required(str, 6)
    timestamp = Required(datetime)
    ht_timestamp = Required(datetime)
    PrimaryKey(id, version)

class Device(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, 255)
    rf_address = Required(str, 6)
    serial = Required(str, 255, unique=True)
    configuration = Optional(str, 255)
    device_type = Optional(int)
    room_id = Optional(Room)
    settings = Optional(str, 1023)
    gateway_known = Optional(bool)
    panel_locked = Optional(bool)
    link_ok = Optional(bool)
    battery_low = Optional(bool)
    status_initialized = Optional(bool)
    is_answer = Optional(bool)
    is_error = Optional(bool)
    is_valid = Optional(bool)
    valve_position = Optional(int)
    temperature = Optional(Decimal, 5, 2)
    actual_temperature = Optional(Decimal, 5, 2)
    timestamp = Required(datetime)
    version = Required(int)

class HtDevice(db.Entity):
    _table_ = 'ht_device'
    id = Required(int)
    version = Required(int)
    name = Required(str, 255)
    rf_address = Required(str, 6)
    serial = Required(str, 255, unique=True)
    configuration = Required(str, 255)
    device_type = Optional(int)
    room_id = Optional(int)
    settings = Optional(str, 1023)
    gateway_known = Optional(bool)
    panel_locked = Optional(bool)
    link_ok = Optional(bool)
    battery_low = Optional(bool)
    status_initialized = Optional(bool)
    is_answer = Optional(bool)
    is_error = Optional(bool)
    is_valid = Optional(bool)
    valve_position = Optional(int)
    temperature = Optional(Decimal, 5, 2)
    actual_temperature = Optional(Decimal, 5, 2)
    timestamp = Required(datetime)
    ht_timestamp = Required(datetime)
    PrimaryKey(id, version)


def init_db(settings):
    db.bind(provider='mysql', host=settings['host'], user=settings['username'], passwd=settings['password'], db=settings['database'])
    sql_debug(True)
    db.generate_mapping(create_tables=True)


@db_session
def save_or_update_room(cube_room):
    try:
        room = Room[cube_room.room_id]
        # room.version = room.version + 1
        room.name = cube_room.name
        logger.info("Room loaded from database: %s", room.name)
        room.rf_address = str(cube_room.rf_address)
        timestamp = datetime.now()
    except ObjectNotFound:
        room = Room(id=cube_room.room_id, name=cube_room.name, rf_address=str(cube_room.rf_address), timestamp=datetime.now(), version=1)


@db_session
def save_or_update_device(cube_device):
    try:
        room = Room[cube_device.room_id]
    except ObjectNotFound:
        room = None
    except AttributeError:
        # this is the fucking cube itself, we won't store this shit to avoid serious brain damage
        return

    device = Device.select(lambda d: d.serial == cube_device.serial).first()
    if device is None:
        device = Device(name=cube_device.name, rf_address = str(cube_device.rf_address), timestamp = datetime.now(), serial = cube_device.serial, version=1)
    else:
        device.name = cube_device.name
        device.rf_address = str(cube_device.rf_address)
        device.timestamp = datetime.now()
    
    if room is not None:
        logger.info("Updating room: %s, device: %s", room.name, device.name)
    else:
        logger.info("Updating room: %s, device: %s" , cube_device.room_id, device.name)

    device.device_type = cube_device.device_type
    device.room_id = room
    if cube_device.device_type in (1, 3):
        device.configuration = str(cube_device.configuration)
        device.settings = str(cube_device.settings)
        device.gateway_known = cube_device.settings.gateway_known
        device.panel_locked = cube_device.settings.panel_locked
        device.link_ok = cube_device.settings.link_ok
        device.battery_low = cube_device.settings.battery_low
        device.status_initialized = cube_device.settings.status_initialized
        device.is_answer = cube_device.settings.is_answer
        device.is_error = cube_device.settings.is_error
        device.is_valid = cube_device.settings.is_valid
        device.valve_position = cube_device.settings.valve_position
        device.temperature = cube_device.settings.temperature
        device.actual_temperature = cube_device.settings.actual_temperature


@db_session
def get_all_rooms():
    # TODO stable ordering
    db_rooms = select(r for r in Room)[:]
    rooms = []
    for db_room in db_rooms:
        devices = []
        for db_device in db_room.devices:
            device = {'name': db_device.name, 'device_type': db_device.device_type, 'temperature': db_device.temperature, 'actual_temperature': db_device.actual_temperature, 'serial': db_device.serial}
            devices.append(device)

        room = {'id': db_room.id, 'name': db_room.name, 'devices': devices}
        rooms.append(room)
    return rooms


@db_session
def get_room_rf_address(room_id):
    room = Room[room_id]
    return room.rf_address

