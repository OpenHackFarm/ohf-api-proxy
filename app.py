#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import requests
import json

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
            return resultDict 
    else:
        return jsonify(resultJSON)

if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)
