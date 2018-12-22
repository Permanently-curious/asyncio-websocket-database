#!/usr/bin/env python


#Made by Pav 
#
#Inspired by:
#
#
# https://websockets.readthedocs.io/en/stable/intro.html?fbclid=IwAR2_W-njALpBXEb0rBbuJm569C817E4_gf0R2p2ewJVhWPwXQGQNAevW7cM
#   - WS server example with synchronization of state
#  
# http://zetcode.com/db/sqlitepythontutorial/
#   - SQL
#

#webserver modules
import asyncio
import json
import logging
import websockets
#import time
import time
from time import gmtime, strftime
import datetime

#database modules
import sqlite3 as lite
import sys

#variabler
enheder = 0
alarmType = 0

#unit variabler til alarm
unitId = 0
unitLatitude = 0
unitLongitude = 0

#variables to message handling from detektion unit
alarmFlag = 0
alarmMessage= "no string"
alarmCall = 0
idCall = 0
#
timeStampFlag = 0
    
#start up connection --------------------#
try:
    con = lite.connect("test.db") #Connect to database, create if absent

    cur = con.cursor() #Points to the current selected row(s)

    #Creates a table, and if it already exists throws an error message
    cur.executescript("""
        CREATE TABLE Units(
        Number INT,
        Id INT,
        Type TEXT,
        Name TEXT,
        Latitude INT,
        Longitude INT,
        Timestamp TEXT);
        """)
    con.commit() #The table is added to the test.db file
    
#Error handling
except lite.Error as e:

    print ("Error %s:" % e.args[0])
#----------------------------------------#


def updateUnitNumber():
    with con:
        try:
            cur = con.cursor() #Points to the current selected row(s)
            cur.execute("SELECT * FROM Units")
            rows = cur.fetchall()
            i = 0
            global enheder #calling enheder global makes sure, it's the global variable that gets changed, which can then be used elsewhere.
            
            try:
                #set enheder to the existing rows
                for row in rows:
                    i += 1
                enheder = i
                print("%s rows exists" %i)
                
            except lite.Error as e:
                print ("Error %s:" % e.args[0])

        #Error handling #
        except lite.Error as e:

            print ("Error %s:" % e.args[0])


#support funktion for maintenance
def printTable():
    
    with con:
        con.row_factory = lite.Row 
        cur = con.cursor()
        cur.execute("SELECT * FROM Units ORDER BY Id ASC")

        rows = [dict(row) for row in cur.fetchall()] #gets all rows as a dictionary inside a list

        for row in rows:
            print (row)


#Fills the database with test stuff
def test():
    
    with con:
        con.row_factory = lite.Row
        cur = con.cursor()

        try:
            cur.execute("INSERT INTO Units VALUES(04, 5432, 'ControlEnhed', 'Pav', 52642, 10000, 00)")
            cur.execute("INSERT INTO Units VALUES(02, 1234, 'ControlEnhed', 'Pav', 52642, 10000, 00)")
            cur.execute("INSERT INTO Units VALUES(03, 5432, 'ControlEnhed', 'Pav', 52642, 10000, 00)")
        except lite.Error as e:
            #if con:
            #    con.rollback()

            print ("Error %s:" % e.args[0])

        cur.execute("SELECT * FROM Units ORDER BY Id ASC")
        rows = [dict(row) for row in cur.fetchall()]

        for row in rows:
            print (row)
            
#creates a list with the entire database inside, for transporting with JSON
def createList():
    with con:
        con.row_factory = lite.Row #uses the .Row lite function to get it in dictionary format
        cur = con.cursor()
        try:
            cur.execute("SELECT * FROM Units ORDER BY Id ASC")#Sorts the database by Id for the user. its nicer
            rows = [dict(row) for row in cur.fetchall()]
            print("Creating list:")
            print(rows)

            for row in rows:
                print (row)
                
        except lite.Error as e:

            #if con:
            #    con.rollback()

            print ("Error %s:" % e.args[0])
                
        return rows


#checks the Id, returns true or false
def checkId(ID):
    cur = con.cursor()
    cur.execute("SELECT * FROM Units WHERE Id=?", (ID,))
    rows = cur.fetchone()
    if rows:
        return True
    else:
        return False


#based on the ID sends out either Alarm with unit's location, or alarm_without_verified_ID with no lokation.
def sendAlarm(ID):
    
    global alarmMessage
    print("Alarm type message")
    if checkId(ID):
        
        with con:
            con.row_factory = lite.Row
            cur = con.cursor()
            
            try:
                cur.execute("SELECT * FROM Units WHERE Id=?", (ID,))
                rows = [dict(row) for row in cur.fetchall()]
                
                print("ID eksisterer")
                enheder = rows[0]["Number"]
                print("Location check =",(rows[0]["Latitude"],rows[0]["Longitude"]))
                global unitId
                global unitLatitude # set the global values for the message
                global unitLongitude # they should all have their own variables
                unitId = rows[0]["Id"]
                unitLatitude = rows[0]["Latitude"]
                unitLongitude = rows[0]["Longitude"]
                alarmMessage = "alarm"
                    
            except lite.Error as e:

                print ("Error %s:" % e.args[0])

    else:
        print("ID eksisterer ikke")
        print(ID)
        alarmMessage = "alarmFake"
        
        unitLatitude = "unknown"
        unitLongitude = "unknown"
    
