#!/bin/bash

if pgrep -a -u $USER ark_update;then
	exit 0
fi


# You are supposed to copy the ark_start.sh script to $HOME
# and name it appropriate for each of your server instances
#
# Then let this script run every minute by a cronjob.
# It will simply call the startup scripts if the appropriate server isn't starting/started.
# You may change the delays. I use them to not strain the server too much.

if ! pgrep -a -u $USER ShooterGameSer | grep -Eo 'ShooterGameServer Ragnarok' &> /dev/null;then
	echo "$(date) - Starting Ragnarok"
	$HOME/ark.ragnarok.sh &
	sleep 60
fi

if ! pgrep -a -u $USER ShooterGameSer | grep -Eo 'ShooterGameServer Aberration' &> /dev/null;then
	echo "$(date) - Starting Aberration"
	$HOME/ark.aberration.sh &
	sleep 60
fi

if ! pgrep -a -u $USER ShooterGameSer | grep -Eo 'ShooterGameServer Scorched' &> /dev/null;then
	echo "$(date) - Starting Scorched Earth"
        $HOME/ark.scorchedearth.sh &
	sleep 60
fi

if ! pgrep -a -u $USER ShooterGameSer | grep -Eo 'ShooterGameServer TheIsland' &> /dev/null;then
       echo "$(date) - Starting The-Island"
        $HOME/ark.theisland.sh &
	sleep 60
fi

if ! pgrep -a -u $USER ShooterGameSer | grep -Eo 'ShooterGameServer TheCenter' &> /dev/null;then
       echo "$(date) - Starting The-Center"
        $HOME/ark.the-center.sh &
fi

