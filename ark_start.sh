#!/bin/bash
SESSION="Server name placeholder"
MESSAGE="Server message placeholder"
ADMINPW="changeme"
PORT=7777
QUERYPORT=27015
RCONPORT=32330
MPLAYERS=160

/home/steam/steamcmd/steamapps/common/ARK/ShooterGame/Binaries/Linux/ShooterGameServer \
"TheCenter\
?listen\
?SessionName=$SESSION\
?Port=$PORT\
?QueryPort=$QUERYPORT\
?RCONEnabled=True\
?RCONPort=$RCONPORT\
?ServerAdminPassword=$ADMINPW\
?MaxPlayers=$MPLAYERS\
?Message=$MESSAGE\
?AllowAnyoneBabyImprintCuddle=true" \
-server \
-USEALLAVAILABLECORES \
-UseBattlEye \
-vday \
-webalarm \
-nosteamclient &

echo "Server should be available in approximately 10 minutes"
