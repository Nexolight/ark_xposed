# ark_xposed
**A collection of tools to build extensions for ARK Survival Evolved**

## Content
* ark_health.sh - bash; Restart server on fail.
* ark_start.sh - bash; My personal startup script
* ark_statistics.sh - bash; Creates a json file with play-times
* ark_update.sh - bash; Update ARK and ARK mods
* ark_xpose.py - python; Provide functions built on top of ark for access via web.
* mcrcon - bundled;native; A tiny third party rcon client for linux x86 

### A word from my side
I started with my server and added the scripts over time in order to improve the unattended realiability and provide some stuff which other private ARK servers don't have. 

The latest one (The RESTful API) came to my mind when I wanted to provide some stuff on the servers webpage which require user interactions and such stuff. I already accessed some info via ajax requests and I tought this is the best way to provide the functionality in a loose and easy way.

## Setup
When using the following setup the stuff provided here should work out of the box.
Please change xposed.cfg according to your needs...


#### Steam installation
/home/steam/steamcmd/
_(Assuming the Steam structure keeps the same)_

---

#### Folder for all the scripts
/home/steam/steamcmd/scripts (the git repo)

---

#### ARK installation:
/home/steam/steamcmd/steamapps/common/ARK
_(Assuming the Game structure keeps the same)_

---

#### Homepage
The point of this is to use this API via ajax requests.
I might provide some snipptes but the setup is up to you.
The API binds to port 6001 per default.

---

#### Dependencies
* common linux tools
* mcrcon (bundled)
* dos2unix
* perl
* python3
* python3 chardet (pip3)
* Python3 flask, flask-openid, flask-cors (pip3)
