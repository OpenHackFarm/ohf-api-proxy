#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import requests
import json

HOST = '0.0.0.0'
PORT = 8008


class MyResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (list, dict)):
            response = jsonify(response)
        return super(Response, cls).force_type(response, environ)

app = Flask(__name__)
CORS(app)
app.response_class = MyResponse


@app.route('/index')
def index():
    return jsonify({'message': 'hello'})

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
