import requests
from requests.auth import HTTPBasicAuth
import datetime
import _tkinter
import tkinter
from tkinter import *
from tkinter import ttk

fermenterTemp = 0
fermenterPressure = 0
garageTemp = 0
iSpindelBlue = 0

def pushData():
    
    r = requests.get('http://localhost:8000/global/Fermenter%20Temp%20Global')
    if r.status_code != 200:
        print( "Error response from BruControl " + str(r.status_code) )
    else:
        fermenterTemp = r.json()['Value']

    r = requests.get('http://localhost:8000/global/Garage%20Temp%20Global')
    if r.status_code != 200:
        print( "Error response from BruControl " + str(r.status_code) )
    else:
        garageTemp = r.json()['Value']

    r = requests.get('http://localhost:8000/global/iSpindel000_g')
    if r.status_code != 200:
        print( "Error response from BruControl " + str(r.status_code) )
    else:
        iSpindelBlue = r.json()['Value']
    
    r = requests.get('http://localhost:8000/global/Fermenter%20Pressure%20Global')
    if r.status_code != 200:
        print( "Error response from BruControl " + str(r.status_code) )
    else:
        fermenterPressure = r.json()['Value']


    print("Time: ", datetime.datetime.now()) 
    print("Fermenter temp", fermenterTemp) 
    print("Garage ", garageTemp) 
    print("iSpindel ", iSpindelBlue) 
    print("Fermenter pressure ", fermenterPressure) 

    data = {}
    data['name'] = 'Fermenter'
    data['temp'] = fermenterTemp
    data['ext_temp'] = garageTemp
    data['temp_unit'] = 'F'
    data['gravity'] = iSpindelBlue
    data['gravity_unit'] = "G" #SpGr
    data['pressure'] = fermenterPressure
    data['pressure_unit'] = "PSI"
    # data['ph'] = 0.0
    # data['comment'] = ""
    # data['beer'] = ""
    # Replace stream id with brewfather provided custom stream id for account
    r = requests.post('http://log.brewfather.net/stream?id=NYZVUthXDqWxwX', json=data)
    if r.status_code != 200:
        print( "Error response from Brewfather " + str(r.status_code) )

    root.after(900000, pushData)

# MAIN ########################################################################
root = Tk()
root.title('BruDevice')
root.tk.call("source", "azure.tcl")
root.tk.call("set_theme", "dark")
root.geometry("320x320")
frame = Frame(root)
frame.pack(pady=5)

pushData()

root.mainloop()