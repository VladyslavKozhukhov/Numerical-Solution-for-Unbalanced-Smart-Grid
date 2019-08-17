import glm
import graph_handler
import itertools
import sys
import data_analyzer
import run_gridlabd
import os
import parser as parser
path = "./analytic_data/folder1/allAnalyticData.json"
import networkx.algorithms.dag     as ancestors


def getProblemNodesFromTotalMapFile(pathToFile):
    return data_analyzer.fromJsonToPython(pathToFile)["UNDER_VOLTAGE_NODES"]
def getOverNodesFromTotalMapFile(pathToFile):
    return data_analyzer.fromJsonToPython(pathToFile)["OVERLOAD_NODES"]


# def getProblemNodesFromTotalMapFile(pathToFile):
#     return data_analyzer.fromJsonToPython(pathToFile)["PROBLEM_NODES"]
#
def getListOfA(mapOfAllCapacitors):
    lst=[]
    for cp in mapOfAllCapacitors:
        lst.append(list(mapOfAllCapacitors[cp][0].keys())[0])
    return lst
def updateCapacitorValue(file,lineNuber,value):
    replace_prefixA = "\tcapacitor_A "+str(value)+";\n"
    replace_prefixB = "\tcapacitor_B "+str(value)+";\n"
    replace_prefixC = "\tcapacitor_C "+str(value)+";\n"

    with open(file) as f:
        lines = f.readlines()
        lines[lineNuber-1] = replace_prefixA
        lines[lineNuber] = replace_prefixB
        lines[lineNuber+1] = replace_prefixC

    f.close()
    with open(file, "w") as f:
        f.writelines(lines)
    f.close()

def addCapacitor(file, name, parent, phase, cap_nominal_voltage, A, B, C):
    network = glm.load(file)

    lstOfObj = network['objects']
    dictMap = {}
    dictMap["name"] = "capacitor"
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
    dictMap["attributes"] = dictAttr
    dictMap["children"] = []
    lstOfObj.append(dictMap)

    glm.dump(network, file)


def addCapacitorText(file, name, parent, phase, cap_nominal_voltage, A, B, C):
    with open(file, 'a') as f:
        strOne = "object capacitor {\n" + "\tname " + name + ";\n" + "\tparent " + parent + ";\n" + "\tphases " + phase + ";\n"
        strTwo = "\tphases_connected " + phase + ";\n" + "\tcap_nominal_voltage " + str(cap_nominal_voltage) + ";\n"
        strThree = "\tcapacitor_A " + str(A) + ";\n" + "\tcapacitor_B " + str(B) + ";\n" + "\tcapacitor_C " + str(
            C) + ";\n"
        strFour = "\tswitchA CLOSED;\n" + "\tswitchB CLOSED;\n" + "\tswitchC CLOSED;\n"
        strFive = "}\n"

        f.write(strOne)
        f.write(strTwo)
        f.write(strThree)
        f.write(strFour)
        f.write(strFive)


# object capacitor {
#   name "cap_capbank3";
#   parent "Bus34";
#   phases ABC;
#   phases_connected ABC;
#   cap_nominal_voltage 240.177712;
#   capacitor_A 10000;
#   capacitor_B 10000;
#   capacitor_C 10000;
#    switchA CLOSED;
#     switchB CLOSED;
# 	 switchC CLOSED;
# }


def get_keys_by_value(dictOfElements, valueToFind):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item in listOfItems:
        if item[1] == valueToFind:
            listOfKeys.append(item[0])
    return listOfKeys


def choose_capacitor_to_split(splitable_capacitors):
    cap_to_split_num_of_children = 0
    cap_to_split_name = None
    for cap in splitable_capacitors.keys():
        if len(splitable_capacitors[cap][1]) > cap_to_split_num_of_children:
            cap_to_split_num_of_children = len(splitable_capacitors[cap][1])
            cap_to_split_name = cap
    return cap_to_split_name

def writeCapacitors(capacitors):
    capV=10000
    for cp in list(capacitors.keys()):
        totalMap = data_analyzer.fromJsonToPython("./analytic_data/folder1/allAnalyticData.json")
        voltage = totalMap["NODES"][cp]["nominal_voltage"]
        addCapacitor("./analytic_data/folder1/gridLAB_D_Model.glm","cap"+str(cp),cp,"ABC",voltage,capV,capV,capV)
        addCapacitorText("./analytic_data/folder1/myTest.glm","cap"+str(cp),cp,"ABC",voltage,capV,capV,capV)

