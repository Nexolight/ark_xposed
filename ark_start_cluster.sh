#!/bin/bash

if pgrep -a ark_update;then
	exit 0
fi


# You are supposed to copy the ark_start.sh script to /home/ark
# and name it appropriate for each of your server instances
#
# Then let this script run every minute by a cronjob.
# It will simply call the startup scripts if the appropriate server isn't starting/started.
# You may change the delays. I use them to not strain the server too much.

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer Ragnarok' &> /dev/null;then
	echo "$(date) - Starting Ragnarok"
	/home/ark/ark.ragnarok.sh &
	sleep 60
fi

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer Aberration' &> /dev/null;then
	echo "$(date) - Starting Aberration"
	/home/ark/ark.aberration.sh &
	sleep 60
fi

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer Scorched' &> /dev/null;then
	echo "$(date) - Starting Scorched Earth"
        /home/ark/ark.scorchedearth.sh &
	sleep 60
fi

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer TheIsland' &> /dev/null;then
       echo "$(date) - Starting The-Island"
        /home/ark/ark.theisland.sh &
	sleep 60
fi

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer TheCenter' &> /dev/null;then
       echo "$(date) - Starting The-Center"
        /home/ark/ark.the-center.sh &
fi

