# Volumio 3 (and 2) 'Recently Added' playlist generator

A Python script to be ran on a Volumio server that generates playlists consisting of recently added songs. 

This script generates a Volumio playlist to the folder `/data/playlist` from file added info in `/var/log/mpd.log`. The script automatically starts `mpc update` to update your Volumio library. 

# Dependencies

* `python3` which can be installed using the command `sudo apt python3` on volumio 2
* `pip3' which can be installed using `sudo apt-get install python3-pip`
* `mutagen` ID3 module for reading the ID3 tags which can be installed using `pip3 install mutagen`

# Usage

`./python3 lastsong.py`
```
-c, --changelog - Show changelog 
-h, --help - Show help 
-v, --version - Show version 
-s, --source-file - Define source file 
-p, --playlist-dir - Define destination directory 
-b, --library-base - The base of the music library
-i, --ignore-timer - Ignoring timer for waiting after mpc update 
-o, --one-playlist - Write only one playlist named RecentlyAdded 
```
Default sources are located in: 

* `/data/playlist` - Directory with custom playlists

* `/var/log/mpd.log` - Log file of volumio with last actions. **This empties on reboot**, so we maintain an 'added on' file to ensure persistence of memory. 

# Install

Copy file `lastsong.py` to `/home/volumio/`

For right function must be locales set to UTF-8. 

`dpkg-reconfigure locales`

and select your language and UTF-8

Recomended is added to cron. This is no longer installed in Volumio 2 by default. To add it:

`apt-get update && apt-get install -y cron`

`crontab -e`

add line

`0 * * * * /usr/bin/python3 -p /home/volumio/lastsong.py -o -b /Path/To/Library`

Changing /Path/To/Library to point to your library. This command updates the playlist every hour.

# Examples

**[Example 1]**

`./python3 lastsong.py`

Usual use of this script. Read mpd.log, select todays added files and create playlist 1-Monday in folder /data/playlist/. 

**[Example 2]**

`./python3 lastsong.py -o -b Path/to/library`

This use create single playlist file named RecentyAdded. 

**[Example 3]**

`./python3 lastsong.py -p /home/volumio/MyPlaylistDir/ -b Path/to/library`

Change destination folder. 

**[Example 4]**

`./python3 lastsong.py -i -b Path/to/library`

Skip waiting time after update mpd. **!!!Script creates playlist without Volumio updating mpd.log!!!**

**[Example 5]**

`./python3 lastsong.py -s /home/volumio/MyOwnLogFile.log -b Path/to/library`

Change source file. 