def tryToSolve(capacitors,G):
    os.system("cp -avr ./analytic_data/folder0/* ./analytic_data/folder1/.")
    flag = True
    allBad = 0
    iter = 20
    allSameVl = False
    samVL = 0
    lstOfCapValue = [7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,20000,30000]
    capVlDict={}
    allBad = 0

    while(flag and iter >0):
        if not allSameVl:
            samVL = sameValueCapacitors(capacitors)
            if(samVL == -1):
                return 1
            cpValues = [samVL] * len(capacitors)
            allSameVl = not allSameVl
            capVlDict = dict(zip(capacitors.keys(), cpValues))

        mapOfCapacitors = parser.getIndexOfCapacitorInsideFile("./analytic_data/folder1/myTest.glm")
        listOfA = getListOfA(mapOfCapacitors)
        bestCap = get_best_capacitor_for_each_out_of_range_node(capacitors, G)
        pbNodes = getProblemNodesFromTotalMapFile("./analytic_data/folder1/allAnalyticData.json")

        lstOfCapToUpdate = listOFIssueCap(bestCap,pbNodes)
        if(allBad < len(lstOfCapToUpdate) ):
            allBad = 0
            for cp in  lstOfCapToUpdate:
                updateCapacitorValue("./analytic_data/folder1/myTest.glm",listOfA[list(capacitors.keys()).index(cp)],int(capVlDict[cp])+500)
                # updateCapacitorValue("./analytic_data/folder1/gridLAB_D_Model.glm",listOfA[list(capacitors.keys()).index(cp)],int(capVlDict[cp])+500)

                if(run_gridlabd.runGridlabd("./analytic_data/folder1/", "myTest.glm")):
                    data_analyzer.createTotalData("output_voltage_1.csv")
                    if len(getProblemNodesFromTotalMapFile(path).keys()) == 0 and len(
                        getOverNodesFromTotalMapFile(path).keys()) == 0:
                        print("Balanced")
                        return 1
                if len(getOverNodesFromTotalMapFile(path).keys()) == 0:
                    capVlDict[cp] = int(capVlDict[cp])+500
                else:
                    updateCapacitorValue("./analytic_data/folder1/myTest.glm", listOfA[list(capacitors.keys()).index(cp)],int(capVlDict[cp])-500)
                    # updateCapacitorValue("./analytic_data/folder1/gridLAB_D_Model.glm",
                    #                      listOfA[list(capacitors.keys()).index(cp)], int(capVlDict[cp]))
                    allBad = allBad +1

        else:
            for cp in list(capacitors.keys()):
                updateCapacitorValue("./analytic_data/folder1/myTest.glm",listOfA[list(capacitors.keys()).index(cp)],int(capVlDict[cp])+500)
                # updateCapacitorValue("./analytic_data/folder1/gridLAB_D_Model.glm",listOfA[list(capacitors.keys()).index(cp)],int(capVlDict[cp])+500)
                if(run_gridlabd.runGridlabd("./analytic_data/folder1/", "myTest.glm")):
                    data_analyzer.createTotalData("output_voltage_1.csv")
                    if len(getProblemNodesFromTotalMapFile(path).keys()) == 0 and len(
                        getOverNodesFromTotalMapFile(path).keys()) == 0:
                        print("Balanced")
                        return 1
                if len(getOverNodesFromTotalMapFile(path).keys()) == 0:
                    capVlDict[cp] = int(capVlDict[cp])+500
                else:
                    updateCapacitorValue("./analytic_data/folder1/myTest.glm", listOfA[list(capacitors.keys()).index(cp)],int(capVlDict[cp])-500)
                    # updateCapacitorValue("./analytic_data/folder1/gridLAB_D_Model.glm",
                    #                      listOfA[list(capacitors.keys()).index(cp)], int(capVlDict[cp]))

        iter=iter -1

    print("Cant balance with this amout and type of these capacitors")
        # "./analytic_data/folder1/")

    return -1
def listOFIssueCap(bestCap,pbNodes):
    lst=[]
    # bestCap["Bus47"][0]#bus32
    for pb in pbNodes:
        lst.append(bestCap[pb][0])

    return lst

