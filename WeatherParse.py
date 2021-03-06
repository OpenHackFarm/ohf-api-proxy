import urllib.request
import re
import json
import configparser
import os
from config import *

work_dir = os.path.dirname(os.path.abspath(__file__))
#CONF_FILE = os.path.join(work_dir,'config.ini')

#config = configparser.ConfigParser()
#config.read(CONF_FILE)

def getWeatherXML(path):
    xmlTree = urllib.request.urlopen(path).read()
    return xmlTree

def getValidTime(root):
    validTime = {}
    startTime = root.find('.//{urn:cwb:gov:tw:cwbcommon:0.1}startTime').text
    endTime = root.find('.//{urn:cwb:gov:tw:cwbcommon:0.1}endTime').text
    validTime['startTime'] = startTime
    validTime['endTime'] = endTime
    return validTime

def getWeatherConents(root):
    contents ={}
    count = 0
    for node in root.iter('{urn:cwb:gov:tw:cwbcommon:0.1}contents'):
        
        for subnode in node.iter():
            
            if '{urn:cwb:gov:tw:cwbcommon:0.1}content' == subnode.tag:
                count += 1
                contents['content'+str(count)] = []
            
            if '{urn:cwb:gov:tw:cwbcommon:0.1}contentText' == subnode.tag:
                contents['content'+str(count)].append(subnode.text.strip())
    
    return contents

def getWeatherHazards(root):
    hazards = {}
    count = 0
    for node in root.iter('{urn:cwb:gov:tw:cwbcommon:0.1}hazards'):
        
        for subnode in node.iter():
            
            if '{urn:cwb:gov:tw:cwbcommon:0.1}hazard' == subnode.tag:
                count += 1
                hazards['hazard'+str(count)] = []
            
            if  '{urn:cwb:gov:tw:cwbcommon:0.1}locationName' == subnode.tag:
                hazards['hazard'+str(count)].append(subnode.text)
    
    return hazards

def getCityinfo(f):
    data = json.load(f)
    resultList = []
    for city in data:
        resultList.append(city)

    return resultList

def getIdentifier(root):
    content = root.find('{urn:cwb:gov:tw:cwbcommon:0.1}identifier').text
    return content

def getAlarmInfo(hazards, cityInfo):
    #search & match alarm city
    citySet = set([])
    nonCitySet = set([])
    for hazard in hazards:
        for location in hazards[hazard]:
            bCheck = False
            for city in cityInfo:
                regexArea = re.search(city, location)
                if regexArea:
                    citySet.add(city)
                    bCheck = True
                    break
            if bCheck == False:
                nonCitySet.add(location)

    cityList = list(citySet)
    nonCityList = list(nonCitySet)
    alarmInfo = {}
    alarmInfo['alarmCity'] = cityList
    alarmInfo['nonMarkCity'] = nonCityList
    
    return alarmInfo 

def getAllData(root):
    #get weather valid Time
    validTime = getValidTime(root)

    #get weather contents
    contents = getWeatherConents(root)
    
    #get weather hazards 
    hazards = getWeatherHazards(root)
   
    #get city name
    f = open(os.path.join(work_dir,CITY_FILE))
    cityInfo = getCityinfo(f)

    #search & match alarm city
    alarmInfo = getAlarmInfo(hazards, cityInfo)
   
    #combine data
    result = []
    result.append(validTime)
    result.append(contents)
    result.append(hazards)
    result.append(alarmInfo)
    
    resultDict = {}
    resultDict['WeatherAlarm'] = result

    return resultDict

def sortHazardsCity(root):
    hazards = getWeatherHazards(root)
    cityInfoArray = []
    for data in hazards:
        cityInfoArray += hazards[data]
    cityInfoSet = set(cityInfoArray)
    return cityInfoSet

def filterHazardCity(cityInfoSet, targetCity):
   
    if cityInfoSet & targetCity:
        return True
    else:
        return False

