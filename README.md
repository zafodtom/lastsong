# Volumio 3 (and 2) 'Recently Added' playlist generator

A Python script to be ran on a Volumio server that generates/ maintains playlists consisting of recently added songs. 

This script generates a Volumio playlist to the folder `/data/playlist` from file added info in `/var/log/mpd.log`. The script automatically starts `mpc update` to update your Volumio library. 

This is all done over a ssh connection to your server. To enable ssh, point your browser at `http://volumio.local/dev` and enable ssh. You can then connect from a terminal (or powershell) using the command `ssh volumio@volumio.local` password is **volumio**.


# Installation

Connect to your server over ssh, clone this repository:
 `git clone https://github.com/veebch/lastsong.git`
and install the dependencies.

## Dependencies

* `python3` which can be installed using the command `sudo apt python3` on volumio 2
* `pip3` which can be installed using `sudo apt-get install python3-pip`
* `mutagen` ID3 module for reading the ID3 tags which can be installed using `pip3 install mutagen`

## Usage
move into the cloned directory: `cd lastsong`

To run: 

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

* `/var/log/mpd.log` - Log file of volumio with last actions. **This empties on reboot**

# Automating

Cron is a nice easy way to schedule runs/updates. This is no longer installed in Volumio by default. To add it:

`apt-get update && apt-get install -y cron`

`crontab -e`

add line

`0 * * * * /usr/bin/python3 /home/volumio/lastsong/lastsong.py -o -b /Path/To/Library`

Changing /Path/To/Library to point to your library. This command updates the playlist every hour.

# Examples

`./python3 lastsong.py`

Usual use of this script. Read mpd.log, select todays added files and create playlist 1-Monday in folder /data/playlist/. 

`./python3 lastsong.py -o -b Path/to/library`

Creates a single playlist file named `RecentyAdded`. 

`./python3 lastsong.py -p /home/volumio/MyPlaylistDir/ -b Path/to/library`

Custom destination folder. 

`./python3 lastsong.py -i -b Path/to/library`

Run without updating the library first

`./python3 lastsong.py -s /home/volumio/MyOwnLogFile.log -b Path/to/library`

Change the source log file. 