#sendBattery sends the warning about low batteri, ID checks out
def sendBattery(ID):
    
    global alarmMessage
    print("Battery low type message")
    if checkId(ID):
        with con:
            con.row_factory = lite.Row
            cur = con.cursor()
            
            try:
                cur.execute("SELECT * FROM Units WHERE Id=?", (ID,))
                rows = [dict(row) for row in cur.fetchall()]
                
                print("ID eksisterer")
                enheder = rows[0]["Number"]
                print("Location check =",(rows[0]["Latitude"],rows[0]["Longitude"]))
                global unitId
                global unitLatitude
                global unitLongitude
                unitId = rows[0]["Id"]
                unitLatitude = rows[0]["Latitude"]
                unitLongitude = rows[0]["Longitude"]
                alarmMessage = "battery"
                    
            except lite.Error as e:

                print ("Error %s:" % e.args[0])

    else:
        print("ID eksisterer ikke")
        print(ID)
        alarmMessage = "alarmFake"
        
        unitLatitude = "unknown"
        unitLongitude = "unknown"


#checkMessage decides which alarmfunktion is called to handle the message
def checkMessage(alarmType,ID):
    print("Checking message")
    if (alarmType == 1):
        sendAlarm(ID)
        return 1
        
    elif (alarmType == 2):
        sendBattery(ID)
        return 1
        
    elif (alarmType == 3):
        compareUnit(ID)
        return 1
    else:
        print ("Wrong alarm code")
    return 0
        
# compare unit checks the ID and updates the timeStamp for the ID if found
def compareUnit(ID): 
    
    cur = con.cursor()
    cur.execute("SELECT * FROM Units WHERE Id=?", (ID,))
    rows = cur.fetchone()
    
    #hent alarmtypen
    
    if (rows):
        print("correct ID tjekket")
        print(rows)
        #timeSlice = str(time.time(%H:%M:%S))
        timeSlice = strftime("%d-%m %H:%M:%S", gmtime())
        cur.execute('''UPDATE Units SET Timestamp = ? WHERE Id=?''',(timeSlice,ID))
        
        return 1
    else:
        print("forkert ID tjekket")
        print(ID)
        return 0
    

#deletes the ID row, and puts rows
def deleteId(ID):
    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        
        try:
            cur.execute("SELECT * FROM Units WHERE Id=?", (ID,))
            rows = [dict(row) for row in cur.fetchall()]
            
            global enheder
            enheder = rows[0]["Number"] # sets enheder to current Number, if unit is being overwritten, the unit maintains its number
            cur.execute("DELETE FROM Units WHERE Id=?", (ID,)) #Deletes the unit
            print("Deleting units")
            
        except lite.Error as e:

            print ("Error %s:" % e.args[0])


#creates a unit in the database by default a detektor unit
def createDevice(ID, ControlUnit=False, name="No Name", longitude ="0000", latitude ="0000"):
    print("make device")
    updateUnitNumber()
    if (ControlUnit):
        makeControlUnit(ID, name, longitude, latitude)
    else:
        makeUnit(ID, name, longitude, latitude)

#creates a Controlunit
def makeControlUnit(ID, name, longitude, latitude):
    if checkId(ID):
        deleteId(ID)
    
    cur.execute("SELECT * FROM Units")
    li= (enheder, ID, 'ControlEnhed' , str(name), longitude, latitude)
    print("making ControlUnit")

    try:
        cur.execute('''INSERT INTO Units(Number, Id, Type, Name, Latitude, Longitude) VALUES(?,?,?,?,?,?)''',(li[0],li[1],li[2],li[3],li[4],li[5]))

    except lite.Error as e:

        print ("Error %s:" % e.args[0])

#creates a DetektorEnhed
def makeUnit(ID, name, longitude, latitude):
    if checkId(ID):
        deleteId(ID)
    
    global enheder
    li= (enheder, ID, 'DetektorEnhed' , str(name), longitude, latitude)
    
    cur.execute("SELECT * FROM Units")
    rows = cur.fetchall()
    
    try:
        cur.execute('''INSERT INTO Units(Number, Id, Type, Name, Latitude, Longitude) VALUES(?,?,?,?,?,?)''',(li[0],li[1],li[2],li[3],li[4],li[5]))
        
    except lite.Error as e:
        print ("Error %s:" % e.args[0])
    

