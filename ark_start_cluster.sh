#!/bin/bash

if pgrep -a ark_update;then
	exit 0
fi

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer Ragnarok' &> /dev/null;then
	echo "$(date) - Starting Ragnarok"
	/home/ark/ark.ragnarok.sh &
	sleep 120
fi

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer Aberration' &> /dev/null;then
	echo "$(date) - Starting Aberration"
	/home/ark/ark.aberration.sh &
	sleep 120
fi

if ! pgrep -a ShooterGameSer | grep -Eo 'ShooterGameServer Scorched' &> /dev/null;then
	echo "$(date) - Starting Scorched Earth"
        /home/ark/ark.scorchedearth.sh &
        sleep 120
fi

