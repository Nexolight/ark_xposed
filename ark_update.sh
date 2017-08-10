#!/bin/bash
SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)
function getFromCfg(){
	cat $SCRIPTPATH/xposed.cfg | grep -Po "(?<=^$1\=)(.*)$" | tr -d '\n' | envsubst 
}
function getFromArkCfg(){
	FILE="$(getFromCfg ARKDIR)/ShooterGame/Saved/Config/LinuxServer/GameUserSettings.ini"
	dos2unix $FILE &> /dev/null && cat $FILE | grep -Po "(?<=^$1\=)(.*)$" | tr -d '\n'
}
#Required folders
#The folder where steamcmd.sh is located
STEAMDIR="$(getFromCfg STEAMDIR)"
#The folder where steamcmd downloads the mods and lists them named by their mod id
STEAMMODDIR="$STEAMDIR/steamapps/common/ARK/steamapps/workshop/content/346110"
#You're not forced to place your server startup script there. Just give enter the full path of the script
STARTUPSCRIPT="$(getFromCfg STARTUP_SCRIPT)"
#The ARK root directory
GAMEDIR="$(getFromCfg ARKDIR)"
#The full path to the GameUserSettings.ini
BASECONFIG=$GAMEDIR/ShooterGame/Saved/Config/LinuxServer/GameUserSettings.ini
MMHINT="\n\nIf you get a version missmatch after the restart then delete your local (outdated) mod version to force steam to redownload it. See ark420-the.center --> faq (right side)\nhttp://ark420-the.center/index.php/faq/"
#Steam user
#No explination needed
STEAMUSER="anonymous"
STEAMPW=""

#MCRCON - Download at https://sourceforge.net/projects/mcrcon/
MCRCON="$SCRIPTPATH/thirdparty/mcrcon"
#The port where ark rcon service is listening
MCRCONPORT="$(getFromArkCfg RCONPort)"

###############################################################################

######################################################################################

#You can ignore this stuff unless you get any errors.
#However some of them will occur but are not problematic
#This function was not done by me
#Copyright (c) of this function - 2015 Fez Vrasta
#https://github.com/FezVrasta/ark-server-tools
doExtractMod(){
  local modid=$1
  local modsrcdir="$STEAMMODDIR/$modid"
  local moddestdir="$GAMEDIR/ShooterGame/Content/Mods/$modid"
  local modbranch="${mod_branch:-Windows}"

  for varname in "${!mod_branch_@}"; do
    if [ "mod_branch_$modid" == "$varname" ]; then
      modbranch="${!varname}"
    fi
  done

  if [ \( ! -f "$moddestdir/.modbranch" \) ] || [ "$(<"$moddestdir/.modbranch")" != "$modbranch" ]; then
    rm -rf "$moddestdir"
  fi

  if [ -f "$modsrcdir/mod.info" ]; then
    echo "Copying files to $moddestdir"

    if [ -f "$modsrcdir/${modbranch}NoEditor/mod.info" ]; then
      modsrcdir="$modsrcdir/${modbranch}NoEditor"
    fi

    find "$modsrcdir" -type d -printf "$moddestdir/%P\0" | xargs -0 -r mkdir -p

    find "$modsrcdir" -type f ! \( -name '*.z' -or -name '*.z.uncompressed_size' \) -printf "%P\n" | while read f; do
      if [ \( ! -f "$moddestdir/$f" \) -o "$modsrcdir/$f" -nt "$moddestdir/$f" ]; then
        printf "%10d  %s  " "`stat -c '%s' "$modsrcdir/$f"`" "$f"
        cp "$modsrcdir/$f" "$moddestdir/$f"
        echo -ne "\r\\033[K"
      fi
    done

    find "$modsrcdir" -type f -name '*.z' -printf "%P\n" | while read f; do
      if [ \( ! -f "$moddestdir/${f%.z}" \) -o "$modsrcdir/$f" -nt "$moddestdir/${f%.z}" ]; then
        printf "%10d  %s  " "`stat -c '%s' "$modsrcdir/$f"`" "${f%.z}"
        perl -M'Compress::Raw::Zlib' -e '
          my $sig;
          read(STDIN, $sig, 8) or die "Unable to read compressed file";
          if ($sig != "\xC1\x83\x2A\x9E\x00\x00\x00\x00"){
            die "Bad file magic";
          }
          my $data;
          read(STDIN, $data, 24) or die "Unable to read compressed file";
          my ($chunksizelo, $chunksizehi,
              $comprtotlo,  $comprtothi,
              $uncomtotlo,  $uncomtothi)  = unpack("(LLLLLL)<", $data);
          my @chunks = ();
          my $comprused = 0;
          while ($comprused < $comprtotlo) {
            read(STDIN, $data, 16) or die "Unable to read compressed file";
            my ($comprsizelo, $comprsizehi,
                $uncomsizelo, $uncomsizehi) = unpack("(LLLL)<", $data);
            push @chunks, $comprsizelo;
            $comprused += $comprsizelo;
          }
          foreach my $comprsize (@chunks) {
            read(STDIN, $data, $comprsize) or die "File read failed";
            my ($inflate, $status) = new Compress::Raw::Zlib::Inflate();
            my $output;
            $status = $inflate->inflate($data, $output, 1);
            if ($status != Z_STREAM_END) {
              die "Bad compressed stream; status: " . ($status);
            }
            if (length($data) != 0) {
              die "Unconsumed data in input"
            }
            print $output;
          }
        ' <"$modsrcdir/$f" >"$moddestdir/${f%.z}"
        touch -c -r "$modsrcdir/$f" "$moddestdir/${f%.z}"
        echo -ne "\r\\033[K"
      fi
    done

    perl -e '
      my $data;
      { local $/; $data = <STDIN>; }
      my $mapnamelen = unpack("@0 L<", $data);
      my $mapname = substr($data, 4, $mapnamelen - 1);
      $mapnamelen += 4;
      my $mapfilelen = unpack("@" . ($mapnamelen + 4) . " L<", $data);
      my $mapfile = substr($data, $mapnamelen + 8, $mapfilelen);
      print pack("L< L< L< Z8 L< C L< L<", $ARGV[0], 0, 8, "ModName", 1, 0, 1, $mapfilelen);
      print $mapfile;
      print "\x33\xFF\x22\xFF\x02\x00\x00\x00\x01";
    ' $modid <"$moddestdir/mod.info" >"$moddestdir/.mod"

    if [ -f "$moddestdir/modmeta.info" ]; then
      cat "$moddestdir/modmeta.info" >>"$moddestdir/.mod"
    else
      echo -ne '\x01\x00\x00\x00\x08\x00\x00\x00ModType\x00\x02\x00\x00\x001\x00' >>"$moddestdir/.mod"
    fi

    echo "$modbranch" >"$moddestdir/.modbranch"
  fi
}

