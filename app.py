#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import requests
import json
from dateutil import parser
import datetime

from config import *

import xml.etree.ElementTree as ET
import WeatherParse as WP


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


@app.route('/special_weather', methods=['GET'])
@app.route('/special_weather/<city>', methods=['GET'])
def cwb_special_weather(city=None):
    xmlTree = WP.getWeatherXML('http://opendata.cwb.gov.tw/opendataapi?dataid=W-C0033-002&authorizationkey=%s' % CWB_AUTHORIZATION_KEY)
    root = ET.fromstring(xmlTree)
    resultJSON = WP.getAllData(root)
    if city:
        cityInfoSet = WP.sortHazardsCity(root)
        temp = city.split(",")
        bCheckCity = WP.filterHazardCity(cityInfoSet,set(temp))
        if bCheckCity:
            return jsonify(resultJSON)
        else:
            resultDict = {}
            resultDict['WeatherAlarm'] = []
            return jsonify(resultDict)
    else:
        return jsonify(resultJSON)


@app.route('/iot/data/<dev_id>/latest', methods=['GET'])
def latest_sensor_data(dev_id=None):
    url = 'http://%s:%s/query?pretty=true&db=%s&q=SELECT * FROM "test" WHERE "id"=\'%s\' ORDER BY DESC LIMIT 1' % (INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_DB, dev_id)
    print(url)
    r = requests.get(url)
    data = r.json()['results'][0]['series'][0]

    ret_data = dict(zip(data['columns'], data['values'][0]))
    ret_data['time'] = (parser.parse(ret_data['time']) + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

    return ret_data


if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)
