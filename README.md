# lastsong.py
Python script for Volumio to generate playlists with last added songs

This script generate Volumio playlist to folder /data/playlist from file /var/log/mpd.log. 
Every weekday in single file. 
Python3 required
Recomended is added to cron (50 23 * * * python3 /home/volumio/lastsong.py)
