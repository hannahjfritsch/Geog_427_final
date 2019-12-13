#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Hannah Fritsch
#
# Created:     20/11/2019
# Copyright:   (c) Hannah Fritsch 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
""" Reformats data from purple air sensor downloads to a joint csv with the
spatial data and sensor names as columns

currently has too much hardcoding"""


import os
import regex
import pandas as p
import filters

#constants
data_path = r"E:\GEO427\Project\Portland_Air"
out_file = "filter_first_week.csv"

#column variables
merge_key = "created_at"
sensor_key = "Sensor"

#regex strings
#general file name
purple =".+[(].+[)]\s[(].+[)](\s\S+){4}[.]csv"
#file for component A
purpleA = ".+\s[(].*side[)]\s[(].+[)](\s\S+){4}[.]csv"
#file for component B
purpleB = ".+\sB\s[(]undefined[)]\s[(].+[)](\s\S+){4}[.]csv"
primary = "[\D|\d]+([(].+[)]\s){2,2}Primary"
secondary ="[\D|\d]+([(].+[)]\s){2,2}Secondary"

def main():
    #set directory and pull a file list
    os.chdir(data_path)
    all_files = os.listdir(data_path)

    site_set = set()

    #select channel a files to pull site names
    #update site_set
    for file in all_files:
        if is_Purple(file) and not(is_B(file)):
            name = file.split(" (")[0]
            site_set.add(name)

    #loop over the site set
    full_file = None
    for site in site_set:
        site_file = reshape_Location(site,all_files)
        if not(site_file is None):
            filters.median_spike_filter(site_file, 'PM2.5_CF1_ug/m3_x',5,30)
            site_file=site_file.head(1400)
            if full_file is None:
                full_file = site_file
            else:
                full_file = full_file.append(site_file)

    #output file if possible
    if not(full_file is None):
        full_file.to_csv(out_file)

def reshape_Location(name,file_list):
    """ Takes a site name, and a list of files
    returns the merged files with column and name
    returns None if files are empty
    or the sensor is indoors"""
    #loop over site_set and get the matching names
    prime = get_Primary(name, file_list)
    #identify a and b
    #assume no duplicates
    a =exp_Matches(purpleA, prime)[0]
    b = exp_Matches(purpleB, prime)[0]
    #read the open the files
    dfA =p.read_csv(a)
    dfB = p.read_csv(b)
    is_out = is_Outdoor(a)
    #check df lengths - kill now if no data
    if max(dfA.size,dfB.size)<1:
        return None
    elif not(is_out):
        return None
    #pull the coordinates
    lat,long = get_Coord(a)
    #merge dfA and dfB based on the time column
    merged = dfA.merge(dfB,"outer",merge_key)
    #add the columns
    merged[sensor_key] = name
    merged["Latitude"] = lat
    merged["Longitude"]= long

    return merged

def get_Coord(file):
    """ takes a file, and returns a tuple of
    latitude and longitude"""
    sub = file.split("(")[2]
    sub = sub.split(")")[0]
    sub = sub.split()
    lat = sub[0]
    long = sub[1]
    return (lat,long)


def is_Outdoor(file):
    """ takes an "A" file name from a sensor, and
    determines whether or not the sensor is outdoor.
    Returns boolean - true if outdoor
    defaults to false in case of error"""
    loc = False
    sub = file.split("(")[1]
    sub = sub.split(")")[0]
    if sub == "outside":
        loc = True
    return loc


def is_Purple(file_name):
    """ A function that takes a file name, and checks if it follows the naming
    conventions for tthe purple air sensor
    returns a boolean
    """
    return bool(regex.fullmatch(purple, file_name))

def is_B(file_name):
    """ A function that takes a file name, and checks if it follows the naming
    conventions for tthe purple air sensor b
    returns a boolean
    """
    return bool(regex.fullmatch(purpleB, file_name))

def exp_Matches (regx, file_list):
    """ Takes a regular expression and a list of strings
    returns a subset list of strings that match the expression"""
    subset = []
    for file in file_list:
        if regex.match(regx,file):
            subset.append(file)
    return subset

def get_Primary (name, files):
    """ Given the cleaned site name, and a list of files
    this returns a list that contains
    the primary files for the sensor."""
    subset = exp_Matches (name, files)
    #verify correct file type
    subset = exp_Matches(purple,subset)
    #further subset to primary
    subset = exp_Matches(primary,subset)
    return subset



if __name__ == '__main__':
    main()
