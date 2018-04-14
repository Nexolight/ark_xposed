#!/bin/bash

# Choose your map
# Valid maps: 
# "TheIsland","TheCenter","ScorchedEarth_P","Ragnarok","Aberration_P"
SMAP="Ragnarok"

# ! Edit this !
SESSION="Server Name"
MESSAGE="Welcome to our cluster!"
ADMINPW="changeme"
CLUSTERNAME="MyCluster"

# Ports used by your server
# Don't make them continuous for multiple servers. I use a +10 gap for each other server.
PORT=7777
QUERYPORT=27015
RCONPORT=32330

# Max players
MPLAYERS=70


# The path to the ShooterGameServer executable
SGAMESRV="/home/ark/steamcmd/steamapps/common/ARK/ShooterGame/Binaries/Linux/ShooterGameServer" 

$SGAMESRV \
"$SMAP\
?listen\
?SessionName=$SESSION\
?bRawSockets\
?Port=$PORT\
?QueryPort=$QUERYPORT\
?RCONEnabled=True\
?RCONPort=$RCONPORT\
?ServerAdminPassword=$ADMINPW\
?MaxPlayers=$MPLAYERS\
?Message=$MESSAGE\
?AllowAnyoneBabyImprintCuddle=true\
?ShowFloatingDamageText=true\
?AltSaveDirectoryName=$SMAP" \
-clusterid="$CLUSTERNAME" \
-NoTransferFromFiltering \
-server \
-UseBattlEye \
-vday \
-webalarm \
-nosteamclient &

echo "$SESSION is starting!"
