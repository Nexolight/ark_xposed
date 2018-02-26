#!/bin/bash

if pgrep -a ark_update;then
	exit 0
fi

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer Ragnarok' &> /dev/null;then
	echo "$(date) - Starting Ragnarok"
	/home/ark/ark.ragnarok.sh &
	sleep 15
fi

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer Aberration' &> /dev/null;then
	echo "$(date) - Starting Aberration"
	/home/ark/ark.aberration.sh &
	sleep 15
fi

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer Scorched' &> /dev/null;then
	echo "$(date) - Starting Scorched Earth"
        /home/ark/ark.scorchedearth.sh &
	sleep 15
fi

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer TheIsland' &> /dev/null;then
       echo "$(date) - Starting The-Island"
        /home/ark/ark.theisland.sh &
	sleep 15
fi

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer TheCenter' &> /dev/null;then
       echo "$(date) - Starting The-Center"
        /home/ark/ark.the-center.sh &
fi