def sameValueCapacitors(capacitors):
    mxx= len(capacitors)
    last = 0
    flagLeave = False
    lstOfCapValue = [100,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,20000,30000]
    for capV in lstOfCapValue:
        if not flagLeave:
            os.system("cp -avr ./analytic_data/folder0/myTest.glm ./analytic_data/folder1/.")
            os.system("cp -avr ./analytic_data/folder0/gridLAB_D_Model.glm ./analytic_data/folder1/.")

            for cp in list(capacitors.keys()):
                totalMap = data_analyzer.fromJsonToPython("./analytic_data/folder1/allAnalyticData.json")
                voltage = totalMap["NODES"][cp]["nominal_voltage"]
                addCapacitor("./analytic_data/folder1/gridLAB_D_Model.glm","cap"+str(cp),cp,"ABC",voltage,capV,capV,capV)
                addCapacitorText("./analytic_data/folder1/myTest.glm","cap"+str(cp),cp,"ABC",voltage,capV,capV,capV)
            if(run_gridlabd.runGridlabd("./analytic_data/folder1/", "myTest.glm")):
                data_analyzer.createTotalData("output_voltage_1.csv")
                if len(getProblemNodesFromTotalMapFile(path).keys())<=mxx and len(getOverNodesFromTotalMapFile(path).keys())==0:
                    mxx = len(getProblemNodesFromTotalMapFile(path).keys())
                    last = capV
                if len(getOverNodesFromTotalMapFile(path).keys())>0:
                    flagLeave = True
                    continue
            if len(getProblemNodesFromTotalMapFile(path).keys())==0 and len(getOverNodesFromTotalMapFile(path).keys())==0:
                print("Balanced")
                return -1
        else:
            continue
    os.system("cp -avr ./analytic_data/folder0/myTest.glm ./analytic_data/folder1/.")
    os.system("cp -avr ./analytic_data/folder0/gridLAB_D_Model.glm ./analytic_data/folder1/.")
    for cp in list(capacitors.keys()):
        totalMap = data_analyzer.fromJsonToPython("./analytic_data/folder1/allAnalyticData.json")
        voltage = totalMap["NODES"][cp]["nominal_voltage"]
        addCapacitor("./analytic_data/folder1/gridLAB_D_Model.glm", "cap" + str(cp), cp, "ABC", voltage, last, last,last)
        addCapacitorText("./analytic_data/folder1/myTest.glm", "cap" + str(cp), cp, "ABC", voltage, last, last, last)
    return last

# splitable capaciors: key -> name of capacitor location, value -> unique over/under-loaded children (must be assigned to capacitor)
def get_splitable_capacitors(current_capacitor_placement, capacitor_bank_size):
    splitable_capacitors = {}
    for cap in current_capacitor_placement.keys():
        unique_children = get_cla_unique_children(current_capacitor_placement, cap)
        if can_replace_capacitor(capacitor_bank_size, len(current_capacitor_placement), len(unique_children)):
            splitable_capacitors[cap] = (
                unique_children, current_capacitor_placement[cap])  # (unique children, all children)
    return splitable_capacitors


# def increase_num_of_capacitors(current_capacitor_placement, capacitor_bank_size):
#     while capacitor_bank_size != len(current_capacitor_placement):
#         if (len(current_capacitor_placement) > capacitor_bank_size):
#             print("error - increasing number of capacitors")
#             sys.exit()
#         splitable_capacitors = get_splitable_capacitors(current_capacitor_placement, capacitor_bank_size)
#         cap = choose_capacitor_to_split(splitable_capacitors)
#         num_of_capacitors_remaining = capacitor_bank_size - len(current_capacitor_placement)
#         unique_children = splitable_capacitors[cap][0]
#         added_capacitors = []
#         for child in unique_children:  # first add unique to capacitors dict (can add capacitors the prev capacitor location is splitable)
#             if child not in current_capacitor_placement.keys():
#                 current_capacitor_placement[child] = {}
#                 added_capacitors.append(child)
#         # add as many capacitors as possible (from what is left)
#         for node in splitable_capacitors[cap][1]:  # iterate over all children of capacitor
#             if len(current_capacitor_placement) - 1 == capacitor_bank_size:
#                 break  ##TODO choose the one with the least number of clas
#             if node not in current_capacitor_placement.keys():
#                 current_capacitor_placement[node] = {}
#                 added_capacitors.append(node)
#         current_capacitor_placement.pop(cap)


def increase_num_of_capacitors(current_capacitor_placement, capacitor_bank_size):
    while capacitor_bank_size != len(current_capacitor_placement):
        if (len(current_capacitor_placement) > capacitor_bank_size):
            print("error - increasing number of capacitors")
            sys.exit()
        splitable_capacitors = get_splitable_capacitors(current_capacitor_placement, capacitor_bank_size)
        cap = choose_capacitor_to_split(splitable_capacitors)
        unique_children_of_capacitor = set(splitable_capacitors[cap][0])
        all_capacitor_children = set(splitable_capacitors[cap][1])
        for child in unique_children_of_capacitor:  # first add unique to capacitors dict (can add capacitors the prev capacitor location is splitable)
            if child not in current_capacitor_placement.keys():
                current_capacitor_placement[child] = {}
                current_capacitor_placement.get(cap).remove(child)
        # add as many capacitors as possible (from what is left)
        for node in all_capacitor_children:  # iterate over all children of capacitor
            if len(current_capacitor_placement) == capacitor_bank_size and cap_has_children(cap,current_capacitor_placement)\
                    or not cap_has_children(cap,current_capacitor_placement)  :
                break  ##TODO choose the one with the least number of clas
            if node not in current_capacitor_placement.keys():
                current_capacitor_placement[node] = {}
                current_capacitor_placement.get(cap).remove(node)
        if not cap_has_children(cap,current_capacitor_placement):
            current_capacitor_placement.pop(cap)



