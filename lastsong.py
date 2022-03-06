#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
from subprocess import Popen, PIPE
import sys, os
import time
from collections import OrderedDict
import datetime
import argparse
import re
import urllib.request
from mutagen.easyid3 import EasyID3
from urllib.parse import quote

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

parser.add_argument('-b', '--librarybase', default='/NAS/peachy/',
            action='store', dest='librarybase',
                    help='The base URL of the library')

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
# mpd.log empties on reboot, and dates
# do not include year, so if uptime is 
# more than a year (!) it will get confused

data=[]
dates = []
pattern= ': added'
if results.oneplst:
    daysback = 28 # If the single playlist flag is added , look multiple days back. (make command line parameter?
else:
    daysback = 1 
for i in range(daysback):
    dates.append((datetime.datetime.today()-datetime.timedelta(days=i)).strftime('%h %d'))

# match anything added in the last 'daysback' days - Also, reverse order, so most recent are at the top 
with open(results.sfile, encoding='utf-8', mode='r') as file:
    lines = file.readlines()
    for line in reversed(lines):
        if re.search(pattern, line) and re.search('|'.join(dates), line):
            data.append(line.split('added ',1)[1].strip())
print(data)

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
######### Parse info from ID3 file #####
########################################

librarybase = results.librarybase

for pth in data:
    path = '/mnt/'+pth.strip()
    if os.path.isfile(path) == False:
            print('The audio file is missing')
    else:
        try:
            audio = EasyID3(path)
            artist = ''.join(audio['artist'])
            album = ''.join(audio['album'])
            title = ''.join(audio['title'])
            # a precaution for now
            artistfrompath = pth.split('/')[2]
            albumart = "/albumart?web="+artist+"/"+album+"/extralarge&path="+quote(librarybase)+urllib.request.pathname2url(artistfrompath)+"&icon=fa-tags&metadata=true"
            output.append('{"service":"mpd","albumart":"'+albumart+'","title":"' + title  + '","artist":"' + artist  + '","album":"' + album + '","uri":"' + pth.strip() + '"}')
            # get info from the metadata rather than the path alone
        except Exception as e:
            print(e)
            # there must have been an issue, eg no tags, revert to path parsing
            artist = pth.split('/')[2]
            artistfrompath = artist
            album=''        
            title = pth.split('/')[-1]
            title = title.split('.')[-2]
            albumart = ''
            output.append('{"service":"mpd","albumart":"'+albumart+'","title":"' + title.strip()+ '","artist":"' + artist.strip()  + '","album":"' + album.strip() + '","uri":"' + pth.strip() + '"}')
        except:
            pass
o.write(','.join(output))
o.write(']')
o.close()
print("Successfully added to " + plstname)
