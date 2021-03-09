import cv2 #pip install opencv-python
import pandas as pd #pip install pandas2
import numpy as np #pip install numpy
import os 
import math 
from math import log,ceil 
import subprocess
import shutil
import re

texWidthLimit = 3840 #maximum texture size
swapJPGTo = ".ktx2" #rename all .jpg mentions to .ktx2
swapPNGTo = ".ktx2" #rename all .png mentions to .ktx2
ktx2Args = "--t2 --bcmp --genmipmap" #https://khronos.org/ktx/documentation/ktxtools/toktx.html
 
folderToTexToKTX2 = os.getcwd()  
allFilesFolder = folderToTexToKTX2 + "/_files/AllFiles/"
all3DFolder = folderToTexToKTX2 + "/_files/AllFiles/"
tempResize_folder = folderToTexToKTX2 + "/_tempResized/" 
doneAllFolder = folderToTexToKTX2 + "/_converted/" 
toktxExeFolder = folderToTexToKTX2 + "/tools/"
csvPath = folderToTexToKTX2 + '/_files/TextureWidthTargets_optional.csv'
useCSV = False

if os.path.exists(csvPath):
    csv = pd.read_csv(csvPath)  
    useCSV = True

if os.path.exists(tempResize_folder) == False:
    os.makedirs(tempResize_folder)
if os.path.exists(doneAllFolder) == False:
    os.makedirs(doneAllFolder)

def pot_convert(number):
    return pow(2, ceil(log(number)/log(2)))

def find_imageTargetWidth(name): 
    i = 0
    while i < csv.index.stop:
        if csv['FileName'].loc[i] == name:
            return csv['Target Width'].loc[i]
        i = i + 1
    print("!!!! NEW FILE IN FOLDER THAT IS NOT IN THE CSV LIST: " + name);
         
def set_image(image, name):
    origin_width = image.shape[1]
    origin_height = image.shape[0]
    if(useCSV):
        received_target_width = find_imageTargetWidth(name)  
    else:
        received_target_width = origin_width
    if(received_target_width > texWidthLimit):
        received_target_width = texWidthLimit
    target_width = 0.0
    if math.isnan(received_target_width):
        target_width = origin_width
    else:
        target_width = received_target_width
        
    new_height = round(origin_height/origin_width*target_width)
    pot_height = pot_convert(new_height)
    pot_width = pot_convert(target_width)
    
    resized = cv2.resize(image, (pot_width, pot_height), interpolation = cv2.INTER_AREA)
    fileLoc = tempResize_folder + name
    cv2.imwrite(fileLoc, resized)

    filename = name
    resultName = os.path.splitext(filename)[0]
    args = toktxExeFolder + 'toktx.exe ' + ktx2Args + ' "' + doneAllFolder + resultName + '" "' + tempResize_folder + filename + '"'
    subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=False)
    os.remove(fileLoc) 

def set_gltf(_fileFolder, _fileName):
    shutil.copyfile(_fileFolder + _fileName, doneAllFolder + _fileName)
    with open(doneAllFolder + _fileName) as f:
        s = f.read()
    with open(doneAllFolder + _fileName, 'w') as f:
        s = re.sub('.jpg', swapJPGTo, s)
        s = re.sub('.png', swapPNGTo, s) 
        f.write(s)
    print(_fileName + " done!")
                
 
def parse_all_files(_folder):
    for filename in os.listdir(_folder):
        fileFormat = os.path.splitext(filename)[1]
        if(fileFormat == '.bin'): #copy to target folder
            shutil.copyfile(_folder + filename, doneAllFolder + filename)
        elif(fileFormat == '.gltf'):
            set_gltf(_folder, filename);
        elif(fileFormat == '.jpg' or fileFormat == '.jpeg' or fileFormat == '.png'):
            img = cv2.imread(os.path.join(_folder, filename), cv2.IMREAD_UNCHANGED)
            if img is not None:
                set_image(img, filename)
                print(filename + " done!")
            else:
                print ("!!!! Failed to load file " + filename)
        else:
            print("!!!! Unknown file format for file: " + filename)
 
FNULL = open(os.devnull, 'w')
parse_all_files(allFilesFolder)
os.rmdir(tempResize_folder) #remove the temp texture resize folder
print("----All files converted!")
