import requests
from requests.auth import HTTPBasicAuth
import json

import _tkinter
import tkinter
from tkinter import *
from tkinter import ttk

# Replace with auth data from Brewfather
auth = HTTPBasicAuth('luhe82GBTIS5ghVWvMUNBMj7pwI2', 'TTeC59kzR9rNiwfl4giLcWHa29Z9tERAeaZqgyEgdN7MhjiSwOW899TDOkis0i6X')

gToOzConversion = 0.03527
lToGalConversion = 0.264172

def cToFConversion( degreesC):
    return degreesC * 1.80 + 32.0

def getBatch( batchId ):
    #query = {'include' : 'recipe.mash,recipe.equipment,recipe.data'}
    query = {'include' : ''} # Uncommenting will pull down 'all' batch data

    response = requests.get('https://api.brewfather.app/v2/batches/' + batchId, auth=auth, params=query)
    batch = response.json()
    #print( json.dumps(batch, indent=2) )

    data = '[{"Name":"Recipe","Value":"' + batch['recipe']['name'] + '"}'
    
    # Mash Steps
    indx = 1
    for step in batch['recipe']['mash']['steps']:
        #print( json.dumps(step, indent=2) )
        data = data + ', {"Name":"Mash Temp ' + str(indx) + '","Value":"' + str(cToFConversion(step['stepTemp'])) + '"}'
        hours = int(step['stepTime'] / 60)
        minutes = step['stepTime'] % int(60)
        data = data + ', {"Name":"Mash Length ' + str(indx) + '","Value":"' + str(hours) + ':' + str(minutes) + ':00"}'
        indx = indx + 1
    
    # Zero out any remaining from previous batch
    while indx < 7:
        data = data + ', {"Name":"Mash Temp ' + str(indx) + '","Value":"0.00"}'
        data = data + ', {"Name":"Mash Length ' + str(indx) + '","Value":"00:00:00"}'
        indx = indx + 1 
    
    # Hops Schedule
    # Zero out any remaining from previous batch
    indx = 1
    while indx < 7:
        data = data + ', {"Name":"Hops Amount ' + str(indx) + '","Value":"0.00"}'
        data = data + ', {"Name":"Hops Time ' + str(indx) + '","Value":"00:00:00"}'
        data = data + ', {"Name":"Hops Name ' + str(indx) + '","Value":""}'
        data = data + ', {"Name":"Hops Whirlpool ' + str(indx) + '","Value":"0"}'
        indx = indx + 1 

    indx = 1
    for hops in batch['recipe']['hops']:
        #print( json.dumps(hops, indent=2) )
        if hops['use'] == "Dry Hop":
            continue

        data = data + ', {"Name":"Hops Amount ' + str(indx) + '","Value":"' + str(hops['amount'] * gToOzConversion) + '"}'
        hours = int(hops['time'] / 60)
        minutes = hops['time'] % int(60)
        data = data + ', {"Name":"Hops Time ' + str(indx) + '","Value":"' + str(hours) + ':' + str(minutes) + ':00"}'
        data = data + ', {"Name":"Hops Name ' + str(indx) + '","Value":"' + hops['name'] + '"}'
        if "temp" in hops:
            if hops['temp'] is not None:
                data = data + ', {"Name":"Hops Whirlpool ' + str(indx) + '","Value":"' + str(cToFConversion(hops['temp'])) + '"}'
        indx = indx + 1

    # Boil Time
    hours = int(batch['recipe']['equipment']['boilTime'] / 60)
    minutes = batch['recipe']['equipment']['boilTime'] % int(60)
    if minutes < 10:
        data = data + ', {"Name":"Boil Time","Value":"0' + str(hours) + ':0' + str(minutes) +':00"}'
    else:
        data = data + ', {"Name":"Boil Time","Value":"0' + str(hours) + ':' + str(minutes) +':00"}' 

    # Target pre-boil volume
    #print( json.dumps(batch, indent=2) )
    boilVol = batch['recipe']['boilSize'] * lToGalConversion # Liters -> Gallons
    print( boilVol )
    data = data + ', {"Name":"Preboil Volume","Value":"' + str(boilVol) + '"}'

    # Water Strike Temp
    #print( json.dumps(batch, indent=2) )
    recipeStrikeTemp = batch['recipe']['data']['strikeTemp']
    if recipeStrikeTemp is not None:
        strikeTemp =  cToFConversion(batch['recipe']['data']['strikeTemp']) # C -> F
        data = data + ', {"Name":"Strike Water Temp","Value":"' + str(strikeTemp) + '"}'

    # Mash water volume
    #print( json.dumps(batch, indent=2) )
    strikeVol =  batch['recipe']['data']['mashWaterAmount'] * lToGalConversion # Liters -> Gallons
    data = data + ', {"Name":"Strike Water Volume","Value":"' + str(strikeVol) + '"}'

    # Sparge water volume
    #print( json.dumps(batch, indent=2) )
    spargeVol =  batch['recipe']['data']['spargeWaterAmount'] * lToGalConversion # Liters -> Gallons
    data = data + ', {"Name":"Sparge Volume","Value":"' + str(spargeVol) + '"}'

    data = data + ']'
    headers = {"Content-Type": "application/json"}
    response = requests.put('http://localhost:8000/globals', data=data, headers=headers)
    if response.status_code != 200:
        print('Failed to put batch data to BruControl.')
        print( data )    

def refresh():
    for btn in button_list:
        btn.destroy()

    response = requests.get('https://api.brewfather.app/v2/batches', auth=auth)
    if response.status_code != 200:
        print('Failed to obtain batch list.')

    batches = response.json()
    for batch in batches:
        if batch['status'] == 'Planning' or batch['status'] == 'Brewing':
            button = ttk.Button(frame, text = batch['name'] + " " + str(batch['batchNo']) + ", " + batch['recipe']['name'], command = lambda v = batch['_id']: getBatch(v) )
            button.pack(pady=5)
            button_list.append( button )

# MAIN ########################################################################
root = Tk()
root.title('BruFather')
root.tk.call("source", "azure.tcl")
root.tk.call("set_theme", "dark")
root.geometry("320x400")
frame = Frame(root)
frame.pack(pady=5)

button = ttk.Button(frame, text = 'Refresh List', command = refresh )
button.pack(pady=5)

button_list = []

refresh()

root.mainloop()