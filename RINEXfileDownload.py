# -*- coding: utf-8 -*-
"""
Created on Sun Jan 04 14:00:29 2015

@author: Aditya
Note: Download file from SOPAC database RINEX obs and nav. 
"""

import ftplib
import time
import os


initial=os.getcwd()
site='cnvl'
station_list = ['algo','baie','drao','godz','gol2','kuuj','kour','unbj','vald']

def make_alpha_dict():
    alpha_dict = {}
    numa_dict = {}
    alpha_list = ['a', 'b', 'c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    for i in range(0,26):
        alpha_dict[i] = alpha_list[i]
        numa_dict[i] = str(i).zfill(2)
    return alpha_dict, numa_dict

alpha,sigma=make_alpha_dict()

def download_file_to(doy,obs_nav_met):
    day_dir='/home/aditya/Download_RINEX' + os.sep + doy
    if not os.path.exists(day_dir):
        os.mkdir(day_dir)
    if obs_nav_met == 'obs':
        download_file_to= '/home/aditya/Download_RINEX' + os.sep + doy + os.sep + 'obs'
    elif obs_nav_met == 'nav':
        download_file_to= '/home/aditya/Download_RINEX' + os.sep + doy + os.sep + 'nav'
    elif obs_nav_met == 'met':
        download_file_to= '/home/aditya/Download_RINEX' + os.sep + doy + os.sep + 'met'
    if not os.path.exists(download_file_to):
        os.mkdir(download_file_to)
    os.chdir(download_file_to)
    k = os.getcwd()
    print 'The current directory is in download files!'
    print k
    
def download_ref_stations(doy):
    print 'Near Real Time WV Data'
    global station_list
    global alpha,sigma
    if time.gmtime().tm_hour == 0:
        #doy = str(time.gmtime().tm_yday -1).zfill(3)
        real_hour = str(sigma[23])
        hour_alpha = str(alpha[23])
    else:
        #doy = str(time.gmtime().tm_yday).zfill(3)
        real_hour = str(sigma[time.gmtime().tm_hour -1])
        hour_alpha = str(alpha[time.gmtime().tm_hour -1])
    print os.getcwd()
    ftp = ftplib.FTP('garner.ucsd.edu','anonymous','adityanagara@engin.umass.edu')
    print 'logged in'
    base_folder='/pub/nrtdata' + os.sep + str(time.gmtime().tm_year) + os.sep
    ftp.cwd(base_folder)
    dyna_folder= base_folder + doy
    ftp.cwd(dyna_folder)
    temp_dir_list=ftp.nlst()
    print real_hour
    print temp_dir_list
    if real_hour in temp_dir_list:      
        dyna_folder= base_folder + doy + os.sep + real_hour  
        print dyna_folder
        ftp.cwd(dyna_folder)
        file_list=ftp.nlst()
        for stn in station_list:
            dyna_file_name = stn + doy + hour_alpha + '.' + str(time.gmtime().tm_year)[-2:] + 'd.Z'
            dyna_file_name_nav=stn + doy + hour_alpha + '.' + str(time.gmtime().tm_year)[-2:] + 'n.Z'
#            print 'This is what we are going to get'
#            print dyna_file_name
#            print dyna_file_name_nav
            if dyna_file_name in file_list:
                download_file_to(doy,'obs')
                gfile = open(dyna_file_name,'wb')
                ftp.retrbinary('RETR ' + dyna_file_name,gfile.write)
                gfile.close()
                print 'The File >>>>>>>>>>>>>>>>> ' + dyna_file_name + ' was downloaded successfully!'
            if dyna_file_name_nav in file_list:
                download_file_to(doy,'nav')
                gfile = open(dyna_file_name_nav,'wb')
                ftp.retrbinary('RETR ' + dyna_file_name_nav,gfile.write)
                gfile.close()
                print 'The File >>>>>>>>>>>>>>>>> ' + dyna_file_name_nav + ' was downloaded successfully!'
    else:
        print 'The hourly folder at SOPAC have not been updated yet!'
    ftp.close()

download_ref_stations(str(time.gmtime().tm_yday).zfill(3))
