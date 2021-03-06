"""
Author: Amund M. Raniseth
Date: 25.12.2021

Reads the varoius types of diffraction data
"""

import os 
from fdat.log import LOG
import numpy as np

def read(filename):
    _fn, ext = os.path.splitext(filename)
    if ext == ".xye":
        xye_t = read_xye(filename)
        datetime_object = None
    elif ext == ".brml":
        xye_t, datetime_object = read_brml(filename)
    return xye_t, datetime_object
        

def read_xye(filename):
    try:
        with open(filename, 'r') as f:
            raw = f.readlines()
    except Exception as e:
        LOG.warning("Error occurred while opening the file {}: {}".format(filename, e))


    
    xye = np.zeros((len(raw),3)) # creates 3dim numpy array with x(2theta), y(intensity) and e(error)
        
    for i,line in enumerate(raw):
        xye[i] = np.array(list(map(float, line.split())))

    # Transpose array is easier to plot
    xye_t = np.transpose(xye)

    return xye_t



"""
Made by Rasmus Vester Thøgersen, NAFUMA, Dept. of Chemistry, University of Oslo 2021
Modified by Amund Raniseth 25.12.2021
"""
def read_brml(filename):
    
    import pandas as pd
    import zipfile
    import xml.etree.ElementTree as ET
    import shutil

    if not os.path.isdir("./temp"):
        os.mkdir("./temp")

    # Extract the RawData0.xml file from the brml-file
    with zipfile.ZipFile(filename, 'r') as brml:
        with brml.open("Experiment0/RawData0.xml") as Rawxml:
            tree = ET.parse(Rawxml)


    root = tree.getroot()

    twoth = []
    intensity = []

    datetime_text = root.findall('./TimeStampStarted')[0].text
    import dateutil.parser
    datetime_object = dateutil.parser.isoparse(datetime_text)

    for chain in root.findall('./DataRoutes/DataRoute'):

        for scantype in chain.findall('ScanInformation/ScanMode'):
            if scantype.text == 'StillScan':

                if chain.get('Description') == 'Originally measured data.':
                    start = chain.findall('ScanInformation/ScaleAxes/ScaleAxisInfo/Start')[0].text
                    #stop = chain.findall('ScanInformation/ScaleAxes/ScaleAxisInfo/Stop')[0].text
                    increment = float(chain.findall('ScanInformation/ScaleAxes/ScaleAxisInfo/Increment')[0].text)
                    #LOG.debug("Start: {}, Stop: {}, Increment: {}".format(start, stop, increment))

                    data = np.array([float(i) for i in chain.findall('Datum')[0].text.split(",")])
                    # Remove all non-intensity values
                    diff = np.append(np.diff(data),0)
                    data = data[diff != 0]
                    #print(data)

                    twoth = np.zeros(len(data))
                    twoth[0] = start
                    for i, elem in enumerate(twoth[:-1]):
                        twoth[i+1] = twoth[i] + increment
                    
                    #print(twoth)
                    #import sys
                    #sys.exit()
                    """
                    print(data)
                    print(twoth)
                    for data in :
                        data = data.text.split(',')
                        data = [float(i) for i in data]
                        print(len(data))
                        twoth.append(float(data[2]))
                        intensity.append(float(data[3]))

                        ## THIS NEEDS TO GET START AND STOP TWOTHETA FROM THE FILE, AND THEN GET ALL THE INTENSITIES IN DATUM, AND GENERATE THE TWOTH POSITIONS FOR EACH INTENSITY
                    """
            else:
                if chain.get('Description') == 'Originally measured data.':
                    for data in chain.findall('Datum'):
                        data = data.text.split(',')
                        print("Else: {}".format(len(data)))
                        twoth.append(float(data[2]))
                        intensity.append(float(data[3]))

    
    xye_t = np.array((np.array(twoth), np.array(data), np.zeros(len(twoth))))
    #print(xye_t)
    return xye_t, datetime_object