def checkLivstegn():
    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM Units ORDER BY Id ASC")
        print("Livstegns check()")
        
        rows = [dict(row) for row in cur.fetchall()]
        #print(timedelta.total_seconds())
        timeSlice = strftime("%d-%m %H:%M:%S", gmtime())
        realTime = time.mktime(datetime.datetime.strptime(timeSlice, "%d-%m %H:%M:%S").timetuple())
        
        global enheder
        enheder = rows[0]["Number"] # sets enheder to current Number, if unit is being overwritten, the unit maintains its number

        for row in rows:
            if(row["Timestamp"]):
                localTime = time.mktime(datetime.datetime.strptime(row["Timestamp"], "%d-%m %H:%M:%S").timetuple())
                print("Enhed ID & time difference:" ,(row["Id"], realTime-localTime))
                if (realTime-(localTime+1800)>0): #1800 because 30 min *60 secs
                    global unitId
                    global alarmMessage
                    global unitLatitude
                    global unitLongitude #sætter enhederne så noLife alarm can be send
                    unitId = row["Id"]
                    unitLatitude = row["Latitude"]
                    unitLongitude = row["Longitude"]
                    alarmMessage = "noLife"
                    
                    print ("Time surpassed")
                    return 1
                else:
                    print ("Time not exceeded")
        return 0

                
                
        


## MESSAGES

#--------------------------------------------------#
#--------------WEBSOCKET SERVER--------------------#
#Event based program where unrelated tasks can be executed while await is called. 

logging.basicConfig()

STATE = {"value": 0}

USERS = set()

#-----------------Event functions -----------------#

def alarm_event():
    print("Sending Alarm")
    return json.dumps({"type": alarmMessage,"latitude":unitLatitude, "longitude":unitLongitude, "id":unitId})


def state_event():
    return json.dumps({"type": "state", **STATE})

#User event when another users connects to the server
def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})

#When a user connects an update of data is send in json format
def info_event():
    rows = createList()
    print("Sending Info")
    return json.dumps({"type": "info", "detectors": rows})

#-----------------Notify functions--------------------#

async def notify_state():
    if USERS:       # asyncio.wait doesn"t accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])
        
async def notify_alarm():
    if USERS:       # asyncio.wait doesn"t accept an empty list
        
        message = alarm_event()
        print(message)
        await asyncio.wait([user.send(message) for user in USERS])

#The information is send to the user with asyncio
async def notify_info():
    if USERS:       # asyncio.wait doesn"t accept an empty list
        message = info_event()
        await asyncio.wait([user.send(message) for user in USERS])

#Other users are notified when more users connect
async def notify_users():
    if USERS:       # asyncio.wait doesn"t accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])

#----------------Websocket connections-----------------#

async def register(websocket):
    USERS.add(websocket)
    await notify_users()

async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()

#---------------Thread to handle incoming messages------#
async def handler(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)

    try:
        #Send updated information after connection register
        await notify_info()
        
        #Asyncron for-loop to handle messages fra client to websocket
        async for message in websocket:
        #await websocket.send(state_event())
            #the data received is loaded from json into python
            data = json.loads(message)
            #Checks if the message received is a new device
            if data["action"] == "new_device":
                print("new device received")
                createDevice(data["deviceid"],0,"no name yet",data["longitude"],data["latitude"])
                print(data)
                print("new device made")
                
            else:
                logging.error(
                "unsupported event: {}", data)

    finally:
        await unregister(websocket)
        #await asyncio.sleep(0)
        

#---------Main initalization of the event driven system-----#

#Get the current event loop and run until the service is done
asyncio.get_event_loop().run_until_complete(
    websockets.serve(handler, "localhost", 6789))

#Initiation
createDevice(111,0,"bob",56.162937,10.203921) #creates ID 111, for testing
printTable()



#
async def handleClients():
    print('Running in server')
    try:
        
        asyncio.get_event_loop().run_forever()
    except:
        print ("Websocket opdateret")
        
    await asyncio.sleep(1)
    print('Explicit context switch to server again')


async def handleMessages():
    
    print('Explicit context to handleMessages') #sleep 3 sec is just for easier debugging
    await asyncio.sleep(2)# sleeps 3 sec, the await sleep call is required but it can be sleep(0) so it doesn't delay.
    print('Implicit context switch back to handleMessages')
    #check om der er spi besked #typeAlarm #ID
    #compare = checkMessage(3,111)
    
    global alarmFlag
    global idCall
    global alarmCall
    #variables that can be recieved from detektion units
    alarmFlag= 1
    alarmCall = 1
    idCall = 111
    debug = 1
    
    if(debug):
        
        #checks 
        if (alarmFlag):
            await notify_info()
        
        #checks 
        if (alarmFlag):
            if (checkMessage(alarmCall,idCall)):
                print ("send this:")
                await notify_alarm()
                alarmFlag= 0
                
        if(checkLivstegn()):
            await notify_alarm()
        

while(1):
    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(handleClients()), ioloop.create_task(handleMessages())]
    wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_tasks)
    #ioloop.close()
    print("Main")
    

#The server keeps running ready for new users
