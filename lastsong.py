#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
from subprocess import Popen, PIPE
import sys, os
import time
from collections import OrderedDict
import datetime
import argparse
import urllib.request

########################################
############### Versions ###############
########################################

changeloglst = {}
changeloglst[0.1] = 'First release'
changeloglst[0.2] = 'Rewrite to one file lastsong.py'
changeloglst[0.3] = 'Adding some features (checking files, progressbar, arguments)'
changeloglst[0.4] = 'Change parsing info of track'

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
 return switcher.get(i,'RecentlyAdded')

########################################
############# Progressbar ##############
########################################

def update_progress(progress):
    barLength = 30
    status = ''
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = 'error: progress var must be float\r\n'
    if progress < 0:
        progress = 0
        status = 'Halt...\r\n'
    if progress >= 1:
        progress = 1
        status = 'Done...\r\n'
    block = int(round(barLength*progress))
    text = '\rPercent: [{0}] {1}% {2}'.format( '#'*block + '-'*(barLength-block), int(progress*100), status)
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

parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.4')

results = parser.parse_args()

########################################
############ Define paths ##############
########################################

wn = datetime.datetime.today().weekday()

if not os.path.isfile(results.sfile):
 print('File {} not found!'.format(results.sfile))
 sys.exit(0)

if results.pldir[-1:]!='/':
  results.pldir+= '/'

if not os.path.isdir(results.pldir):
 print('Folder {} not found!'.format(results.pldir))
 sys.exit(0)

if results.changelog:
 for key in changeloglst:
  print(key,'\t',changeloglst[key])
 sys.exit(0)

########################################
############## Update MPC ##############
########################################

output=subprocess.call(['mpc','update'])
if not results.ignoretimer:
 print('Waiting 120 sec for update mpd.')
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
  if myline.find('added') != -1:
   if myline.find(datetime.datetime.today().strftime('%h %d')) != -1:
    data.append(myline.split('added ',1)[1])

########################################
########## Write volumio file ##########
########################################

if results.oneplst:
 plstname=results.pldir +'RecentlyAdded'
else:
 plstname=results.pldir + week(wn)

o = open(plstname, encoding='utf-8', mode='w')
o.write('[')

output = []

########################################
######### Parse info from path #########
########################################

for pth in data:
 artist = pth.split('/')[2]

 if '/' in pth and pth.count('/') > 2:
  album = pth.split('/')[3]
  if ' - ' in album and album.count(' - ') > 0:
   album = album.split(' - ')[1]
   album = album.split('(')[0]
 else:
  album=''

 title = pth.split('/')[-1]
 title = title.split('-')[-1]
 title = title.split('.')[-2]

 # TODO:  what value for cacheid should we use ?
 albumart = "/albumart?cacheid=531&web="+urllib.request.pathname2url(artist)+"/extralarge&path=%2Fmnt%2FNAS%2Fmusic-nas%2F"+urllib.request.pathname2url(artist)+"&icon=fa-tags&metadata=true"

 output.append('{"service":"mpd","albumart":"'+albumart+'","title":"' + title.strip() + '","artist":"' + artist.strip() + '","album":"' + album.strip() + '","uri":"' + pth.strip() + '"}')

o.write(','.join(output))
o.write(']')
o.close()
print("Successfully added to " + plstname)
