import csv_to_Json
import json
import os
from sklearn.metrics import mean_squared_error
import  numpy as np
import glm
from pathlib import Path
import operator
import network_capacitors_placement

NUM_OF_FILES = 1
minValue = 0.95
maxValue= 1.05
treshold =0.75
numOfNodes = 4883
#inputFile = "data/0/IEEE8500_DSS_GLD_v10.glm"
inputFile = "/home/vladko/Downloads/FinalProject/FinalProject/analytic_data/folder0/gridLAB_D_Model.glm"

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


def getAllData(listOfNodesInformation, mapNodeVoltage, clearNodes):
    mseA=[]
    mseB=[]
    mseC=[]
    mseTotal=[]
    overloadNode={}
    problemNode={}
    mapNodes = {}
    zeroNode={}
    fullMap={}

    for nodeInfo in listOfNodesInformation:
        if nodeInfo["node_name"] in mapNodeVoltage.keys():
            voltageA = float(nodeInfo['voltA_mag'])
            voltageB = float(nodeInfo['voltB_mag'])
            voltageC = float(nodeInfo['voltC_mag'])
            nominalVoltage = float(mapNodeVoltage[nodeInfo["node_name"]])
            problemNodeData = {}
            overloadNodeData={}
            zeroNodeData={}
            A = voltageA/nominalVoltage
            B = voltageB/nominalVoltage
            C = voltageC/nominalVoltage

            if (float(A)>=treshold):
                mseA.append(A)
            if (float(B) >=treshold):
                mseB.append(B)
            if (float(C)>=treshold):
                mseC.append(C)

            if(float(A)<minValue  and float(A)>=treshold ):
                problemNodeData["A"]=A
            if ((float(B) < minValue ) and float(B)>=treshold):
                problemNodeData["B"]=B
            if ((float(C) < minValue )and float(C)>=treshold):
                problemNodeData["C"]=C

            if(float(A)>=maxValue):
                overloadNodeData["A"] = A
            if(float(B)>=maxValue):
                overloadNodeData["B"] = B
            if(float(C)>=maxValue):
                overloadNodeData["C"] = C

            if (float(A) <=treshold):
                zeroNodeData["A"]=A
            if (float(B) <=treshold):
                zeroNodeData["B"]=B
            if (float(C) <=treshold):
                zeroNodeData["C"]=C

            dataNode={}
            dataNode["nominal_voltage"]=nominalVoltage
            dataNode["voltageA"]=voltageA
            dataNode["voltageB"] = voltageB
            dataNode["voltageC"] = voltageC
            dataNode["voltageA_pr"] = A
            dataNode["voltageB_pr"] = B
            dataNode["voltageC_pr"] = C
            mapNodes[nodeInfo["node_name"]]=dataNode

            if(len(problemNodeData.keys())>0):
                problemNode[nodeInfo["node_name"]] = problemNodeData
            if(len(zeroNodeData.keys())>0):
                zeroNode[nodeInfo["node_name"]]=zeroNodeData
            if(len(overloadNodeData.keys())>0):
                overloadNode[nodeInfo["node_name"]] = overloadNodeData

    lstMSE= []
    lstMSE.append(MSE(mseA))
    lstMSE.append(MSE(mseB))
    lstMSE.append(MSE(mseC))
    mseTotal=mseA+mseB+mseC
    lstMSE.append(MSE(mseTotal))
    fullMap["MSE"] = lstMSE
    fullMap["ZERO_NODES"]= zeroNode
    fullMap["OVERLOAD_NODES"] = overloadNode
    fullMap["UNDER_VOLTAGE_NODES"]=problemNode
    fullMap["NODES"] = mapNodes

    f = open(clearNodes, "w+")
    if(len(problemNode.keys())==0 and len(overloadNode.keys())==0):
        f.write("Clear")
        # print("AAAAAAAAAAAAAAAAAAAAA_____CLEAR___AAAAAAAAAAAAAAAAAAAAAAAAA")
    else:
        f.write("Not Clear")
    f.close()
    return fullMap





def makeMapNodeNameNominalVoltage():

    totalMap = {}
    network = glm.load(inputFile)
    for obj in network["objects"]:
        if(obj["name"]=="node" or obj["name"]=="triplex_node"):
            totalMap[obj["attributes"]["name"]]=obj["attributes"]["nominal_voltage"]

    return totalMap

def createTotalData(csvName, index =1):
    # for index in range(0,numOfFiles):

    voltagePath = "./analytic_data/folder" + str(index) +"/" + csvName
    voltagePathUpdated = "./analytic_data/folder"+str(index)+"/output_voltage_1_updated.csv"
    jsonFile = "./analytic_data/folder"+str(index)+"/file.json"
    clearNodes = "./analytic_data/folder"+str(index)+"/clearNodes.txt"
    config = Path(voltagePath)
    if config.is_file():
        listOfNodesInformation = getStateData(voltagePath, voltagePathUpdated, jsonFile)
        mapOfNodeVoltage = makeMapNodeNameNominalVoltage()
        totalMap = getAllData(listOfNodesInformation, mapOfNodeVoltage, clearNodes)
        csv_to_Json.convertToJson(totalMap, "analytic_data/folder" + str(index) + "/allAnalyticData.json")
        # print(str(index))


def MSE(NodeVoltage):
    lstOfValues=  np.fromiter(NodeVoltage, dtype=float)
    perfetList = np.array([1 for x in range(0,len(NodeVoltage))])
    #a = lstOfValues+perfetList
    mse = mean_squared_error(lstOfValues,perfetList)#true,pred
    # print("MSE: "+""+ np.float64(mse).astype(str))
    return mse


