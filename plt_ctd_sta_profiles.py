# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 14:25:06 2022
Routine to read & plot CTD .cnv data
@author: James.manning
modified Sep2022 before posting to github
"""
import glob
import pandas as pd
from dateutil.parser import parse
from matplotlib import pyplot as plt
import numpy as np
import netCDF4
import os,imageio

#FUNCTIONS######
def make_gif(gif_name,png_dir,frame_length = 0.2,end_pause = 4 ):
    '''use images to make the gif
    frame_length: seconds between frames
    end_pause: seconds to stay on last frame
    the format of start_time and end time is string, for example: %Y-%m-%d(YYYY-MM-DD)'''
    
    if not os.path.exists(os.path.dirname(gif_name)):
        os.makedirs(os.path.dirname(gif_name))
    allfile_list = glob.glob(os.path.join(png_dir,'*.png')) # Get all the pngs in the current directory
    file_list=allfile_list
    list.sort(file_list, key=lambda x: x.split('/')[-1].split('t')[0]) # Sort the images by time, this may need to be tweaked for your use case
    images=[]
    # loop through files, join them to image array, and write to GIF called 'wind_turbine_dist.gif'
    for ii in range(0,len(file_list)):       
        file_path = os.path.join(png_dir, file_list[ii])
        if ii==len(file_list)-1:
            for jj in range(0,int(end_pause/frame_length)):
                images.append(imageio.imread(file_path))
        else:
            images.append(imageio.imread(file_path))
    # the duration is the time spent on each image (1/duration is frame rate)
    imageio.mimsave(gif_name, images,'GIF',duration=frame_length)


###MAINCODE""
files=glob.glob('HB2204- Spring EcoMon/*.cnv')
mode='just_station_plot'# or 'gif'
#files=['HB2204- Spring EcoMon/sbe062.cnv']
df=pd.DataFrame()
for k in files:
    with open(k) as f:
        for line in f:
            #print(line[2:17])
            if line[2:15]=='NMEA Latitude':
                lat=int(line[18:20])+float(line[21:26])/60.
                #print(line[2:15])    
            elif line[2:16]=='NMEA Longitude':
                lon=-1*int(line[19:22])-float(line[22:28])/60.
            elif line[2:17]=='NMEA UTC (Time)':
                dtime=parse(line[20:41])
                print(dtime)
        sta=k[-10:-4]
        f.close()
        if k[-10:-7]=='sbe':
            skip=105
        else:
            skip=294# ctd file case
        df1=pd.read_csv(k,skiprows=skip,delim_whitespace=True,names=['depth','temp','c','salt','scan','flag'])
        df1['lat']=lat;df1['lon']=lon;df1['dtime']=dtime;df1['sta']=sta
    df=pd.concat([df,df1])

#df['datetime'] = pd.to_datetime(df['dtime'])
#df=df.sort_values(['datetime','depth'],axis=0)

    
# loading coastlines & bathy lines
#coastfilename='c:/users/james.manning/Downloads/basemaps/capecod_coastline_detail.csv'
coastfilename='c:/users/james.manning/Downloads/basemaps/us_coast.dat'
dfc=pd.read_csv(coastfilename,delim_whitespace=True,names=['lon','lat'])
bathyfile='c:/users/james.manning/Downloads/basemaps/necs_60m.bty'
dfb=pd.read_csv(bathyfile,delim_whitespace=True,names=['lon','lat','d1','d2'])
dfb=dfb[dfb.lat!=0]
dfb['lon']=dfb['lon']*-1
url='http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3'
nc = netCDF4.Dataset(url).variables
lats = nc['lat'][:]
lons = nc['lon'][:]
depth = nc['h'][:]  # depth

dfs=df.drop_duplicates(subset='sta')# cast positions
stas=dfs.sta.values
dts=dfs.dtime
#stas=stas[0:24]
count=0
for i in dts:
    if mode=='just_station_plot':
        fig, ax1 = plt.subplots(1, 1) 
    else:
        fig, (ax1, ax2) = plt.subplots(1, 2)
    #plot coast
    ax1.plot(dfc.lon,dfc.lat,'k.',markersize=1)

    # plot bathy
    ax1.tricontour(lons,lats,depth,[200.],colors='purple')
    ax1.plot(dfb.lon,dfb.lat,'g.',markersize=1)
    ax1.text(-71.,39.,'60m isobath',color='g')
    ax1.text(-71.,38.5,'200m isobath',color='purple')

    # plot stations
    ax1.plot(dfs.lon,dfs.lat,'r.',markersize=12)
    df1=df[df['dtime']==i]
    ax1.plot(df1.lon[0],df1.lat[0],'k.',markersize=30)
    ax1.set_title('R/V Henry Bigelow June 2022',fontsize=12)
    ax1.set_ylim(min(dfs.lat)-.1,max(dfs.lat)+.1)
    ax1.set_xlim(min(dfs.lon)-.1,max(dfs.lon)+.1)
    ax1.text(-71.,38.,df1.sta[0],color='k')
    ax1.text(-74.5,44.,str(i)[:-3])
    if mode=='just_station_plot':
        for j in range(len(dfs)):
            ax1.text(dfs.lon.values[j],dfs.lat.values[j],dfs.sta.values[j],color='k',verticalalignment='center',horizontalalignment='center',fontsize=6)
        break
    box = ax1.get_position()
    box.x0 = box.x0 - 0.05
    box.x1 = box.x1 - 0.05
    ax1.set_position(box)
    # plot profiles

    df1=df1[df1['depth']>2.0]
    #id=np.where(np.diff(df1['depth'])<0)
    id=np.where(df1['depth']==max(df1['depth']))[0][0]
    df1=df1[0:id]#downcast
    #ax2.plot(df1['temp'].values[id[0]],df1['depth'].values[id[0]]*-1.,'r-')
    ax2.plot(df1['temp'].values,df1['depth'].values*-1.,'r-')
    ax2.set_ylim(-100.,0)
    ax2.set_xlabel(df1['sta'].values[0]+' temp (degC)',color='r')
    ax2.set_ylabel('depth (meters)')
    

    ax3 = ax2.twiny()
    ax3.plot(df1['salt'].values,df1['depth'].values*-1.,'c-')
    ax3.set_xlim(31.,36.)
    ax3.set_title('salinity (PSU)',color='c')

    count=count+1
    #fig.savefig('plots/'+"{:03d}".format(count)+'.png')
    ib=str(i).replace(' ','_')
    ib=ib.replace(':','')
    fig.savefig('plots/'+ib+'.png')
    plt.close(fig)
if mode=='gif':
    make_gif('c:/users/james.manning/Downloads/ctd/plots/HB2204.gif','c:/users/james.manning/Downloads/ctd/plots/',frame_length=2.0)
else:
    fig.savefig('station_plot.png')


            
                