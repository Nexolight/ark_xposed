# Warning
This is Work In Progress!
It is here just in case you find it interesting and are willing to figure certain things out in case you want to use it as well.

This project is a result of my needs for my personal cluster.
It started as a collection of scripts and was later merged to this project.
Thus it is a little messy and not ready for a "release".

# ark_xposed
**A collection of tools to build extensions for ARK Survival Evolved**

## Content
* `xposed.cfg` - Text; Shared config file.
* `ark_health.sh` - bash; Restart server on fail (For single server setup).
* `ark_start.sh` - bash; My personal startup script. Use it in combination with `ark_start_cluster.sh` and a `cronjob`.
* `ark_start_cluster.sh` - bash; Just a wrapper for multiple start scripts. Use it with a `cronjob`
* `ark_statistics.sh` - bash; Creates a json file with play-times. Additionally it will copy and convert player profiles on login/logout into json. Many things will not work that well without it.
* `ark_chatlog.py` - python; Creates and updates a chatlog file which is used by `ark_xposed.py` and includes the botadmin. Botadmin functionalities can be enabled/disabled in `xposed.cfg` under `CHATBOT_*`.
* `ark_update.sh` - bash; Update ARK and ARK mods
* `ark_xpose.py` - python; Provides some functionalities via web (not much yet).
* `mcrcon` - bundled; native; A tiny third party rcon client for linux x86 
* `ark-tools` - bundled; jar; A program used to convert savegames into json.
* `initfiles/runit/*` - shell; These are service files for `runit` - an init system like systemd (*caugh). 

### What is this / Why it exists?
This is a meanwhile merged scriptcollection to provide some advanced functions in ARK.
The main idea is to do it via RCON - as long as possible. 
It includes an API accessible from the web
which is intendet for stuff like web/ark crosschat, multiuser management, downloads, serverstatus, statistics etc.
Beside this it contains an update script for ARK as well as the used mods.
Furthermore there's a easily extendable botadmin which may help players with voted events 
(restart, daytime, whatever you have in mind...), rewards, etc. 

The files are all stored in a non binary format. If you whish you may make use of them.

---

There are many other Programs that do such stuff out there. There is no specific reason to use this.
I use it for myself as I prefer to have some control over it. 
I don't want to rely on others too much if something breaks.

## Setup

If you want to start fast without possible quirks, then the best advice
is to use the same setup as I do.

#### Cluster/Server Environment
I use all instances under the same user `ark` (`/home/ark`).
The different instances are started by a dedicated startup script for each.
Namely `ark_start.sh` as copy, edited and used with `ark_start_cluster.sh` via cronjob.
It is important to set the correct ports inside `xposed.cfg` as they will be used
for any rcon command.

The toolset respects the origin/destination for specific tasks. Don't worry.

When you use the structure described next you don't need to worry too much
about the other config options as well.

---

#### Folder for this toolset:
`/home/ark/ark_xposed` (git clone)

---

#### Steam installation
Referred in `xposed.cfg` as `STEAMDIR`

Use: `/home/ark/steamcmd/`
_(Assuming the Steam structure keeps the same)_

---

#### ARK installation:
Referred in `xposed.cfg` as `ARKDIR`

Use: `/home/ark/steamcmd/steamapps/common/ARK`
_(Assuming the Game structure keeps the same)_

---

#### WEB API (ark_xposed)
**Use nginx/apache as proxy!**
The point of this is to use this API via ajax requests.
I might provide some snipptes but the setup is up to you.
The API binds to port 6003 per default.
You will find the parameters and options via webbrowser at this port.

---

#### Dependencies
* common linux tools
* mcrcon (bundled)
* ark server tools (bundled)
* dos2unix
* gettext
* perl
* python3
* python3 chardet (pip3)
* Python3 flask, flask-openid, flask-cors, flask-session (pip3)
* Java 8
