import fileinput
import os
import shutil

def getIndexOfCapacitorInsideFile(path):
    file = open(path, 'r+')
    inputFile = file.read()
    substr= "object capacitor"
    lst =[]
    lstcapacitors =[]
    capacitor="	capacitor_"
    index = 1
    mapCapacitorIndex={}
    mapNodeCapacitors={}
    insideNode = False
    indexMain = 1
    lstOfCapacitorsInsideNode = []

    lstFile=str(inputFile).split("\n")
    for line in lstFile:
        if substr in line:
            if len(lstOfCapacitorsInsideNode)!=0:
                mapNodeCapacitors[indexMain]=lstOfCapacitorsInsideNode
                lstOfCapacitorsInsideNode = []
            #lst.append(index)
            indexMain = index
            insideNode = False
        if capacitor in line:
            insideNode = True
            mapCapacitorIndex[index]=line
            lstOfCapacitorsInsideNode.append(mapCapacitorIndex)
            mapCapacitorIndex={}

        index =index +1

    if(insideNode):
        mapNodeCapacitors[indexMain] = lstOfCapacitorsInsideNode

    print(mapNodeCapacitors)
    file.close()
    return mapNodeCapacitors

def readFile(inputFile):
    #inputFile = "gridLAB_D_Model.glm"
    fileUpdated = open(inputFile,'r+')
    file = fileUpdated.read()
    getIndexOfCapacitorInsideFile(getIndexOfCapacitorInsideFile(file))

def replaceClock():

    entries = os.scandir('analytic_data/folder1/')
    counter = 0
    for entry in entries:
        with open(entry) as f:
            lines = f.readlines()
            lines[1]= "\tstarttime '2000-01-01 12:00:00';\n"
            lines[2]= "\tstoptime '2000-01-01 12:00:01'; \n"

        f.close()
        with open(entry, "w") as f:
            f.writelines(lines)
        f.close()

def createFolders(max):
        for i in range(0,max):
            cmd = "mkdir folder"+str(i)
            os.system(cmd)
def moveFile():
    entries = os.listdir('Files/')
    counter = 0
    for entry in entries:
        name = entry.split(".")
        index = name[0].split("_")
        shutil.move('Files/'+str(entry),"folder"+index[1])
        counter = counter +1

def threadFunc(index):
    #lock.acquire()
    path = "C:\\Users\\VladKo\\Documents\\GridLAB-D\\FinalProject\\"
    os.chdir(path)

    a = os.getcwd()
    entries = os.listdir('folder' + str(index) + '/')
    for entry in entries:
        # os.chdir("/folder"+str(index))
        folder = "folder"+str(index)
        path = "C:\\Users\\VladKo\\Documents\\GridLAB-D\\FinalProject\\"
        os.chdir(path+folder)
        # cmd = "gridlabd " + 'folder' + str(index) + '/' + entry
        cmd = "gridlabd " + entry
        print("start")
        os.system(cmd)
    #lock.release()

def execEachFile(max):

    threadLst = []
    for i in range(0,max):
        threadFunc(i)
    #     t =threading.Thread(target = threadFunc, args = (i,))
    #     threadLst.append(t)
    #
    # for t in threadLst:
    #     t.start()
    # for t in threadLst:
    #     t.join(45)

    print("finish")
# shutil.move("Voltage_8500_1.csv", "folder" + str(i))
# shutil.move("Current_8500.csv", "folder" + str(i))
