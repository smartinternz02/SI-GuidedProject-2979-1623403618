import requests
import ibmiotf.application
import ibmiotf.device
import random
import json
import time
import os
import json

#Provide your IBM Watson Device Credentials
organization = "y0d2ux"
deviceType = "iotdevice"
deviceId = "1001"
authMethod = "token"
authToken = "1234567890"


# Initialize the device client.
T=0
H=0
RF=0

def myCommandCallback(cmd):
        print("Command received: %s" % cmd.data['command'])


        if cmd.data['command']=='motoron':
                print("Starting The System To Water The Field...")
               
               
        elif cmd.data['command']=='motoroff':
                print("Shutdown The Watering System...")
                

       
        if cmd.command == "setInterval":
                if 'interval' not in cmd.data:
                        print("Error - command is missing required information: 'interval'")
                else:
                        interval = cmd.data['interval']
        elif cmd.command == "print":
                if 'message' not in cmd.data:
                        print("Error - command is missing required information: 'message'")
                else:
                        print(cmd.data['message'])


def crop(P, K, N, humidity, temperature, ph, rainfall):

    f = open('main.json')

    data = json.load(f)
    
    try:
        for i in range(2200):
            data[i]['humidity'] = round(data[i]['humidity'])
            data[i]['temperature'] = round(data[i]['temperature'])
            data[i]['ph'] = round(data[i]['ph'])
            data[i]['rainfall'] = round(data[i]['rainfall'])
            # print(i, data[i])
            if(data[i]['P'] == P and data[i]['K'] == K and data[i]['N'] == N):
                if(data[i]['humidity'] == round(humidity) and data[i]['temperature'] == round(temperature) and data[i]['ph'] == round(ph) and data[i]['rainfall'] == round(rainfall)):
                    return data[i]['label']
        # else:
        #     print("No Matching Data Found...For the given Values")
    except:
        pass

try:
 deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
 deviceCli = ibmiotf.device.Client(deviceOptions)
#..............................................

except Exception as e:
 print("Caught exception connecting device: %s" % str(e))
 os.sys.exit()

# Connect and send a datapoint "hello" with value "world" into the cloud as an event of type "greeting" 10 times
deviceCli.connect()

while True:
        r = requests.get('https://api.openweathermap.org/data/2.5/weather?q=Vijayawada,IN&appid=d9743d5e16a053fa0ca2506cfd91b858')
        data = r.json()
        TAPI = round(data['main']['temp'] - 273.15)
        HAPI = round(data['main']['humidity'])
        PAPI = round(data['main']['pressure'])

        T=25      #Temperature.
        H=82      #Humidity.
        N=99      #Nitrogen.
        P=57      #Phosphorous.
        K=38      #Potassium.
        PH=6      #Ph Value.
        M=54      #Moisture per Millimeters(mm).
        RF=156    #Rainfall per Millimeters(mm).


        RC = crop(P, K, N, H, T, PH, RF)
        #Send Temperature & Humidity to IBM Watson
        data = {"d":{ 'temperature' : T, 'humidity': H, 'nitrogen': N, 'phosphorous': P, 'potassium': K, 'ph': PH, 'moisture': M, 'rainfall': RF,'temperature_API' : TAPI, 'humidity_API': HAPI, 'pressure_API': PAPI, 'Recommended_Crop': RC}}
        #print (data)
        def myOnPublishCallback():
                print ("Published Temperature = %s C" % T, "Humidity = %s %%" % H, "Nitrogen = %s" % N, "Phosphorous = %s" % P, "Potassium = %s" % K, "ph = %s" % PH, "Moisture = %s mm" % M, "Rainfall = %s" % RF,  "Temperature_API = %s C" % TAPI, "Humidity_API = %s %%" % HAPI, "Pressure_API = %s" % PAPI, "Recommended Crop = %s" % RC,"to IBM Watson")

        success = deviceCli.publishEvent("Data", "json", data, qos=0, on_publish=myOnPublishCallback)
        if not success:
                print("Not connected to IoTF")
        time.sleep(1)


        deviceCli.commandCallback = myCommandCallback

# Disconnect the device and application from the cloud
deviceCli.disconnect()
