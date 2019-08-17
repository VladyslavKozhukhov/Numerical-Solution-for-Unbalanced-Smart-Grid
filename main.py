import data_analyzer
import network_capacitors_placement
import graph_handler

# minValue = 0.95
# numOfNodes = 4883
# global _listOfMapAllZeroCapacitors
# global _capacitorsValueMap
# global _capacitorsRadiusMap
# VoltageFile  = "data/0/output_voltage_1.csv"
# #VoltageFile = "data/0/Voltage_8500_1.csv"
# updatedVoltageFile = "data/0/output_voltage_1_no_2_first_lines.csv"
# jsonFile = "data/0/file.json"
# allCapacitorsZeroFile = "data/0/output_voltage_1.csv"
# inputFile = "data/0/gridLAB_D_Model.glm"
# updatedFile = "UpdatedFile.glm"


# global pid
# lock = threading.Lock()
#
#
#
# def runGridLab(inputFile):
#     cmd = 'gridlabd ' + inputFile
#     os.system(cmd)


#
# def handler8500(network):
#     ### todo networksCreator.create(network)
#     parser.replaceClock()
#    # parser.createFolders(256)
#    # parser.moveFile()
#    # parser.execEachFile(256)
#     fileOpen = open(inputFile,'r+')
#     #addCapacitorToNode()
#     mapOfIndexandValues = parser.getIndexOfCapacitorInsideFile(fileOpen.read())
#     _capacitorsValueMap = mapOfIndexandValues
#
#     #prepareData and get Raius
#     _listOfMapAllZeroCapacitors = data_analyzer.getStateData(VoltageFile, updatedVoltageFile, jsonFile)
#     _capacitorsRadiusMap = data_analyzer.findRaiusOfEachCapacitor(_listOfMapAllZeroCapacitors, _capacitorsValueMap)
#     _specialRaiusMap = data_analyzer.getSpecialRadius(_capacitorsRadiusMap)




def handler(numOfFiles, numOfCapacitors, pathToJsonGraph):
    # Check if net is voltage balanced
    data_analyzer.createTotalData("output_voltage_1.csv", 1)
    data_analyzer.bestConfig(1)
    lstOfProblemNodes = network_capacitors_placement.getProblemNodesFromTotalMapFile("analytic_data/folder0/allAnalyticData.json")
    G = graph_handler.getGraphOfNet(pathToJsonGraph)
    T = graph_handler.convertToDirectedGraph(G)

    #
    #
    # SHOW graph
    #
    #

    if(len(lstOfProblemNodes) == 0):
        print("Net Is Voltage Balanced")
    else:
        print("Lets Start")
        network_capacitors_placement.capacitorsPlacementAlgorithm(numOfCapacitors, G, T, lstOfProblemNodes)
#
# #handler()
# if __name__== "__main__":
#     capacitors = 2
#     files = 4
#     pathToJsonGraph = "savedGraphEurope.json"
#     handler(files, capacitors, pathToJsonGraph)


#runAllFiles()