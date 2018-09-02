#!/usr/bin/python3

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
import database

def run_api(execute_api_update):
    app = Flask(__name__)
    api = Api(app)
    # TODO configurable origins
    CORS(app, origins="*", allow_headers=[
            "Content-Type", "Authorization", "Access-Control-Allow-Credentials"])


    class RoomApi(Resource):
        def get(self):
            rooms = database.get_all_rooms()
            return jsonify({'rooms': rooms})

    class UpdateApi(Resource):
        def get(self):
            execute_api_update()
            return jsonify({'status': 'ok'})

    api.add_resource(RoomApi, '/max/rooms')
    api.add_resource(UpdateApi, '/max/update')

    # TODO configurable port
    app.run(port=5003)

