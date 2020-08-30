#!/usr/bin/python3

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from threading import Thread
from log import logger
import database, json

app = Flask(__name__)
# TODO configurable origins
CORS(app, origins="*", allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"])

update_callback = None
room_callback = None

@app.route('/max/rooms', methods=['GET'])
def get_all_rooms():
    # TODO more checks?
    rooms = database.get_all_rooms()
    logger.debug('rooms: %s', rooms)
    return jsonify({'rooms': rooms})


@app.route('/max/rooms/<int:room_id>', methods=['POST'])
def update_room(room_id):
    # TODO more checks?
    data = request.data
    logger.debug("Update request received: %s", data.decode('UTF-8'))
    dataDict = json.loads(data.decode('UTF-8'))
    temperature = float(dataDict['temperature'])
    logger.debug('New temperature: %s', temperature)
    thread = Thread(target = room_callback, args = (room_id, temperature))
    thread.start()
    return jsonify({'status': 'ok'})


@app.route('/max/update', methods=['GET'])
def update_cube():
    # TODO more checks?
    thread = Thread(target = update_callback)
    thread.start()
    return jsonify({'status': 'ok'})


def run_api(execute_api_update, update_room):
    global update_callback, room_callback, app

    update_callback = execute_api_update
    room_callback = update_room

    # TODO configurable port
    app.run(port=5003)