# for decrease choose the 2 closest cla's
def decrease_num_of_clas(out_of_range_nodes,numOfCapacitors, G, T,problemNodes):
    flag = False
    while not flag :
        all_pairs_distance = {}
        clas={}
        all_pairs_cla = {}
        for pair in list(itertools.combinations(out_of_range_nodes.keys(), 2)):
            all_pairs_distance[pair] = graph_handler.getPathLenBetweenNodes(G, pair[0], pair[1])
            cla = graph_handler.getCLABetweenPair(T, pair[0], pair[1])
            all_pairs_cla[pair] = cla
            if cla in clas.keys():  # create a dict of cla and its children
                clas[cla].add(pair[0])
                clas[cla].add(pair[1])
            else:
                clas[cla] = {pair[0], pair[1]}
        if(len(clas )== numOfCapacitors):
            return clas.keys()
        if (len(clas) < numOfCapacitors):
            numOfDegree = numOfCapacitors - len(clas)
            maxLst = [-1]*numOfDegree
            maxLstNode=[0]*numOfDegree
            for i in range(0,numOfDegree):
                for cp in problemNodes:
                    for claNode in list(clas.keys()):
                        nm = graph_handler.getPathLenBetweenNodes(G, cp, claNode)
                        if maxLst[i] < nm:
                            if(cp not in maxLstNode):
                                maxLst[i] = nm
                                maxLstNode[i] = cp
            return list(clas.keys())+maxLstNode
        else:
            out_of_range_nodes =clas


# def get_cla_children_from_kes

# clas is a map -> key: the cla name value: a set of children
def get_cla_unique_children(current_capacitor_placement, lookup_capacitor):
    not_unique_children = []
    for child in current_capacitor_placement[lookup_capacitor]:
        for cla in current_capacitor_placement.keys():
            if cla != lookup_capacitor and child in current_capacitor_placement[cla]:
                not_unique_children.append(child)
                break
    unique_cla_children = [child for child in current_capacitor_placement[lookup_capacitor] if
                           child not in not_unique_children]
    return unique_cla_children


def can_replace_capacitor(num_of_capacitors_in_bank, current_capacitor_num, num_of_unique_children_for_capacitor):
    return num_of_capacitors_in_bank - current_capacitor_num >= num_of_unique_children_for_capacitor - 1

def get_best_capacitor_for_each_out_of_range_node(current_capacitor_placement, G):
    capacitors = current_capacitor_placement.keys()
    out_of_range_nodes_closest_capacitors = {}
    for cap in capacitors:
        for node in current_capacitor_placement[cap]:
            if(node!= None):
                distance_node_from_cap = graph_handler.getPathLenBetweenNodes(G, node, cap)
                if node not in out_of_range_nodes_closest_capacitors.keys():
                    out_of_range_nodes_closest_capacitors[node] = (cap, distance_node_from_cap)
                else:
                    if out_of_range_nodes_closest_capacitors[node][1]>distance_node_from_cap:
                        out_of_range_nodes_closest_capacitors[node] = (cap,distance_node_from_cap)
    return out_of_range_nodes_closest_capacitors

