#!/bin/bash

if pgrep -a ShooterGameSer;then
	exit 0	
elif pgrep -a ark_update;then
	exit 0
else
	echo "ARK is down! force restart: $(date)"
	/home/steam/steamcmd/scripts/ark_start.sh
	exit 0
fi
