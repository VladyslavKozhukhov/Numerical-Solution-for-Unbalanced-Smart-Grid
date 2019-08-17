# def runProgram(lstOfIndex, valuesOn,values,dicIndexVal):
#     counter = 0;
#     dicIndexMSE={}
#     lstOfIndexStr = [str(x) for x in lstOfIndex]
#
#     indexTocheck = [','.join(x) for x in itertools.combinations(lstOfIndexStr, valuesOn)]
#
#     for indexes in indexTocheck:
#         indexes = [int(x) for x in indexes.split(',')]
#         values = getValuesByIndex(values,indexes,dicIndexVal)
#
#         parser.updateValueByIndex(allCapacitorsZeroFile, indexes, values)
#         valNewMse =exec(updatedFile,counter)
#         if(valNewMse != 9999):
#             dicIndexMSE[str(indexes)] = valNewMse
#             # if(mse> valNewMse):
#             #     mse =valNewMse
#
#         counter = counter +1
#     return  dicIndexMSE
#
# def getValuesByIndex(values,indexes,dicIndexVal):
#     val=[]
#     for index in indexes:
#         val.append(dicIndexVal[index])
#     return  val
#
# def createDicIndexVal(indexes,values):
#     counter = 0
#     dic = {}
#     for i in indexes:
#         dic[i]=values[counter]
#         counter=counter+1
#     return  dic
#
#
# def validateThatAllNodesOk(dictNodeVoltage):
#     lstOfValues = dictNodeVoltage.values()
#     for i in lstOfValues:
#         if(float(i)< minValue):
#             return False
#     return  True
#
#
# def MSE(dictNodeVoltage):
#     lstOfValues=  np.fromiter(dictNodeVoltage.values(), dtype=float)
#     perfetList = np.array([1 for x in range(0,len(dictNodeVoltage))])
#     #a = lstOfValues+perfetList
#     mse = mean_squared_error(lstOfValues,perfetList)#true,pred
#     print("MSE: "+""+ np.float64(mse).astype(str))
#     return mse
#
#
#
# # def exec(fileName,index = None):
# #     if(index == None):
# #         runGridLab(fileName)
# #         csvToJson.cleanTrashFromFirstLine(VoltageFile, updatedVoltageFile)
# #         csvToJson.convertFromCsvToJson(updatedVoltageFile)
# #         listOfNodesInformation = dataAnalyzer.fromJsonToPython(jsonFile)  # list of dicts
# #         #_listOfMapAllZeroCapacitors = listOfNodesInformation
# #         dictNodeVoltage = printToFileNodeAndNormalizedVoltageAndReturnDict(listOfNodesInformation[0:numOfNodes])
# #         #showGraph(dictNodeVoltage)
# #         if (validateThatAllNodesOk(dictNodeVoltage)):
# #             return MSE(dictNodeVoltage)
# #         return 9999
# #     else:
# #         runGridLab(fileName)
# #         csvToJson.cleanTrashFromFirstLine(VoltageFile, updatedVoltageFile)
# #         csvToJson.convertFromCsvToJson(updatedVoltageFile)
# #         listOfNodesInformation = dataAnalyzer.fromJsonToPython(jsonFile)  # list of dicts
# #         dictNodeVoltage = printToFileNodeAndNormalizedVoltageAndReturnDict(listOfNodesInformation[0:numOfNodes])
# #         print(dictNodeVoltage.values())
# #         if (validateThatAllNodesOk(dictNodeVoltage)):
# #             showGraph(dictNodeVoltage)
# #             return MSE(dictNodeVoltage)
# #         return 9999
#
# def buildBruteForeSolution(mapOfIndexandValues):
#     #values = parser.updateAllCapacitorsToZero(inputFile)
#     dicIndexMSE={}
#     #@TODO FIRST RUN:
#     mse =9999
#     if exec(allCapacitorsZeroFile) < mse:
#         print("Alredy optimized")
#     #dicIndexVal=createDicIndexVal(mapOfIndexandValues,values)
#     #
#     # for i in range(0,len(mapOfIndexandValues)):
#     #     print("Num Of Capcacitors : "+ str(i+1))mapOfIndexandValues
#     #     dicIndexMSE = runProgram(lstOfIndex,i+1,values,dicIndexVal)
#     #     if(len(dicIndexMSE)>0):
#     #         break
#     print(dicIndexMSE)
#     print("Optimized")
#
#     def findMaxVoltageValueInPhase(phase, listOfNodesInformation):
#         max = -1
#         if phase == 0:
#             for nodeInfo in listOfNodesInformation:
#                 voltage = nodeInfo['voltA_mag']
#                 if float(voltage) > max:
#                     max = float(voltage)
#         elif phase == 1:
#             for nodeInfo in listOfNodesInformation:
#                 voltage = nodeInfo['voltB_mag']
#                 if float(voltage) > max:
#                     max = float(voltage)
#         else:
#             for nodeInfo in listOfNodesInformation:
#                 voltage = nodeInfo['voltC_mag']
#                 if float(voltage) > max:
#                     max = float(voltage)
#
#         return max
#
#     def printToFileNodeAndNormalizedVoltageAndReturnDict(listOfNodesInformation):
#         maxVoltageValueA = findMaxVoltageValueInPhase(0, listOfNodesInformation)
#         maxVoltageValueB = findMaxVoltageValueInPhase(1, listOfNodesInformation)
#         maxVoltageValueC = findMaxVoltageValueInPhase(2, listOfNodesInformation)
#
#         dictNodeVoltage = {}
#         with open("NormalizedVoltage.txt", 'w') as nmv:
#             for nodeInfo in listOfNodesInformation:
#                 voltage = nodeInfo['voltA_mag']
#                 normalizedVoltage = float(voltage) / maxVoltageValueA
#                 # newV = "%.3f" % float()/maxVoltageValue
#                 dictNodeVoltage[nodeInfo['node_name']] = "%.3f" % (normalizedVoltage)
#                 nmv.write(nodeInfo['node_name'] + ": " + "%.3f" % (normalizedVoltage) + "\n")
#         return dictNodeVoltage
# def updateAllCapacitorsToZero(inputFile):
#     textToSearch ="capacitor_A"
#     values=[]
#     # capacitor_A 50 kVAr;
#
#     textToReplace = "    capacitor_A 0.01 kVAr; \n"
#
#     fileUpdated = open("UpdatedFileAllZero.glm",'r+')
#     for line in fileinput.input(inputFile):
#         if textToSearch in line:
#             values.append(line)
#             fileUpdated.write(line.replace(line, textToReplace))
#         else:
#             fileUpdated.write(line)
#     fileUpdated.close()
#     return  values
#
# def updateValueByIndex(inputFile,indexLst,valueLst):
#     textToSearch ="    capacitor_A 0.01 kVAr; \n"
#     # capacitor_A 50 kVAr;
#     counter = 0
#     #textToReplace = value
#     index = 0
#     fileUpdated = open("UpdatedFile.glm",'w')
#     for line in fileinput.input(inputFile):
#         if textToSearch in line:
#             if(counter == indexLst[index]):
#                 fileUpdated.write(line.replace(line, valueLst[index]))
#                 if(index+1 <= len(indexLst)-1):
#                     index =index +1
#             else:
#                 fileUpdated.write(line)
#         else:
#             fileUpdated.write(line)
#         counter = counter + 1
#
#     fileUpdated.close()
# def printToFileNodeAndNormalizedVoltageAndReturnDict(listOfNodesInformation, mapNodeVoltage,path):
#     listVoltageValue =getVoltageValueInPhase(listOfNodesInformation, mapNodeVoltage)
#
#
#     dictNodeVoltage={}
#     with open(path+"/NormalizedVoltage.txt",'w') as nmv:
#         for nodeInfo in listOfNodesInformation:
#             voltage = nodeInfo['voltA_mag']
#             normalizedVoltage= float(voltage)
#             # newV = "%.3f" % float()/maxVoltageValue
#             dictNodeVoltage[nodeInfo['node_name']] = "%.3f" % (normalizedVoltage)
#             nmv.write(nodeInfo['node_name'] +": "+"%.3f" % (normalizedVoltage)+"\n")
#
#     return  dictNodeVoltage

