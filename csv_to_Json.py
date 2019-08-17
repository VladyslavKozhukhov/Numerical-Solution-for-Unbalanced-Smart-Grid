import csv
import json
def cleanTrashFromFirstLine(fileName, outputFIle):
    with open(fileName, 'r') as fin:
        data = fin.read().splitlines(True)
    with open(outputFIle, 'w') as fout:
        fout.writelines(data[2:])

def convertToJson(totalMap,path):
    with open(path, 'w') as fp:
        json.dump(totalMap, fp)

#input: gridlab csv output creates json file
def convertFromCsvToJson(csvFile, newJsonFile):
    f = open(csvFile, 'rU')
    reader = csv.DictReader(f, fieldnames=(
    "node_name", "voltA_mag", "voltA_angle", "voltB_mag", "voltB_angle", "voltC_mag", "voltC_angle"))
    out = json.dumps([row for row in reader])
    f = open(newJsonFile, 'w')
    f.write(out)
