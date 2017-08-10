#!/bin/bash
SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)
function getFromCfg(){
        cat $SCRIPTPATH/xposed.cfg | grep -Po "(?<=^$1\=)(.*)$" | tr -d '\n'
}
STATSF="$SCRIPTPATH/$(getFromCfg STATS_PLAYERDB)"
STATSFC=$(cat "$STATSF")
if [ -f "$STATSF" ] && [ ! -z "$STATSFC" ];then
	cp "$STATSF" "$STATSF.bkup"
fi