# def addCapacitorToNode(file, name, parent, phase,cap_nominal_voltage, capacitor, capacitorValue, lineCap,ptPhase,switch ):
#     network = glm.load(file)
#     listOfObj = network['objects']
#     dictMap = {}
#     dictAttr={}
#     dictMap["name"]="capacitor"
#     dictAttr["name"] = name
#     dictAttr["parent"] = parent
#     dictAttr["phases"] = phase
#     dictAttr["phases_connected"] = phase
#     dictAttr["cap_nominal_voltage"] = cap_nominal_voltage
#     dictAttr[capacitor] = capacitorValue #'capacitor_B': '300000',
#     dictAttr["control"]="MANUAL"
#     dictAttr["VAr_set_low"]= "-225000"
#     dictAttr["VAr_set_high"]= "150000"
#     dictAttr["remote_sense"]= lineCap #'line_cap_1b',
#     dictAttr["pt_phase"]= ptPhase
#     dictAttr["control_level"] ="BANK"
#     dictAttr["time_delay"]= "101.000"
#     dictAttr[switch]="CLOSED"
#     dictMap["attributes"]= dictAttr
#     dictMap["children"]=[]
#     listOfObj.append(dictMap)
#     glm.dump(network,file)

#data analyzer
#
# def findRaiusOfEachCapacitor(lstOfNodesInfInitState, mapCapacitors):
#     skipFirst = 1
#     skipThird = 3
#     mapCapacitorRadius = {}
#     notConv = list(data_creator.makeMapNodeNameNominalVoltage().keys())
#     for index in range(1,len(mapCapacitors)+1):
#         mapNodeValue = {}
#
#         if index != skipFirst and index != skipThird:
#             voltageFile ="data/"+str(index)+"/output_voltage_1.csv"
#             updatedVoltageFile="data/"+str(index)+"/output_voltage_1_no_2_firstLines.csv"
#             jsonFile = "data/"+str(index)+"/jsonFile.json"
#             nodesData = getStateData(voltageFile, updatedVoltageFile, jsonFile)
#
#             for indexNode in range(0,len(nodesData)):
#                 if(float(lstOfNodesInfInitState[indexNode]["voltA_mag"])!=0):
#                     diffPhaseA =abs(1-(float(nodesData[indexNode]["voltA_mag"])/float(lstOfNodesInfInitState[indexNode]["voltA_mag"])))
#                 else:
#                     diffPhaseA=0
#                 if (float(lstOfNodesInfInitState[indexNode]["voltB_mag"]) != 0):
#                     diffPhaseB =abs(1-(float(nodesData[indexNode]["voltB_mag"]) /float(lstOfNodesInfInitState[indexNode]["voltB_mag"])))
#                 else:
#                     diffPhaseB=0
#
#                 if (float(lstOfNodesInfInitState[indexNode]["voltC_mag"]) != 0):
#                     diffPhaseC =abs(1-(float(nodesData[indexNode]["voltC_mag"]) / float(lstOfNodesInfInitState[indexNode]["voltC_mag"])))
#                 else:
#                     diffPhaseC=0
#                 if(diffPhaseA >= _threshold or diffPhaseB >= _threshold or diffPhaseC >= _threshold):
#                     lst=[0]*3
#                     lst[0]=diffPhaseA
#                     lst[1]=diffPhaseB
#                     lst[2]=diffPhaseC
#                     mapNodeValue[nodesData[indexNode]["node_name"]] = lst
#                     if(nodesData[indexNode]["node_name"] in notConv):
#                         notConv.remove(nodesData[indexNode]["node_name"])
#
#
#         mapCapacitorRadius[index] =  mapNodeValue
#     print("Radius: ")
#     printCapacitorAndNodes(mapCapacitorRadius)
#     print("___________________Not Conv_____________________")
#     print(set(notConv))
#     print("Num of Nodes not Conv : " + str(len(set(notConv))))
#     print("________________________________________________")
#     return mapCapacitorRadius
# def getSpecialRadius(mapCapacitorRadius):
#
#     lstOfKeysToDelete=[]
#     for mainIndex in range(1, len(mapCapacitorRadius)):
#         mainKeysLst = mapCapacitorRadius[mainIndex].keys()
#         if(len(mainKeysLst)>0):
#             for secondIndex in range(mainIndex+1,len(mapCapacitorRadius)+1):
#                 secondKeysLst =mapCapacitorRadius[secondIndex].keys()
#                 if(len(secondKeysLst)>0):
#                     lstOfKeysToDelete = listIntersection(mainKeysLst, secondKeysLst)
#
#                 mapCapacitorRadius[mainIndex] = entries_to_remove(lstOfKeysToDelete,mapCapacitorRadius[mainIndex])
#                 if(mainIndex == len(mapCapacitorRadius) -1 ):
#                     mapCapacitorRadius[mainIndex+1] = entries_to_remove(lstOfKeysToDelete, mapCapacitorRadius[mainIndex+1])
#
#                 lstOfKeysToDelete=[]
#     print("UNIQUE")
#     printCapacitorAndNodes(mapCapacitorRadius)
#     return mapCapacitorRadius
#
# def listIntersection(a , b):
#     c = list(set(a) & set(b))
#     return c
#
#
# def entries_to_remove(entries, the_dict):
#     for key in entries:
#         if key in the_dict:
#             del the_dict[key]
#     return the_dict
#
#
# def  printCapacitorAndNodes(mapCapacitorRadius):
#     for mainIndex in range(1, len(mapCapacitorRadius) + 1):
#         if mainIndex!=1 and mainIndex!=3:
#             print("Capacitor "+str(mainIndex)+" : "+str(len(mapCapacitorRadius[mainIndex])))
#             print(mapCapacitorRadius[mainIndex])F
#
#
# def getAllCLA(G):
#     H = G.to_directed()
#     lstEven = uniq(H.edges)
#     # lstEven = [v for i, v in enumerate(lst) if i % 2 == 0]
#     print(list(H.edges))
#     print(lstEven)
#     T = nx.DiGraph()
#     T.add_edges_from(lstEven)
#     print(list(T.edges))
#     #print(nx.is_directed_acyclic_graph(G))
#     print(nx.find_cycle(G))
#     write_dot(T, "europeanTreeGraph.dot")
#     #return CLA(T)


