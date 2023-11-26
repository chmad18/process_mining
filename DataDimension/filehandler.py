from calendar import c
from datetime import datetime
import xml.etree.ElementTree as ET
import sys

def debugger_is_active() -> bool:
    """Return if the debugger is currently active"""
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None

def read_from_file(filename):

    tree = ET.parse(filename)
    root = tree.getroot()

    log = {}

    s = {'xes' : 'http://www.xes-standard.org/'}

    for trace in root.findall('xes:trace', s):
        caseId = trace.find('xes:string[@key="concept:name"]', s).attrib['value']
        
        log[caseId] = []

        for event in trace.findall('xes:event', s):
            e = {}

            for data in event.findall('xes:date', s):
                key = data.attrib['key']
                value = data.attrib['value']
                e[key] = datetime.strptime(value[:19], '%Y-%m-%dT%H:%M:%S')
            
            for data in event.findall('xes:string', s):
                key = data.attrib['key']
                value = data.attrib['value']
                e[key] = value

            for data in event.findall('xes:int', s):
                key = data.attrib['key']
                value = int(data.attrib['value'])
                e[key] = value

            for data in event.findall('xes:boolean', s):
                key = data.attrib['key']
                value = data.attrib['value'] == 'true'
                e[key] = value
            
            log[caseId].append(e)

    return log


def files_dictionary():
    return {
        "S1" : {
            "normal": ['Scenario1/logNormal.xes'],
            "enriched": ['Scenario1/logFreq.xes', 'Scenario1/logDur.xes']
        },
        "S2" : {
            "normal": ['Scenario2/logNormal.xes'],
            "enriched": ['Scenario2/logDelay.xes', 'Scenario2/logAbsence.xes']
        },
        "S3" : {
            "normal": ['Scenario3/logNormal.xes'],
            "enriched": ['Scenario3/logShuffle.xes']
        }
    }