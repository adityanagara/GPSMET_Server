# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 12:57:47 2014

@author: Aditya
Note: Plot near real time water vapor and publish online.
emmy9.casa.umass.edu/gpsmet
"""

import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot
import os
import time

def make_x_axis():
    file_day=time.gmtime().tm_yday
    if time.gmtime().tm_hour == 0:
        file_day=time.gmtime().tm_yday - 1
    file_name='met_cnvl.' + str(time.gmtime().tm_year)[-2:] + str(file_day).zfill(3)
    folder_name='/home/aditya/UMASS/20141028/TEST/2014/WV'
    file_to_get=folder_name + os.sep + file_name
    read_file=open(file_to_get)
    lines=read_file.readlines()
    last=len(lines)
    WV_Values=[]
    time_list=[]
    axis_time=[]
    axis_time_dict={}
    for x in range(4,last):
        WV_Values.append(lines[x][50:55])
        time_list.append(lines[x][10:18])
    #print time_list
    time_list_len=len(WV_Values)
    #print time_list_len
    for i in range(0,time_list_len):
        axis_time.append(i*5)
    hour_axis_time=[]
    for i in range(0,288):
        temp=float(i)/12.0
        hour_axis_time.append(temp)
    time_list.pop()
    #print time_list
    #print len(hour_axis_time)
    #print len(time_list)
    for i in range(0,len(time_list)):
        #print i
        axis_time_dict[time_list[i]] = hour_axis_time[i]
    #print len(axis_time_dict)
    #print axis_time_dict
    current_time=str(time.gmtime().tm_hour) + '  0  0'
    if time.gmtime().tm_hour == 0:
        current_time=str(23) + '  0  0'
    #print current_time
    dyna_axis=[]
    dyna_WV=[]
    for i in range(0,len(axis_time_dict)):
	#print time_list[i]
        if current_time == time_list[i].strip():
            time_index=i
            dyna_axis=hour_axis_time[0:time_index]
            dyna_WV=WV_Values[0:time_index]
            #print time_index
    print len(dyna_axis)
    print len(dyna_WV)
    pyplot.plot(dyna_axis,dyna_WV)
    axes = pyplot.gca()
    axes.set_xlabel('Hour (UTC time)')
    axes.set_ylabel('IPW (mm)')
    file_name_day=str(time.gmtime().tm_year) + str(time.gmtime().tm_mon) + str(time.gmtime().tm_mday).zfill(2)
    if time.gmtime().tm_hour == 0:
        file_name_day=str(time.gmtime().tm_year) + str(time.gmtime().tm_mon) + str(time.gmtime().tm_mday).zfill(2)
    pyplot.title('Integrated Precipitable Water ' + file_name_day)
    main_page= '/var/www/html/gpsmet/2015'
    if not os.path.exists(main_page + os.sep + str(time.gmtime().tm_yday).zfill(3)):
        os.makedirs(main_page + os.sep + str(time.gmtime().tm_yday).zfill(3))
 #save_plot='/home/aditya/UMASS/20140917/TEST/2014/WV_Plots' + os.sep + 'cnvl' + file_name_day + '.png'
    save_plot=main_page + os.sep + str(file_day).zfill(3) + os.sep + 'cnvl' + file_name_day + str(time.gmtime().tm_hour).zfill(2) + '.png'
    print save_plot
    pyplot.savefig(save_plot)
   
make_x_axis()
