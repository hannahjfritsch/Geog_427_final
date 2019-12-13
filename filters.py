"""Filters
Hannah Fritsch, December 2019
Demp project

filters and functions for cleaning the time series data"""

#updated version from https://github.com/danda-ecological-monitoring/Data-Cleaning
#update needs to be pushed

import pandas as pd
from scipy import signal


def median_spike_filter(df, column, window, gap):
    """ Checks to see if each value in a column is within the gap distance
    fromm the median of the window
    if it is not, replace with empty vvalue
    no return, updates the column

    nop"""
    try:
        raw = df[column].to_numpy()
        smooth = signal.medfilt(raw, window)
        dif = abs(raw-smooth)
        trim = int(window/2)

        #print(raw,"\n",smooth,"\n",dif)

        for i in range(0,len(raw)):
            if (i < trim) or (i >= len(raw)-trim):
                df[column].iloc[i]= ""
            elif dif[i] > gap:
                df[column].iloc[i]= ""

        #print(raw,"\n",smooth,"\n",dif,"\n" )
        #print(df[column])
        #print(df.columns.get_loc(column))
        return df
    except Exception as e:
        print(e)


