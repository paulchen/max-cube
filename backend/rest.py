#!/usr/bin/python3

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from threading import Thread
import database

app = Flask(__name__)
# TODO configurable origins
CORS(app, origins="*", allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"])

update_callback = None

@app.route('/max/rooms')
def get_all_rooms():
    rooms = database.get_all_rooms()
    return jsonify({'rooms': rooms})


@app.route('/max/update')
def update_cube():
    thread = Thread(target = update_callback)
    thread.start()
    return jsonify({'status': 'ok'})


def run_api(execute_api_update):
    global update_callback, app

    update_callback = execute_api_update

    # TODO configurable port
    app.run(port=5003)

