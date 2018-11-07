#!/usr/bin/env python3
import subprocess
import time
import os

# Path pattern to block
apppattern = ".*idea.Main.*"
#apppattern = "jetbrains-idea"

# Write a backup that can restore the settings at the
# start of the script.
# Leave empty to not write a backup.
backupfile = "~/.keymap_backup"

# Add the keys to be disabled below.
shortcuts = {
    "org.gnome.settings-daemon.plugins.media-keys/key" : "gsettings",
    "/org/gnome/desktop/wm/keybindings/key" : "dconf",
    # CTRL + ALT + Backspace
    "org.gnome.settings-daemon.plugins.media-keys/logout" : "gsettings",
    # CTRL + ALT + L
    "org.gnome.settings-daemon.plugins.media-keys/screensaver" : "gsettings",
    # CTRL + ALT + T
    "org.gnome.settings-daemon.plugins.media-keys/terminal" : "gsettings",
    # ALT + F6
    "org.gnome.desktop.wm.keybindings/cycle-group" : "gsettings",
    # ALT + F7
    "org.gnome.desktop.wm.keybindings/begin-move" : "gsettings",
    # ALT + F8
    "org.gnome.desktop.wm.keybindings/begin-resize" : "gsettings",
    # CTRL + ALT + S
    "org.gnome.desktop.wm.keybindings/toggle-shaded" : "gsettings",

    "org.gnome.desktop.wm.keybindings/move-to-workspace-left" : "gsettings",
    "org.gnome.desktop.wm.keybindings/move-to-workspace-right" : "gsettings",
    "org.gnome.desktop.wm.keybindings/move-to-workspace-up" : "gsettings",
    "org.gnome.desktop.wm.keybindings/move-to-workspace-down" : "gsettings",
    "org.gnome.desktop.wm.keybindings/panel-main-menu" : "gsettings",
    "org.gnome.desktop.wm.keybindings/toggle-maximized" : "gsettings",
    "org.gnome.desktop.wm.keybindings/unmaximize" : "gsettings",
    "org.gnome.desktop.wm.keybindings/activate-window-menu" : "gsettings",
    "org.gnome.desktop.wm.keybindings/cycle-group-backward" : "gsettings",
    "org.gnome.desktop.wm.keybindings/cycle-panels" : "gsettings",
    "org.gnome.desktop.wm.keybindings/switch-group" : "gsettings",
    "org.gnome.desktop.wm.keybindings/switch-group-backward" : "gsettings",
    "org.gnome.desktop.wm.keybindings/switch-panels" : "gsettings",
    "org.gnome.desktop.wm.keybindings/switch-panels-backward" : "gsettings",
    "org.gnome.desktop.wm.keybindings/switch-to-workspace-up" : "gsettings",
    "org.gnome.desktop.wm.keybindings/switch-to-workspace-down" : "gsettings",
    # ALT + `
    # ??
    # ALT + F1, Super + S
    # ??
}

#
# Helper functions
#

# Run a command on the shell
def run(cmd):
    subprocess.Popen(cmd)

# Run a command on the shell and return the
# stripped result
def get(cmd):
    try:
        return subprocess.check_output(cmd).decode("utf-8").strip()
    except:
        pass

# Get the PID of the currently active window
def getactive():
    xdoid = get(["xdotool", "getactivewindow"])
    pidline = [l for l in get(["xprop", "-id", xdoid]).splitlines()\
                 if "_NET_WM_PID(CARDINAL)" in l]
    if pidline:
        pid = pidline[0].split("=")[1].strip()
    else:
        # Something went wrong
        print("Warning: Could not obtain PID of current window")
        pid = ""

    return pid

def readkey(key):
    if shortcuts[key] == "gsettings":
        return get(["gsettings", "get"] + key.split("/"))
    elif shortcuts[key] == "dconf":
        return get(["dconf", "read", key])

def writekey(key, val):
    if val == "": 
        val = "['']"
    if shortcuts[key] == "gsettings":        
        run(["gsettings", "set"] + key.split("/") + [val])
    elif shortcuts[key] == "dconf":
        run(["dconf", "write", key, val])

def resetkey(key):
    if shortcuts[key] == "gsettings":
        run(["gsettings", "reset"] + key.split("/"))
    elif shortcuts[key] == "dconf":
        run(["dconf", "reset", key])

# If val == True, disables all shortcuts.
# If val == False, resets all shortcuts.
def setkeys(flag):
    for key, val in shortcutmap.items():
        if flag == True:
            # Read current value again; user may change
            # settings, after all!
            shortcutmap[key] = readkey(key)
            writekey(key, "")            
        elif flag == False:
            if val:
                writekey(key, val)
            else:
                resetkey(key)

#
# Main script
#

# Store current shortcuts in case they are non-default
# Note: if the default is set, dconf returns an empty string!
# Optionally, create a backup script to restore the value in case
# this script crashes at an inopportune time.
shortcutmap = {}
if backupfile:
    f = open(os.path.expanduser(backupfile),'w+') 
    f.write('#!/bin/sh\n')

for key, val in shortcuts.items():
    if shortcuts[key] == "gsettings":
        shortcutmap[key] = get(["gsettings", "get"] + key.split("/"))

        if backupfile:
            if shortcutmap[key]:
                f.write("gsettings set " + " ".join(key.split("/")) + " " + 
                shortcutmap[key] + "\n")
            else:
                f.write("gsettings reset " + " ".join(key.split("/")) + "\n")
    elif shortcuts[key] == "dconf":
        shortcutmap[key] = get(["dconf", "read", key])

        if backupfile:
            if shortcutmap[key]:
                f.write("dconf write " + key + " " + shortcutmap[key] + "\n")
            else:
                f.write("dconf reset " + key + "\n")

if backupfile: f.close()

# Check every half second if the window changed form or to a 
# matching application.
front1 = None
while True:
    time.sleep(0.5)
    checkpids = get(["pgrep", "-f", apppattern])

    if checkpids:
        checkpids = checkpids.splitlines()
        activepid = getactive()

        if activepid:
            front2 = True if activepid in checkpids else False
        else:
            front2 = False
    else:
        front2 = False

    if front2 != front1:
        if front2:
            setkeys(True)
        else:
            setkeys(False)
    front1 = front2
