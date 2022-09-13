# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 18:33:45 2022

@author: Zed
"""

# img_viewer.py

# we will clean these up later but for now even leave unused imports
#we are not in cleanup phase yet
from PIL import Image 
from utils import launcherUtils, githubUtils
import PySimpleGUI as sg
import cloudscraper
import io
import json
import os.path
import requests
import sys



# Folder where script is placed, It looks in this for the Exectuable
if getattr(sys, 'frozen', False):
    LauncherDir = os.path.dirname(os.path.realpath(sys.executable))
elif __file__:
    LauncherDir = os.path.dirname(__file__)

installpath = str(LauncherDir + "\\resources\\")

#intialize default variables so they are never null
currentModderSelected = None
currentModSelected = None
currentModURL = None
currentModImage = None


#comment this out if you want to test with a local file
moddersAndModsJSON = requests.get("https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/ListOfMods.json").json()

j_file = json.dumps(moddersAndModsJSON)
#print(moddersAndModsJSON["Modding Community"][0]["name"])
#print(moddersAndModsJSON["Modding Community"][0]["URL"])


# First the window layout in 2 columns

mod_list_column = [
	[sg.Text("Available Mods", font=("Helvetica", 14))],
	[sg.Text("Mod Creator")], 
    [sg.Combo(list(moddersAndModsJSON.keys()), enable_events=True, key='pick_modder', size=(40, 0))],
    [sg.Text("Their Mods")], 
    [sg.Combo([], key='pick_mod', size=(40, 0),enable_events=True)]
]

installed_mods_column = [
    [sg.Text("Installed Mods", font=("Helvetica", 14))],
    [sg.Listbox(values=["This List is not", "Classic+"],size=(40,5),key="InstalledModListBox",enable_events=True)],
    [sg.Btn(button_text="Refresh"), sg.Btn(button_text="Uninstall")],
]

mod_details_column = [
    [sg.Text("Selected Mod", font=("Helvetica", 14))], 
    [sg.Text("", key="-SELECTEDMOD-"), sg.Text("", key="-SELECTEDMODURL-", visible=False)],
    [sg.Image(key="-SELECTEDMODIMAGE-")],
    [sg.Btn(button_text="Launch!")]
]

# ----- Full layout -----
layout = [
    [sg.Column([
        [sg.Column(installed_mods_column)],
        [sg.HSeparator()],
        [sg.Column(mod_list_column)],
        ]),
    sg.VSeparator(),
    sg.Column(mod_details_column)]
]

url= "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/appicon.ico"
jpg_data = (
                cloudscraper.create_scraper(
                    browser={"browser": "firefox", "platform": "windows", "mobile": False}
                )
                .get(url)
                .content
            )
            
pil_image = Image.open(io.BytesIO(jpg_data))
png_bio = io.BytesIO()
pil_image.save(png_bio, format="PNG")
iconfile = png_bio.getvalue()

url= "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/noRepoImageERROR.png"
jpg_data = (
                cloudscraper.create_scraper(
                    browser={"browser": "firefox", "platform": "windows", "mobile": False}
                )
                .get(url)
                .content
            )
            
pil_image = Image.open(io.BytesIO(jpg_data))
png_bio = io.BytesIO()
pil_image.save(png_bio, format="PNG")
noimagefile = png_bio.getvalue()

window = sg.Window('OpenGOAL Mod Launcher v0.02', layout, icon= iconfile, finalize=True)
def bootup():
    print("BOOT")
    
    #installed mods
    subfolders = [ f.name for f in os.scandir(os.getenv('APPDATA') + "\\OpenGOAL-Mods") if f.is_dir() ]
    if subfolders == []:
        subfolders = ["No Mods Installed"]
    print(subfolders)
    window["InstalledModListBox"].update(subfolders)
    
    #default mod selection on boot
    window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(1,1)))
    item = "Modding Community"
    window['pick_modder'].update(item)
    
    title_list = [i["name"] for i in moddersAndModsJSON[item]]
    window['pick_mod'].update(value=title_list[0], values=title_list)



    currentModderSelected = "Modding Community"
    currentModSelected = "Randomizer"
    currentModURL = "https://github.com/OpenGOAL-Unofficial-Mods/opengoal-randomizer-mod-pack/tree/main"
    currentModImage = None

    [currentModderSelected, currentModSelected, currentModURL, currentModImage] = handleModSelected()
	
def handleModSelected():
    tmpModderSelected = window['pick_modder'].get()
    tmpModSelected = window['pick_mod'].get()
    tmpModURL = None
    tmpModImage = None
    
    for mod in moddersAndModsJSON[tmpModderSelected]:
        if mod["name"] == tmpModSelected:
            tmpModURL = mod["URL"]
    
    tmpModImage = githubUtils.returnModImageURL(tmpModURL)

    
    url = tmpModImage
    try:
        r = requests.head(tmpModImage).status_code
        print(str(r))
        if r == 200:
            jpg_data = (
                cloudscraper.create_scraper(
                    browser={"browser": "firefox", "platform": "windows", "mobile": False}
                )
                .get(url)
                .content
            )
            
            pil_image = Image.open(io.BytesIO(jpg_data))
            png_bio = io.BytesIO()
            pil_image.save(png_bio, format="PNG")
            png_data = png_bio.getvalue()
            window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(png_data ,resize=(250,250)))
            # prints the int of the status code. Find more at httpstatusrappers.com :)    
        else:
            window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(250,250)))

    except requests.exceptions.MissingSchema:
        window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(250,250)))

    window['-SELECTEDMOD-'].update(tmpModSelected)
    window['-SELECTEDMODURL-'].update(tmpModURL)
    return [tmpModderSelected, tmpModSelected, tmpModURL, tmpModImage]

def handleInstalledModSelected():
    if len(window['InstalledModListBox'].get()) == 0:
        return [None, None]
        
    tmpModSelected = window['InstalledModListBox'].get()[0]
    tmpModderSelected = None

    for modder in moddersAndModsJSON.keys():
        if not tmpModderSelected:
            for mod in moddersAndModsJSON[modder]:
                if mod["name"] == tmpModSelected:
                    tmpModderSelected = modder
                    break

    return [tmpModderSelected, tmpModSelected]

def refreshInstalledList():
    subfolders = [ f.name for f in os.scandir(os.getenv('APPDATA') + "\\OpenGOAL-Mods") if f.is_dir() ]
    window["InstalledModListBox"].update(subfolders)

bootupcount = 0
# Run the Event Loop
if bootupcount == 0:
    bootup()
while True:
    event, values = window.read()

    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    
    # Folder name was filled in, make a list of files in the folder
    if event == "InstalledModListBox" and not window["InstalledModListBox"].get() == ['No Mods Installed']:
        [tmpModderSelected, tmpModSelected] = handleInstalledModSelected()

        if not tmpModderSelected:
            sg.Popup('Installed mod not recognized!', keep_on_top=True)
            window['-SELECTEDMOD-'].update(tmpModSelected)
            window['-SELECTEDMODURL-'].update("")
            local_img = launcherUtils.local_mod_image(tmpModSelected)
            if local_img:
                window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(local_img ,resize=(250,250)))
            else:
                window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(250,250)))
        else:
            window['pick_modder'].update(tmpModderSelected)
            title_list = [i["name"] for i in moddersAndModsJSON[tmpModderSelected]]
            window['pick_mod'].update(value=tmpModSelected, values=title_list)
            
            handleModSelected()
    elif event == "Refresh":
        refreshInstalledList()
    elif event =='pick_modder':
        window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(1,1)))
        item = values[event]
        print(item)
        title_list = [i["name"] for i in moddersAndModsJSON[item]]
        window['pick_mod'].update(value=title_list[0], values=title_list)
        handleModSelected()
    elif event =='pick_mod':
        handleModSelected()
    elif event == "Launch!":
        tmpModSelected = window['-SELECTEDMOD-'].get()
        tmpModURL = window['-SELECTEDMODURL-'].get()

        if tmpModURL:
            # online launch
            window['Launch!'].update(disabled=True)
            [linkType, tmpModURL] = githubUtils.identifyLinkType(tmpModURL)
            launcherUtils.launch(tmpModURL, tmpModSelected, linkType)
            #turn the button back on
            window['Launch!'].update(disabled=False)
            #may have installed new mod, update list
            refreshInstalledList()
        elif tmpModSelected:
            # local launch
            window['Launch!'].update(disabled=True)
            err = launcherUtils.launch_local(tmpModSelected)
            if err:
                sg.popup("Error: " + err)
            #turn the button back on
            window['Launch!'].update(disabled=False)
        else:
            sg.Popup('No mod selected', keep_on_top=True)
    elif event == "Uninstall":
        [tmpModderSelected, tmpModSelected] = handleInstalledModSelected()
        if tmpModSelected:
            dir = os.getenv('APPDATA') + "\\OpenGOAL-Mods\\" + tmpModSelected
            ans = sg.popup_ok_cancel('Confirm: uninstalling ' + dir)
            if ans == 'OK':
                launcherUtils.try_remove_dir(dir)
                refreshInstalledList()
                window['-SELECTEDMOD-'].update("")
                window['-SELECTEDMODURL-'].update("")
                window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(1,1)))
                sg.popup('Uninstalled ' + tmpModSelected)
        else:
            sg.popup('No mod selected')

window.close()