# def getlistOfUnbalancedNodes(voltfile,updateVolt, jsonFile):
#     lstOfData = dataAnalyzer.getStateData(VoltageFile, updatedVoltageFile, jsonFile)
#     tresholdVoltage = 50
#     listOfUnbalancedNodes = []
#     for node  in lstOfData:
#         if(abs(int(node["voltA_mag"])-int(node["voltB_mag"]))>tresholdVoltage or
#                 abs(int(node["voltA_mag"]) - int(node["voltC_mag"])) > tresholdVoltage or
#                 abs(int(node["voltB_mag"]) - int(node["voltC_mag"])) > tresholdVoltage):
#             listOfUnbalancedNodes.append(node)
#         elif (abs(int(node["voltA_angle"])-int(node["voltB_angle"]))>2.095 or
#                 abs(int(node["voltA_angle"]) - int(node["voltC_angle"]))  >2.095 or
#                 abs(int(node["voltB_angle"]) - int(node["voltC_angle"])) >2.095):
#             listOfUnbalancedNodes.append(node)
#
#     return  listOfUnbalancedNodes


# def showGraph(dictNodeVoltage):
#     vertexes = [ x for x in range(len(dictNodeVoltage))]
#
#     plt.plot(dictNodeVoltage.keys(), dictNodeVoltage.values(),'ro')
#     plt.ylabel('Voltage')
#     plt.xlabel('Node Number')
#     ax = plt.gca()
#     ax.invert_yaxis()
#     plt.show()