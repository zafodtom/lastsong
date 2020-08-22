# lastsong.py
Python script for Volumio to generate playlists with last added songs. 

This script generate Volumio playlist to folder `/data/playlist` from file `/var/log/mpd.log`. Every weekday in single file. Script automaticly start `mpc update` to update your volumio library. 

The script is composed of various parts found on the Internet and some my ideas. The basis is used from https://github.com/suuuehgi/m3u2volumio

# Version

0.3

# Dependencies

* `python3`

# Usage

`./python3 lastsong.py`
```
-c, --changelog - Show changelog 
-h, --help - Show help 
-v, --version - Show version 
-s, --source-file - Define source file 
-p, --playlist-dir - Define destination directory 
-i, --ignore-timer - Ignoring timer for waiting after mpc update 
-o, --one-playlist - Write only one playlist named RecentlyAdded 
```
Default sources are located in: 

* `/data/playlist` - Directory with custom playlists

* `/var/log/mpd.log` - Log file of volumio with last actions. **!!!After reboot this file are empty!!!**

# Install

Copy file `lastsong.py` to `/home/volumio/`

Recomended is added to cron. 

`crontab -e`

add line

`50 23 * * * python3 /home/volumio/lastsong.py`

This command start lastsong.py every day in 23:50

# Examples

**[Example 1]**

`./python3 lastsong.py`

Usual use of this script. Read mpd.log, select todays added files and create playlist 1-Monday in folder /data/playlist/. 

**[Example 2]**

`./python3 lastsong.py -o`

This use create single playlist file named RecentyAdded. 

**[Example 3]**

`./python3 lastsong.py -p /home/volumio/MyPlaylistDir/`

Change destination folder. 

**[Example 4]**

`./python3 lastsong.py -i`

Skip waiting time after update mpd. **!!!Script create playlist before volumio update mpd.log!!!**

**[Example 5]**

`./python3 lastsong.py -s /home/volumio/MyOwnLogFile.log`

Change source file. 
