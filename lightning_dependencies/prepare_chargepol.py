##
# Script to create a list containing all Chargepol.csv data.
# Author : David Rodriguez Sanchez
# Date   : May 17 2023
# Desc   : Using a converted .csv file from a .hdf5 chargepol file, the script will create a histogram.
#
# Dependencies : seaborn, numpy, matplotlib, Python 3.6+
# Usage :: python3 prepare_data.py <path_to_charepol_csv_file>
##

from os import path
import csv

def verify_data(filepath) -> bool:
    with open(filepath, 'r') as chargepol_file:
        chargepol_file.readline()
        header = chargepol_file.readline()
        if "longitude" not in header:
            return False
    return True



def get_data(filepath):
    """Creates a custom data frame of the charge pol data."""
    if not (path.exists(filepath) and filepath[-4:] == '.csv'):
        exit("Error: file must be a .csv file.")

    if not verify_data(filepath):
        exit("Error: please used the forked version of chargepol")

    time = list()
    chargeEvent = list()
    longLat = list()

    with open(filepath, 'r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if(row[0] != "pos") and (row[0] != "neg") : continue
            time.append(float(row[1]))
            chargeEvent.append([row[0], float(row[2]), float(row[3])])
            longLat.append([row[-2], row[-3]])

    chargepol = { "Timestamp" : time,    # Time of event
                  "Charge": chargeEvent, # Type of charge, length and starting altitude
                  "Location": longLat    # Longitude and altitude of charge
                }
    return chargepol