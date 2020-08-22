#!/usr/bin/python3
# -*- coding: utf-8 -*-
########################################
###export LC_ALL="en_US.UTF-8" - set####
########################################

import subprocess
from subprocess import Popen, PIPE
import sys, os
import time
from collections import OrderedDict
import datetime
import argparse

########################################
############### Versions ###############
########################################

changeloglst = {}
changeloglst[0.1] = "First release"
changeloglst[0.2] = "Rewrite to one file lastsong.py"
changeloglst[0.3] = "Adding some features (checking files, progressbar, arguments)"

########################################
############## Split info ##############
########################################

def gen_simple(data):
    parsed_m3u  = OrderedDict()
    for l in data:
        title = l.split('/')[-1]
        uri = l
        parsed_m3u[title] = uri
    return parsed_m3u

########################################
######### Create playlist name #########
########################################

def week(i):
 switcher={
  0:'1-Monday',
  1:'2-Tuesday',
  2:'3-Wednesday',
  3:'4-Thursday',
  4:'5-Friday',
  5:'6-Saturday',
  6:'7-Sunday',
 }
 return switcher.get(i,"RecentlyAdded")

########################################
############# Progressbar ##############
########################################

def update_progress(progress):
    barLength = 30
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), int(progress*100), status)
    sys.stdout.write(text)
    sys.stdout.flush()
    
########################################
########### Argument parser ############
########################################

parser = argparse.ArgumentParser()

parser.add_argument('-s', '--source-file', default='/var/log/mpd.log',
		    action='store', dest='sfile',
                    help='Source file')

parser.add_argument('-p', '--playlist-dir', default='/data/playlist/',
		    action='store', dest='pldir',
                    help='Destination directory')

parser.add_argument('-i', '--ignore-timer', 
		    action='store_true', default=False,
                    dest='ignoretimer',
                    help='Ignore timer for waiting after mpc update')

parser.add_argument('-o', '--one-playlist', 
		    action='store_true', default=False,
                    dest='oneplst',
                    help='Write only one playlist named RecentlyAdded')

parser.add_argument('-c', '--changelog', 
		    action='store_true',  default=False,
                    dest='changelog',
                    help='Show changelog')

parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.3')

results = parser.parse_args()

########################################
############ Define paths ##############
########################################

wn = datetime.datetime.today().weekday()

if not os.path.isfile(results.sfile):
 print('File {} not found!'.format(results.sfile))
 sys.exit(0)

if not os.path.isdir(results.pldir):
 print('Folder {} not found!'.format(results.pldir))
 sys.exit(0)

if results.changelog: 
 for key in changeloglst:
  print(key,"\t",changeloglst[key])
 sys.exit(0)

########################################
############## Update MPC ##############
########################################

output=subprocess.call(["mpc","update"])
if not results.ignoretimer:
 print("Waiting 120 sec for update mpd.")
 for i in range(101):
  time.sleep(120/100)
  update_progress(i/100.0)
 print ("")

########################################
############ Parse mpd.log #############
########################################

data = []
with open(results.sfile, encoding='utf-8', mode='r') as myfile:
 for myline in myfile:
  if myline.find("added") != -1:
   if myline.find(datetime.datetime.today().strftime("%h %d")) != -1:
    data.append(myline.split("added ",1)[1])

########################################
########## Write volumio file ##########
########################################

if results.oneplst:
 plstname=results.pldir +"RecentlyAdded"
else:
 plstname=results.pldir + week(wn)

o = open(plstname, encoding='utf-8', mode="w")
o.write('[')

data = [l.strip() for l in data]    
data = list(filter(None, data))
data = gen_simple(data)

output = []

for key in data:
 if '-' in key and key.count('-') == 1:
  artist = key.split('-')[0].strip()
  title = key.split('-')[1].strip()
  title_temp = '.'.join(title.split('.')[:-1])
  if not title_temp == '':
   title = title_temp
  output.append('{' + '"service":"mpd","title":"' + title + '","artist":"' + artist + '","uri":"' + data[key] + '"}')
 else:
  title_temp = '.'.join(key.split('.')[:-1])
  if not title_temp == '':
   title = title_temp
  output.append('{' + '"service":"mpd","title":"' + title + '","uri":"' + data[key] + '"}')
o.write(','.join(output))
o.write(']')
o.close()
print("Successfully added to " + plstname)
