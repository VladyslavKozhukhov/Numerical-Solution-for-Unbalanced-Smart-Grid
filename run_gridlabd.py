import subprocess
import os
#"./analytic_data/folder1/")
def runGridlabd(pathOfDir,fileName):
    finnished = True
    p = subprocess.Popen(['gridlabd', fileName],cwd =pathOfDir)
    try:
        p.wait(5)
    except subprocess.TimeoutExpired:
        p.kill()
        finnished = not finnished

    return finnished

