#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
import time


def parseAircraftReportXML(xmlfile) -> list:
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    ar_reports = []
    for item in root.findall('./data'):
        for child in item:
            if child.tag == "AircraftReport":
                ar = {}
                for ar_element in child:
                    ar[ar_element.tag] = ar_element
                ar_reports.append(ar)
    return ar_reports


def getAircraftReport(start_time, end_time):
    # https://aviationweather.gov/dataserver/example?datatype=airep
    params = {"dataSource": "aircraftreports", "requestType": "retrieve",
              "format": "xml", "startTime": str(start_time), "endTime": str(end_time)}
    r = requests.get(
        "https://aviationweather.gov/adds/dataserver_current/httpparam", params=params)
    with open('reports.xml', 'w') as f:
        f.write(r.text)
    reports = parseAircraftReportXML('reports.xml')
    for report in reports:
        try:
            print(report["turbulence_condition"].attrib)
        except KeyError:
            pass


epoch_time = int(time.time())
cur_time = epoch_time
time_step = 30*60
for i in range(500):
    getAircraftReport(cur_time - time_step, cur_time)
    cur_time = cur_time - time_step

# todo:
# 1. write to CSV with lat,lon,alt,aircraft ref,intensity
# 2. hash the data to make sure there's no duplicates
# 3. check warnings and report it (i.e >max reports returned)