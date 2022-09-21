# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 14:25:06 2022
Routine to read & plot CTD .cnv data
@author: James.manning
"""
import glob
import pandas as pd
from dateutil.parser import parse
files=glob.glob('*.cnv')
df=pd.DataFrame()
for k in files:
    with open(k) as f:
        for line in f:
            print(line[2:17])
            if line[2:15]=='NMEA Latitude':
                lat=int(line[18:20])+float(line[21:26])/60.
                print(line[2:15])
                
            elif line[2:16]=='NMEA Longitude':
                lon=int(line[19:22])+float(line[22:28])/60.*-1.
            elif line[2:17]=='NMEA UTC (Time)':
                dtime=parse(line[20:41])
                print(dtime)
                f.close(k)
                continue
        #df=read_csv(k,skiprows=293)
            
                