echo ""
echo "ARK dedicated Server update Script v2.0"
echo "$(date) Try to update ARK installation"
echo "-------------------------------------------------------"
dorestart=0
echo ""
echo "Using command to update ARK..."
echo "-------------------------------------------------------"
echo ""
arkupdate=$($STEAMDIR/steamcmd.sh +login $STEAMUSER $STEAMPW +force_install_dir $GAMEDIR +app_update 376030 +quit | tee /dev/tty)
echo ""
if [[ "$arkupdate" == *"Success! App '376030' already up to date."* ]]; then
        echo "ARK seems to be up to date"
elif [[ "$arkupdate" == *"Error! App '376030' state is"* ]]; then
        echo "ARK cannot update - got an error code"
elif [[ "$arkupdate" == *"Success! App '376030' fully installed."* ]]; then
        dorestart=1
else
        echo "unknown error while updating ARK"
fi
        echo "ARK update check performed at: $(date)"

activemodsIDs=/tmp/arkmods_enabled
beforeUpdateIDs=/tmp/arkmods_old_ids
beforeUpdate=/tmp/arkmods_old
afterUpdate=/tmp/arkmods_new
echo ""
echo "Looking up current steam mod directory (pre-update)..."
echo "-------------------------------------------------------"
echo ""
modcheckbefore=$(ls -l -t "$STEAMMODDIR" | tee $beforeUpdate)
cat $beforeUpdate | grep -Eo "[0-9]{9}$" > $beforeUpdateIDs
echo "State of steam mod dir:"
echo "$modcheckbefore"
echo ""
echo "Looking up current GameUserConfig file..."
echo "-------------------------------------------------------"
echo ""
activemods=$(dos2unix -q $BASECONFIG && cat $BASECONFIG | grep "ActiveMods=" | cut -d "=" -f 2 | sed 's/,$//' | xargs -d ',' -n1 echo | tee $activemodsIDs)
echo "Mods contained in list:"
echo "$activemods"
echo ""
echo "Removing mods which were removed from config..."
echo "-------------------------------------------------------"
echo ""
for installedID in $(cat $beforeUpdateIDs);do
        if ! grep -xo $installedID $activemodsIDs &> /dev/null;then
                echo "Mod $installedID was removed from config - Removing mod"
                dorestart=1
                if [ -f "$STEAMMODDIR/../../appworkshop_346110.acf" ];then
                        sed -i -n -E '1h;1!H;${;g;s/\"'"$installedID"'\"[^\{]*[^\}]*.{1}\s*//g;p;}' "$STEAMMODDIR/../../appworkshop_346110.acf"
                fi
                if [ -d "$GAMEDIR/ShooterGame/Content/Mods/$installedID" ];then
                        rm -r "$GAMEDIR/ShooterGame/Content/Mods/$installedID"
                fi
                if [ -d "$STEAMMODDIR/$installedID" ];then
                        rm -r "$STEAMMODDIR/$installedID"
                fi
        fi