def capacitorsPlacementAlgorithm(numOfCapacitors, G, T, out_of_range_nodes):
    validate_number_of_capacitors(numOfCapacitors, out_of_range_nodes)
    all_pairs_distance = {}
    all_pairs_cla = {}
    currecnt_capacitor_placement = {}
    for pair in list(itertools.combinations(out_of_range_nodes.keys(), 2)):
        all_pairs_distance[pair] = graph_handler.getPathLenBetweenNodes(G, pair[0], pair[1])
        cla = graph_handler.getCLABetweenPair(T, pair[0], pair[1])
        all_pairs_cla[pair] = cla
        if cla in currecnt_capacitor_placement.keys():  # create a dict of cla and its children
            currecnt_capacitor_placement[cla].add(pair[0])
            currecnt_capacitor_placement[cla].add(pair[1])
        else:
            currecnt_capacitor_placement[cla] = {pair[0], pair[1]}
    if numOfCapacitors > len(currecnt_capacitor_placement):
        increase_num_of_capacitors(currecnt_capacitor_placement, numOfCapacitors)
    if numOfCapacitors < len(currecnt_capacitor_placement):
        dictToRet = {}

        lst = decrease_num_of_clas(currecnt_capacitor_placement, numOfCapacitors, G, T, list(out_of_range_nodes.keys()))
        dictToRet = dict([(key, []) for key in lst])

        for  outNode in out_of_range_nodes:
            lstAnc = ancestors.ancestors(T,outNode)
            for kk in lst :
                if kk in lstAnc:
                    if kk in dictToRet.keys():
                        dictToRet[kk].append(outNode)


        for cp in  dictToRet:
            if len(dictToRet[cp])==0:
                dictToRet[cp].append(cp)



        currecnt_capacitor_placement = dictToRet

    return currecnt_capacitor_placement

def validate_number_of_capacitors(numOfCapacitors, out_of_range_nodes):
    if (int(numOfCapacitors) > len(out_of_range_nodes)):
        print("error - num of capacitor > out of range nodes")
        sys.exit()


# def test1():
#     a = capacitorsPlacementAlgorithm(6, G, T, {'LOAD8': 4, 'LOAD10': 4, 'LOAD9': 4, 'LOAD1': 4, 'LOAD49': 4, 'LOAD51': 4})
#     print(str(a))
#     a = capacitorsPlacementAlgorithm(6, G, T,{'LOAD8': 4, 'LOAD10': 4, 'LOAD9': 4, 'LOAD1': 4, 'LOAD49': 4, 'LOAD51': 4})
#     print(str(a))
#
#     a = capacitorsPlacementAlgorithm(5, G, T, {'Bus249': 4, 'Bus248': 4,'Bus270': 4,'Bus271': 4,'Bus272':4,'Bus263':4})
#     print(str(a))


# G = graph_handler.load("resources/Model_European_System/savedGraphEurope.adjlist")
# T = graph_handler.convertToDirectedGraph(G)
# test1()


def cap_has_children(cap,current_capacitor_placement):
    return len(current_capacitor_placement.get(cap)) != 0





if __name__ == '__main__':
    capNum = input("Please entter num of capacitors: ")
    os.system("cp -avr ./resources/Model_European_System/glm/* ./analytic_data/folder0/. ")
    if(run_gridlabd.runGridlabd("./analytic_data/folder0/", "myTest.glm")):
        data_analyzer.createTotalData("output_voltage_1.csv", 0)
        lstOfProblemNodes = getProblemNodesFromTotalMapFile("./analytic_data/folder0/allAnalyticData.json")
        print("Num  of under voltage nodes : " + str(len(lstOfProblemNodes)))
        allDataFileBefore =data_analyzer.fromJsonToPython("./analytic_data/folder0/allAnalyticData.json")
        print(allDataFileBefore["UNDER_VOLTAGE_NODES"])
        if(len(lstOfProblemNodes)==0):
            print("Net Is Balanced")


        graph_handler.draw("europeanTreeGraph.dot", allDataFileBefore, "netBefore.jpeg")


        G = graph_handler.load("resources/Model_European_System/savedGraphEurope.adjlist")
        T = graph_handler.convertToDirectedGraph(G)
        # a = capacitorsPlacementAlgorithm(4, G, T,{'Bus102': 4, 'Bus106': 4, 'Bus109': 4, 'Bus88': 4, 'Bus290': 4, 'Bus327': 4})
        lstOfCapacitorsPlacement = capacitorsPlacementAlgorithm(int(capNum), G, T,lstOfProblemNodes )
        print("Caapacitor placement : "+ str(lstOfCapacitorsPlacement.keys()))
        tryToSolve(lstOfCapacitorsPlacement,G)
        lstOfProblemNodes = getProblemNodesFromTotalMapFile("./analytic_data/folder1/allAnalyticData.json")
        print("Num  of under voltage nodes : " + str(len(lstOfProblemNodes)))
        allDataFileBefore =data_analyzer.fromJsonToPython("./analytic_data/folder1/allAnalyticData.json")
        print(allDataFileBefore["UNDER_VOLTAGE_NODES"])
        allDataFileAfter =data_analyzer.fromJsonToPython("./analytic_data/folder1/allAnalyticData.json")
        graph_handler.draw("europeanTreeGraph.dot",allDataFileAfter, "netAfter.jpeg")



    # updateCapacitorValue("./analytic_data/folder1/myTest.glm",listOfA[1],7777)
