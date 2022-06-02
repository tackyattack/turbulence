#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
import time
from typing import Tuple
import csv


def getReportElement(report, key, attribute, default):
    try:
        if attribute is not None:
            return getattr(report[key], attribute)
        else:
            return report[key]
    except KeyError:
        return default


class AircraftReport:
    def __init__(self, observation_time, aircraft_ref, latitude, longitude, altitude_ft_msl, turbulence_condition) -> None:
        self.observation_time = observation_time
        self.aircraft_ref = aircraft_ref
        self.latitude = latitude
        self.longitude = longitude
        self.altitude_ft_msl = altitude_ft_msl
        self.turbulence_condition = turbulence_condition
        if turbulence_condition:
            self.turbulence_intensity = getReportElement(
                turbulence_condition, "turbulence_intensity", None, "")
        else:
            self.turbulence_intensity = ""


def parseAircraftReportXML(xmlfile) -> Tuple[list, list]:
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
    warnings = []
    for item in root.find('./warnings'):
        warnings.append(item.text)
    return ar_reports, warnings


def getAircraftReports(start_time, end_time) -> list:
    # https://aviationweather.gov/dataserver/example?datatype=airep
    params = {"dataSource": "aircraftreports", "requestType": "retrieve",
              "format": "xml", "startTime": str(start_time), "endTime": str(end_time)}
    r = requests.get(
        "https://aviationweather.gov/adds/dataserver_current/httpparam", params=params)
    with open('reports.xml', 'w') as f:
        f.write(r.text)
    reports, warnings = parseAircraftReportXML('reports.xml')
    if warnings:
        print(warnings)
    final_reports = []
    for report in reports:
        final_reports.append(AircraftReport(observation_time=getReportElement(report, "observation_time", "text", ""),
                                            aircraft_ref=getReportElement(
                                                report, "aircraft_ref", "text", ""),
                                            latitude=getReportElement(
                                                report, "latitude", "text", ""),
                                            longitude=getReportElement(
                                                report, "longitude", "text", ""),
                                            altitude_ft_msl=getReportElement(
                                                report, "altitude_ft_msl", "text", ""),
                                            turbulence_condition=getReportElement(report, "turbulence_condition", "attrib", "")))
    return final_reports


def writeAircraftReportsCsv(time_step_s, iterations):
    epoch_time = int(time.time())
    cur_time = epoch_time
    with open('reports.csv', 'w', newline='') as csvfile:
        fieldnames = ['observation_time', 'aircraft_ref', 'latitude',
                      'longitude', 'altitude_ft_msl', 'turbulence_intensity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(iterations):
            reports = getAircraftReports(cur_time - time_step_s, cur_time)
            cur_time = cur_time - time_step_s

            for report in reports:
                if report.turbulence_intensity:
                    writer.writerow({'observation_time': report.observation_time,
                                    'aircraft_ref': report.aircraft_ref,
                                     'latitude': report.latitude,
                                     'longitude': report.longitude,
                                     'altitude_ft_msl': report.altitude_ft_msl,
                                     'turbulence_intensity': report.turbulence_intensity})


writeAircraftReportsCsv(30*60, 5000)

# todo:
# 2. hash the data to make sure there's no duplicates
