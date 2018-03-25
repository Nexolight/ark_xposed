# Warning
This project is entirely WIP and in a relatively stale state. The master branch may break any time.
Don't expect any tutorials, help with issues or convinience stuff unless it's finished.

I'm personally using it on my server.

# ark_xposed
**A collection of tools to build extensions for ARK Survival Evolved**

## Content
* xposed.cfg - Text; Shared config file.
* ark_health.sh - bash; standalone; Restart server on fail (For single server setup).
* ark_start.sh - bash; standalone; My personal startup script
* ark_start_cluster.sh - bash; standalone; Just a wrapper for multiple start scripts (also includes ark_health.sh)
* ark_statistics.sh - bash; standalone; Creates a json file with play-times
* ark_chatlog.py - python; standalone; Provides a chatlog. This is primary part of the webchat for the xposed api. In order to use the CHATBOT options you need ark_statistics.py to collect player data.
* ark_update.sh - bash; standalone; Update ARK and ARK mods
* ark_xpose.py - python; standalone; Provide functions built on top of ark for access via web.
* mcrcon - bundled; native; A tiny third party rcon client for linux x86 

### What is this / Why it exists?
I started with my server and added the scripts over time in order to improve the unattended realiability and provide some stuff which other private ARK servers don't have. 

Due to that I added a webapi which allows to get some information into any other application.
The API accesses primary data collected by the standalone programs. And one day may also bring some interactive functionalities.


## Setup
When using the following setup the stuff provided here should work out of the box.
Please change xposed.cfg according to your needs...

* If you just want to use the upgrade script you can delete everything but ark_update.sh, xposed.cfg, and ark_start.sh (or a replacement). The upgrade script itself only uses STEAMDIR, ARKDIR and STARTUP_SCRIPT from the config.


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
* gettext
* perl
* python3
* python3 chardet (pip3)
* Python3 flask, flask-openid, flask-cors, py4j (pip3)
* Java 8