done
modupdatelist=$(echo $activemods | xargs -n1 echo +workshop_download_item 346110)
echo ""
echo "Using command to update mods..."
echo "-------------------------------------------------------"
echo ""
modupdates=$($STEAMDIR/steamcmd.sh +login $STEAMUSER $STEAMPW +force_install_dir $GAMEDIR $modupdatelist +quit | tee /dev/tty)
echo ""
echo "Looking up current steam mod directory (post-update)..."
echo "-------------------------------------------------------"
echo ""
modcheckafter=$(ls -l -t "$STEAMMODDIR" | tee $afterUpdate)
echo "State of steam mod dir:"
echo "$modcheckafter"
echo ""
echo ""
echo "Comparing old and new steam mod directory state"
echo "-------------------------------------------------------"
echo ""
if [[ "$modcheckbefore" != "$modcheckafter" ]]; then
        echo "Something changed - restart scheduled"
        dorestart=1
        updated=$(grep -v -x -f $beforeUpdate $afterUpdate | grep -Eo "[0-9]{9}$")
        for updatedmod in $updated;do
                if [ -d "$GAMEDIR/ShooterGame/Content/Mods/$updatedmod" ];then
                        echo ""
                        echo "Mod $updatedmod got an update! Performing update..."
                        echo "-------------------------------------------------------"
                        echo ""
                        rm -r "$GAMEDIR/ShooterGame/Content/Mods/$updatedmod"
                else
                        echo ""
                        echo "New mod $updatedmod detected! - Performing installation..."
                        echo "-------------------------------------------------------"
                        echo ""
                fi
                doExtractMod "$updatedmod"
        done
else
        echo "No differences found - everything is up to date"
fi
echo ""
echo "ARK mods update check performed at: $(date)"
echo "-------------------------------------------------------"
echo ""
if (("$dorestart" > 0)); then
        MCRCONPW="$(getFromArkCfg ServerAdminPassword)"
        echo "ARK was updated successfully"
        echo "ARK update performed at: $(date)\n"
        echo "Warning users about server restart"
        $MCRCON -c -H 127.0.0.1 -P $MCRCONPORT -p $MCRCONPW cmd1 "broadcast New updates are installed now\nThe server is going to restart in 15min.\nThe world will be saved before restart\n"
        sleep 300
        echo "2nd warning"
        $MCRCON -c -H 127.0.0.1 -P $MCRCONPORT -p $MCRCONPW cmd1 "broadcast 10min left until restart (Updates)\n"
        sleep 300
        echo "3th warning"
        $MCRCON -c -H 127.0.0.1 -P $MCRCONPORT -p $MCRCONPW cmd1 "broadcast 5min left until restart (Updates)\n"
        sleep 180
        echo "4th Saving world warning - countdown"
        $MCRCON -c -H 127.0.0.1 -P $MCRCONPORT -p $MCRCONPW cmd1 "broadcast 2min left until restart (Updates)\n1min left until the ark will be saved\nThe savegame is restored after the restart\n"
        COUNTDOWNSAVE=59
        until [ $COUNTDOWNSAVE -eq -1 ]
        do
                $MCRCON -c -H 127.0.0.1 -P $MCRCONPORT -p $MCRCONPW cmd1 "broadcast $COUNTDOWNSAVE seconds left until save\n$(($COUNTDOWNSAVE + 60)) seconds until restart.$MMHINT"
                COUNTDOWNSAVE=$(($COUNTDOWNSAVE - 1))
                sleep 1
        done
        $MCRCON -c -H 127.0.0.1 -P $MCRCONPORT -p $MCRCONPW cmd1 "SaveWorld"
        echo "5th warning - countdown"
        COUNTDOWN=59
        until [ $COUNTDOWN -eq -1 ]
        do
                $MCRCON -c -H 127.0.0.1 -P $MCRCONPORT -p $MCRCONPW cmd1 "broadcast Server restart in $COUNTDOWN seconds.$MMHINT"
                COUNTDOWN=$(($COUNTDOWN - 1))
                sleep 1
        done
        echo "Kill server now. pls wait..."
        killall -w -v  ShooterGameServer | tee /dev/tty
        wait
        echo "Startup server again"
        $STARTUPSCRIPT &
        sleep 5
else
        echo "No updates required"
fi
echo ""
echo "ARK update script finished at: $(date)"
echo "-------------------------------------------------------"
echo ""
