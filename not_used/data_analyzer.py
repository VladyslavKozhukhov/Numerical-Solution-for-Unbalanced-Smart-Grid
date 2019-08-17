import csv_to_Json
import json

_threshold = 0.05

def fromJsonToPython(jsonFile):
    with open(jsonFile) as json_file:
        json_data = json.load(json_file)
    data = json.dumps(json_data)
    json_to_python_dictList = json.loads(data)#listOFdicts
    return   json_to_python_dictList

def getStateData(voltageFile, updatedVoltageFile, jsonFile):
    csv_to_Json.cleanTrashFromFirstLine(voltageFile, updatedVoltageFile)
    csv_to_Json.convertFromCsvToJson(updatedVoltageFile, jsonFile)
    listOfNodesInformation =fromJsonToPython(jsonFile)  # list of dicts
    return listOfNodesInformation
