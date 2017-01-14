#!/bin/bash

if ps -u steam | grep -q "ShooterGameServ";then
	exit 0
elif ps -u steam | grep -q "ark_update.sh";then
	exit 0
elif ps -u steam | grep -q "ark_start.sh";then
	exit 0
elif ps -u steam | grep -q "bash";then
	exit 0
else
	echo "ARK is down! force restart: $(date)"
	/home/steam/steamcmd/scripts/ark_start.sh
	exit 0
fi