def bestConfig(numOfFiles):
    min = 9999
    i =-1
    mseA=1
    mseB=1
    mseC=1
    mseTotal =1
    iMse =-1
    mapIndexMSEtotal={}
    mapIndexProblemNode={}
    for index in range(0,numOfFiles):
        jsonFile = "analytic_data/folder"+str(index)+"/allAnalyticData.json"
        config = Path(jsonFile)
        if config.is_file():
            totalMap = fromJsonToPython(jsonFile)
            if(len(totalMap["UNDER_VOLTAGE_NODES"].keys()) <min):
                min = len(totalMap["UNDER_VOLTAGE_NODES"])
                i = index
            mapIndexProblemNode[index] = len(totalMap["UNDER_VOLTAGE_NODES"])

            if(totalMap["MSE"][0]<mseA and totalMap["MSE"][1]<mseB and totalMap["MSE"][2]<mseC):
                mseA = totalMap["MSE"][0]
                mseB = totalMap["MSE"][1]
                mseC = totalMap["MSE"][2]
            if (totalMap["MSE"][3] < mseTotal):
                mseTotal = totalMap["MSE"][3]
                iMse=index
            mapIndexMSEtotal[index] = totalMap["MSE"][3]
    # sortMapIndexProblemNode(mapIndexMSEtotal, "orderMseTotalNodes.txt")
    # sortMapIndexProblemNode(mapIndexProblemNode,"orderedProblemNodes.txt")
    print("Best Config by Nodes: "+ str(i)+" with "+str(min) + " UNDER_VOLTAGE_NODES")
    print("Best Config by MSE: "+ str(i)+" with "+"MSEA "+ str(mseA)+",MSEB "+ str(mseB) +",MSEC "+ str(mseC))
    print("Best Config by MSE TOTAL : "+ str(iMse)+" with "+str(mseTotal) + " UNDER_VOLTAGE_NODES")
def sortMapIndexProblemNode(mapIndexProblemNode,name):
    sorted_map = sorted(mapIndexProblemNode.items(), key=operator.itemgetter(1))
    with open(name,'w') as fp:
        fp.write('\n'.join('%s %s' % x for x in sorted_map))
    print(sorted_map)

def addCapacitorText(file, name, parent,phase,cap_nominal_voltage,A,B,C):
    with open(file, 'a') as f:
        strOne="object capacitor {\n"+"\tname "+name+";\n"+"\tparent "+parent+";\n"+"\tphases "+phase+";\n"
        strTwo = "\tphases_connected "+phase+";\n"+"\tcap_nominal_voltage "+str(cap_nominal_voltage)+";\n"
        strThree = "\tcapacitor_A "+str(A)+";\n"+"\tcapacitor_B "+str(B)+";\n"+"\tcapacitor_C "+str(C)+";\n"
        strFour = "\tswitchA CLOSED;\n"+"\tswitchB CLOSED;\n"+"\tswitchC CLOSED;\n"
        strFive = "}\n"

        f.write(strOne)
        f.write(strTwo)
        f.write(strThree)
        f.write(strFour)
        f.write(strFive)


def addCapacitor(file, name, parent,phase,cap_nominal_voltage,A,B,C ):
    network = glm.load(file)
    lstOfObj = network['objects']
    dictMap = {}
    dictMap["name"]="capacitor"
    dictAttr = {}
    dictAttr["name"] = name
    dictAttr["parent"] = parent
    dictAttr["phases"] = phase
    dictAttr["phases_connected"] = phase
    dictAttr["cap_nominal_voltage"] = cap_nominal_voltage
    dictAttr["capacitor_B"] = B  # 'capacitor_B': '300000',
    dictAttr["capacitor_C"] = C
    dictAttr["capacitor_A"] = A
    dictAttr["switchA"] = "CLOSED"
    dictAttr["switchB"] = "CLOSED"
    dictAttr["switchC"] = "CLOSED"
    dictMap["attributes"]= dictAttr
    dictMap["children"]=[]
    lstOfObj.append(dictMap)

    glm.dump(network, file)
    # replaceClock(file)

# def replaceClock(pathFile):
#     entries = os.scandir('analytic_data/folder1/')
#     counter = 0
#     lines=[]
#     for entry in entries:
#         if(entry.name == "myTest.glm"):
#             with open(entry) as f:
#                 lines = f.readlines()
#                 lines[1]= "	 timestamp '2000-01-01 0:00:00';"
#                 lines[2]= "	 stoptime '2000-01-01 0:02:00';"
#
#             f.close()
#             with open(entry, "w") as f:
#                 f.writelines(lines)
#             f.close()
#             # with open(entry, 'r+') as f:
#             #     content = f.read()
#             #     f.seek(0, 0)
#             #     line = "// European LV Test Feeder \n"
#             #     f.write(line + '\n' + content)
# # a = os.getcwd()
# os.chdir("./analytic_data/folder1/")
# os.system("gridlabd myTest.glm")
# os.chdir(a)
#
# checkAllOptions("output_voltage_1.csv",1)
# bestConfig(1)

# if __name__== "__main__":
#     network_capacitors_placement.addCapacitorText("./analytic_data/folder1/myTest.glm", "Test", "Bus32","ABC",240.177712,1000,1000,1000  )
#
#     network_capacitors_placement.addCapacitor("./analytic_data/folder1/gridLAB_D_Model.glm", "Test", "Bus32","ABC",240.177712,1000,1000,1000  )
# #
#
#     a = os.getcwd()
#     os.chdir("./analytic_data/folder1/")
#     os.system("gridlabd myTest.glm")
#     os.chdir(a)
#     checkAllOptions("output_voltage_1.csv",1)
#     bestConfig(1)