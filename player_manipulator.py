import os
from shutil import copyfile
from random import randint
import run_gridlabd
newDirName = "system_with_load"
newLoad = 70


def is_in_load_list(fileName):
    for load in loads_to_change:
        if str(load) + ".player" in fileName:
            return True
    return False


europeanSystemDir = 'resources/Model_European_System/glm'
newNetworkDir = europeanSystemDir + "/" + newDirName
europeanSystemName = "gridLAB_D_Model.glm"
# os.mkdir(newNetworkDir)
flag = True
while(flag):
    loads_to_change = [7, 30, 11,50]
    loads_to_change[0]= randint(1, 53)
    loads_to_change[1]= randint(1, 53)
    loads_to_change[2]= randint(1, 53)
    loads_to_change[2]= randint(1, 53)

    copyfile(europeanSystemDir + "/" + europeanSystemName, newNetworkDir + "/" + europeanSystemName)
    for filename in os.listdir(europeanSystemDir):
        if filename.split(".")[-1] == "player":
            isInLoadList = is_in_load_list(filename)
            with open(europeanSystemDir + "/" + filename) as fp:
                new = open(newNetworkDir + "/" + filename, "w+")
                for line in fp:
                    if isInLoadList:
                        load = line.split(',')[1][:-1].strip()
                        line = line.replace(load, str(newLoad))
                    new.write(line)


    if(run_gridlabd.runGridlabd("./resources/Model_European_System/glm/system_with_load/", "myTest.glm")):
        flag= not flag

os.system("mv ./resources/Model_European_System/glm/system_with_load/load* ./resources/Model_European_System/glm/.")