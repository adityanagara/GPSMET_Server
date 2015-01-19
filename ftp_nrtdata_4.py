# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 12:30:28 2014

@author: Aditya

Note: Downloades all files from NOAA, SOPAC data bases, orbit files nav files etc. and from
      remote sensing node cnvl, onto server at UMASS. Automates sh_gamit for near realtime
      tropospheric products. Runs with crontab. 
"""

import ftplib
import time
import os
import subprocess
import shutil
import math
import RINEXfileDownload

initial=os.getcwd()
site='cnvl'
station_list = ['algo','baie','drao','godz','gol2','kuuj','kour','unbj','vald']
def initialize_environ():
    GMT = ':/usr/lib/gmt/bin'
    GAMIT1 = ':/root/gg/gamit/bin'
    GAMIT2=':/root/gg/kf/bin'
    GAMIT3=':/root/gg/com'
    os.environ['PATH']  = os.environ['PATH']  + GMT + GAMIT1 + GAMIT2 + GAMIT3
    os.environ['HELP_DIR'] = '/usr/local/gamit/help/'
    os.environ['INSTITUTE'] = 'UMA'

def make_alpha_dict():
    alpha_dict = {}
    numa_dict = {}
    alpha_list = ['a', 'b', 'c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    for i in range(0,26):
        alpha_dict[i] = alpha_list[i]
        numa_dict[i] = str(i).zfill(2)
    return alpha_dict, numa_dict

'''
    Modify the cnvl rinex header file
'''
#/home/aditya/UMASS/20140812/TEST/2014
def change_cnvl_header(doy):
    global site
    cnvl='/home/aditya/UMASS/20141028/TEST/2014/rinex' +os.sep + site + doy + '0.' + str(time.gmtime().tm_year)[-2:] + 'o'
    k=open(cnvl,'r')
    p=k.readlines()
    k.close()
    k=open(cnvl,'w')
    replace_1='     2.10           OBSERVATION DATA    GPS                 RINEX VERSION / TYPE\n'
    replace_2='UTA                                                         MARKER NAME         \n'    
    replace_3='Aditya N            UMASS                                   OBSERVER / AGENCY   \n'    
    replace_5='200021              HEMA42          NONE                    ANT # / TYPE\n'
    replace_6='1862964             HEM P320 ECLIPSE II MFA_1.2Qe           REC # / TYPE / VERS \n'    
    p[0]=replace_1
    p[2]=replace_2
    p[3]=replace_3
    p[4]=replace_6
    p[5]=replace_5
    k.writelines(p)
    k.close()

'''
    Note: Remember to 0 pad doy
'''
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

alpha,sigma=make_alpha_dict()


'''
    At hour 1 you need to download 2 files. 
'''
def download_from_node():
    global alpha,sigma,site,initial
    if time.gmtime().tm_hour == 0:
        doy = str(time.gmtime().tm_yday -1).zfill(3)
        file_to_get=site + doy + alpha[24] + '.' +  str(time.gmtime().tm_year)[-2:] + 'o'
        file_to_get_2=site + str(time.gmtime().tm_yday) + alpha[0] + '.' + str(time.gmtime().tm_year)[-2:] + 'o'
        file_to_get_2_nav=site + str(time.gmtime().tm_yday) + alpha[0] + '.' + str(time.gmtime().tm_year)[-2:] + 'n'
        file_to_get_nav=site + doy + alpha[24] + '.' + str(time.gmtime().tm_year)[-2:]+'n'
        file_to_get_met=site + doy + '0.' + str(time.gmtime().tm_year)[-2:]+ 'm'
    else:    
        doy = str(time.gmtime().tm_yday).zfill(3)
        file_to_get=site + doy + alpha[time.gmtime().tm_hour] + '.' + str(time.gmtime().tm_year)[-2:] + 'o'
        file_to_get_nav=site + doy + alpha[time.gmtime().tm_hour] + '.' + str(time.gmtime().tm_year)[-2:] + 'n'
        file_to_get_met=site + doy + '0.' + str(time.gmtime().tm_year)[-2:] + 'm'
    ip_adr='0.0.0.0' # Blocked due to security reasons, it would be bad if you log onto my node.
    ftp2=ftplib.FTP(ip_adr,'username','password')
    ftp2.set_pasv(False)
    dyna_folder_2 = 'RINEX_files' + os.sep + str(time.gmtime().tm_year) + os.sep + doy 
    ftp2.cwd(dyna_folder_2)
    file_list=ftp2.nlst()
    print 'logged in to node!'
    download_file_to(doy,'obs')
    if file_to_get in file_list:
        nfile= open(file_to_get,'wb')
        print file_to_get
        ftp2.retrbinary('RETR '+file_to_get,nfile.write)
        nfile.close()
        print 'We got the file >>>>>> ' + file_to_get
    else:
        print file_to_get + ' Not found!'
    download_file_to(doy,'nav')
    if file_to_get_nav in file_list:
        nfile_nav=open(file_to_get_nav,'wb')
        #print '>>>>>>>>>>>>>>>>>>>>>>>>' + file_to_get_nav
        ftp2.retrbinary('RETR '+file_to_get_nav,nfile_nav.write)
        nfile_nav.close()
        print 'we got the file >>>>>>>> ' + file_to_get_nav
    else:
        print file_to_get_nav + 'Not found!'
    download_file_to(doy,'met')
    if file_to_get_met in file_list:
        nfile_met=open(file_to_get_met,'wb')
        ftp2.retrbinary('RETR '+file_to_get_met,nfile_met.write)
        nfile_met.close()
        print 'we got the file >>>>>>>> ' + file_to_get_met
    else:
        print file_to_get_met + ' Not found!'
    ftp2.close()
    if time.gmtime().tm_hour == 0:
        ftp2=ftplib.FTP(ip_adr,'GPSMET1','aditya')
        ftp2.set_pasv(False)
        print 'logged onto node again'
        os.chdir(initial)
        dyna_folder_once= 'RINEX_files' + os.sep + str(time.gmtime().tm_year) + os.sep  + str(time.gmtime().tm_yday)  
        ftp2.cwd(dyna_folder_once) 
        file_list=ftp2.nlst()
        download_file_to(str(time.gmtime().tm_yday),'obs')                
        if file_to_get_2 in file_list:
            nfile2=open(file_to_get_2,'wb')
            ftp2.retrbinary('RETR '+file_to_get_2,nfile2.write)
            nfile2.close()
            print 'We got the file >>>>>>>> ' + file_to_get_2
        else:
            print file_to_get_2 + 'Not found!'
        download_file_to(str(time.gmtime().tm_yday),'nav')
        if file_to_get_2_nav in file_list:
            nfile2_nav=open(file_to_get_2_nav,'wb')
            ftp2.retrbinary('RETR '+file_to_get_2_nav,nfile2_nav.write)
            nfile2_nav.close()
            print 'We got the file >>>>>>>>> ' + file_to_get_2_nav
        else:
            print file_to_get_2_nav + ' Not found!'
    print 'We got the file from the node'
    ftp2.close()

'''
    Uncompress the files.
'''

def extract_files():
    global station_list,alpha,sigma,site,initial
    if time.gmtime().tm_hour == 0:
        doy = str(time.gmtime().tm_yday -1).zfill(3)
        hour_alpha = str(alpha[23])
    else:
        doy = str(time.gmtime().tm_yday).zfill(3)
        hour_alpha = str(alpha[time.gmtime().tm_hour -1])
    files_to_obs='/home/aditya/Download_RINEX' + os.sep + doy + os.sep + 'obs'
    files_to_nav='/home/aditya/Download_RINEX' + os.sep + doy + os.sep + 'nav'
    for stn in station_list:
        dyna_file_name_c = stn + doy + hour_alpha +'.' + str(time.gmtime().tm_year)[-2:] + 'd.Z'
        #dyna_file_name_n = stn + doy + hour_alpha + '.14n.Z'
        dyna_file_name_h= stn + doy + hour_alpha + '.' + str(time.gmtime().tm_year)[-2:] + 'd'
        #dyna_file_name_hn=stn + doy + hour_alpha + '.14n'
        if dyna_file_name_c in os.listdir(files_to_obs):
            print '#################' + stn
            print 'Uncompress is going to start'
            download_file_to(doy,'obs')
            subprocess.call(['uncompress','-f',dyna_file_name_c])
            subprocess.call(['crx2rnx',dyna_file_name_h,'-f'])
            os.remove(dyna_file_name_h)
            download_file_to(doy,'nav')
            for n_file in os.listdir(files_to_nav):
                if n_file[-3:] == '.gz' or n_file[-2:] == '.Z':
                    print 'uncompressing -->' + n_file
                    subprocess.call(['uncompress','-f',n_file])

'''
    Merge Rinex files. 
'''
def merge_rinex_files():
    global station_list
    if time.gmtime().tm_hour == 0:
        doy = str(time.gmtime().tm_yday -1).zfill(3)
    else:
        doy = str(time.gmtime().tm_yday).zfill(3)
    files_obs='/home/aditya/Download_RINEX' + os.sep + doy + os.sep + 'obs'
    file_nav='/home/aditya/Download_RINEX' + os.sep + doy + os.sep + 'nav'
    station_list.append(site)
    file_path_obs='/home/aditya/UMASS/20141028/TEST/2014/rinex/'
    file_path_nav='/home/aditya/UMASS/20141028/TEST/2014/brdc/'
    for stn in station_list:
        print '<<<<<<<<Merging site>>>>>>>>' + stn
        download_file_to(doy,'obs')
        k = os.getcwd()
        print 'The current directory is:'
        print k
        subprocess.call(['sh_merge_rinex','-site',stn,'-year',str(time.gmtime().tm_year),'-days',doy])        
        file_path_from=files_obs + os.sep + stn + doy + '0.' + str(time.gmtime().tm_year)[-2:] + 'o'        
        subprocess.call(['mv',file_path_from,file_path_obs])        
    download_file_to(doy,'nav')        
    subprocess.call(['sh_merge_nav','-t',str(time.gmtime().tm_year),doy])
    file_path_from_nav=file_nav + os.sep + 'brdc' + doy + '0.' + str(time.gmtime().tm_year)[-2:] + 'n.gz'
    brdc_path='/home/aditya/UMASS/20141028/TEST/2014/brdc' + os.sep + 'brdc' + doy + '0.' + str(time.gmtime().tm_year)[-2:] + 'n'
    if os.path.exists(brdc_path):
        subprocess.call(['rm',brdc_path])
        print 'existing brdc removed'
    subprocess.call(['mv',file_path_from_nav,file_path_nav])
    os.chdir(file_path_nav)
    brdc_file='brdc' + doy + '0.' + str(time.gmtime().tm_year)[-2:] + 'n.gz'
    subprocess.call(['uncompress','-f',brdc_file])
            
'''
    Compute the GPS week and day to retrieve sp3 file(Hourly updayed sp3 file from SOPAC archive )

'''
def compute_gps_week():
    secsInWeek = 604800 
    secsInDay = 86400 
    gpsEpoch = (1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)
    epochTuple= gpsEpoch + (-1,-1,0) 
    t0=time.mktime(epochTuple)
    time_tuple= (time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday, time.gmtime().tm_hour, time.gmtime().tm_min,time.gmtime().tm_sec)
    time_tuple = time_tuple + (-1,-1,0)
    secFract = time.gmtime().tm_sec % 1
    t=time.mktime(time_tuple)
    t = t+14
    tdiff = t-t0
    gpsWeek = int(math.floor(tdiff/secsInWeek))
    gpsSOW = (tdiff % secsInWeek)  + secFract
    gpsDay = int(math.floor(gpsSOW/secsInDay))
    return (gpsWeek,gpsDay)

'''
    Download the hourly sp3 file
'''
def download_sp3_file(doy):
    gps_week_day=compute_gps_week()
    sp3_files=[]
    ftp3=ftplib.FTP('garner.ucsd.edu','anonymous','root@GPSMET.ecs.umass.edu')
    go_to_base='/products' + os.sep
    ftp3.cwd(go_to_base)
    go_to=go_to_base + str(gps_week_day[0])
    print go_to
    ftp3.cwd(go_to)
    k=ftp3.nlst()
    for sp3_file in k:
        if sp3_file[:8] == 'siu' + str(gps_week_day[0]) + str(gps_week_day[1]):
            sp3_files.append(sp3_file)
    print gps_week_day
    file_to_get_sp3=sp3_files[len(sp3_files) - 1]
    #initial=os.getcwd()
    os.chdir('/home/aditya/UMASS/20141028/TEST/2014/igs')
    current=os.getcwd()
    nfile_sp3=open(file_to_get_sp3,'wb')
    ftp3.retrbinary('RETR '+file_to_get_sp3,nfile_sp3.write)
    nfile_sp3.close()
    print 'we got the file >>>>>>>>> ' + file_to_get_sp3
    subprocess.call(['uncompress','-f',file_to_get_sp3])
    #sh_sp3fit -f igr18022.sp3 -o igsr -u -d 2014 203  -m 0.200
    subprocess.call(['sh_sp3fit','-f',file_to_get_sp3.strip('.Z'),'-o','igsu','-u','-d',str(time.gmtime().tm_year),doy,'-m','0.200'])     
    file_to_move=current + os.sep +'gigsu5.' + doy
    dest='/home/aditya/UMASS/20141028/TEST/2014/gfiles'
    subprocess.call(['mv',file_to_move,dest])
    ftp3.close()

def move_old_data(doy):
    initial=os.getcwd()
    run_dir='/home/aditya/UMASS/20141028/TEST/2014'
    os.chdir(run_dir)
    into_folder='/home/aditya/UMASS/20141028/TEST/2014/DAY_Bkp' + os.sep
    subprocess.call(['mv','-f',run_dir + os.sep + doy,into_folder])
    print doy + 'Has been moved out'
    os.chdir(initial)

def clear_rinex_dir():
    file_path='/home/aditya/UMASS/20141028/TEST/2014/rinex'
    uta1_bkp_dir='/home/aditya/UMASS/20141028/TEST/2014/UTA1_RINEX_BKP'
    k=os.listdir(file_path)
    uta1_list=[]
    if not k:
        print 'No files exist, no clearing necessary'
    else:
        for file in k:
            if file[:4] == site:
                uta1_list.append(file_path + os.sep + file)
                shutil.move(file_path + os.sep + file,uta1_bkp_dir + os.sep + file)
            else:
        #os.remove(os.path.abspath(file))
                print file_path + os.sep + file
                os.remove(file_path + os.sep + file)

def run_GAMIT(doy):
    initial=os.getcwd()
    run_dir='/home/aditya/UMASS/20141028/TEST/2014'
    #-expt scal -d 2014 223 -pres ELEV -orbit IGSU -copt k p -dopts x c ao -noftp 
    os.chdir(run_dir)
    subprocess.call(['sh_gamit','-expt','scal','-d',str(time.gmtime().tm_year),doy,'-pres','ELEV','-orbit','IGSU','-copt','k','p','-dopts','x','c','ao','-noftp'])
    os.chdir(initial)

def run_METUTIL(doy):
    initial =os.getcwd()
    o_file='/home/aditya/UMASS/20141028/TEST/2014' + os.sep + doy + os.sep + 'oscala.' + doy
    met_file='/home/aditya/Download_RINEX' + os.sep + doy + os.sep  + 'met' + os.sep + site + doy + '0.' + str(time.gmtime().tm_year)[-2:] + 'm'   
    dest_WV='/home/aditya/UMASS/20141028/TEST/2014/WV/' 
    os.chdir(dest_WV)
    if os.path.exists(o_file):
        subprocess.call(['cp','-f',o_file,dest_WV])
        subprocess.call(['cp','-f',met_file,dest_WV])
    subprocess.call(['sh_metutil','-f',os.path.basename(o_file),'-m',os.path.basename(met_file),'-i','300'])
    os.chdir(initial)

#Michael Jacques <navmik91@massmed.org>
def mail_data(doy):
    results='/home/aditya/UMASS/20141028/TEST/2014/WV' + os.sep + 'met_cnvl.' + str(time.gmtime().tm_year)[-2:] + doy
    mail_to_1="mail -s 'near real time water vapor data' aditya_n09@yahoo.co.in < " +  results
    mail_to_2="mail -s 'near real time water vapor data' navmik91@massmed.org < " +  results
    os.system(mail_to_1)
    os.system(mail_to_2)
        


if time.gmtime().tm_hour == 0:
    doy = str(time.gmtime().tm_yday -1).zfill(3)
else:
    doy = str(time.gmtime().tm_yday).zfill(3)

clear_rinex_dir()
initialize_environ()
RINEXfileDownload.download_ref_stations(doy)
#download_ref_stations()

download_from_node()
extract_files()
merge_rinex_files()
change_cnvl_header(doy)
if not time.gmtime().tm_hour == 0:
    download_sp3_file(doy)
move_old_data(doy)
run_GAMIT(doy)
run_METUTIL(doy)
mail_data(doy)

os.chdir(initial)
print 'done'
