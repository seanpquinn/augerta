import os
import sys
import subprocess
import time
import shutil
import glob

#Config parameters
# USER CAN EDIT

basePath = "/bigData/irodsData/showers/auger_ta_corsika76400/"
hadModel = "QGSJII-04"
primComp = "proton"
evtNum = "34"
runNum = 3
cpuCores = 6
evtGenPath = "/auger_fd_scale_reconstruct/QGSJETII-04/run1/"

#  Main script below, should not need to be edited

runFolders = ["%s_run%i" %(evtNum,i+1) for i in range(runNum)]
#runFolder = "%s_run1" %evtNum

for runFolder in runFolders:

  check_dir = os.path.isdir(runFolder)
  if not check_dir:
    os.mkdir(runFolder)    
  fullPath = basePath+hadModel+"/"+primComp+"/"+runFolder+"/"

  showerFiles = os.listdir(fullPath)

  showerFiles = [x for x in showerFiles if ".part" in x]

#print(showerFiles)

  with open("Dummy_EventFileReader.xml", "r") as f:
    freadTemplate = f.readlines()

#print(freadTemplate)

#Get dummy file list index entry
  dfi = freadTemplate.index("\t    putPathHere\n")

#print(dfi)

#Before doing any reconstructions, remove any data files. These are append mode
#so we must have a clean file for new writes
  try:
    os.remove("DataWriterTest.dat")

  except:
    None

  for i,j in enumerate(showerFiles):
    freadTemplate[dfi] = "\t   " + fullPath + j + "\n"
    print(freadTemplate[dfi])
    shower_num = j.split(".")[0]
    job_folder = runFolder + "/" + shower_num
    chk_dir = os.path.isdir(job_folder)
    if not chk_dir:
      os.mkdir(job_folder)
    with open("EventFileReader.xml", "w") as f:
      f.writelines(freadTemplate)
    xml_cards = glob.glob('*.xml')
    # Copy xml config to job folder
    for xf in xml_cards:
      shutil.copy(xf,job_folder)
    # Copy EventGenerator with core positions
    shutil.copy(evtGenPath+evtNum+"/1/"+"EventGenerator.xml",job_folder+"/"+"EventGenerator.xml") 
    # Copy executable
    shutil.copy('userAugerOffline',job_folder)
    # Copy CachedShowerRegeneratorOG seems like library object needed
    shutil.copytree('CachedShowerRegeneratorOG',job_folder+"/"+"CachedShowerRegeneratorOG")
    # Run jobs until max CPU cores reached
    os.chdir(job_folder)
    if (i+1) % cpuCores == 0:
      pid = subprocess.Popen("./userAugerOffline")
      pid.communicate()
    else:
        subprocess.Popen("./userAugerOffline")
    os.chdir('../..')
    # Sleep to allow disk I/O for corsika file
    time.sleep(20)

