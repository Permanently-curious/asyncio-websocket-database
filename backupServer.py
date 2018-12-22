#!/usr/bin/env python

# WS server example that synchronizes state across clients

#webserver modules
import asyncio
import json
import logging
import websockets
import time

#database modules
import sqlite3 as lite
import sys

#variabler
enheder = 0
alarmType = 0

unitLatitude = 0
unitLongitude = 0


#encoding
# -*- coding: utf-8 -*-
#https://stackoverflow.com/questions/4872007/where-does-this-come-from-coding-utf-8
#but doesn"t seem to be needed

# #connect to database as con
# #con = lite.connect("database.db")
# units = 0
# alarmflag = 0
#
#init: creates a table in the database called units
# if allready made prints it

#init:




    
#start up connection --------------------
try:
    con = lite.connect("test.db") #Connect to database, create if absent

    cur = con.cursor() #Points to the current selected row(s)

    #Creates a table, and if it already exits throws an error message
    cur.executescript("""
        CREATE TABLE Units(
        Number INT,
        Id INT,
        Type TEXT,
        Name TEXT,
        Latitude INT,
        Longitude INT);
        """)

    con.commit() #The table is added to the test.db file

#Error handling
except lite.Error as e:

    print ("Error %s:" % e.args[0])
    

def updateUnitNumber():
    #startup check tables --------------------
    with con:
        try:
            cur = con.cursor() #Points to the current selected row(s)
            cur.execute("SELECT * FROM Units")
            rows = cur.fetchall()
            i = 0
            global enheder
            
            #set enheder to the existing rows
            try:
                for row in rows:
                    i += 1

                
                enheder = i
                print("%s rows exists" %i)
            except lite.Error as e:
                print ("Error %s:" % e.args[0])

        #Error handling #
        except lite.Error as e:

            print ("Error %s:" % e.args[0])


#Fills the database with test stuff
def printTable():
    
    with con:
        con.row_factory = lite.Row
        cur = con.cursor()


        cur.execute("SELECT * FROM Units ORDER BY Id ASC")

        rows = [dict(row) for row in cur.fetchall()]

        for row in rows:
            print (row)

def test():
    
    with con:
        con.row_factory = lite.Row
        cur = con.cursor()

        try:
            cur.execute("INSERT INTO Units VALUES(04, 5432, 'ControlEnhed', 'Pav', 52642, 10000)")
            cur.execute("INSERT INTO Units VALUES(02, 1234, 'ControlEnhed', 'Pav', 52642, 10000)")
            cur.execute("INSERT INTO Units VALUES(03, 5432, 'ControlEnhed', 'Pav', 52642, 10000)")
        except lite.Error as e:
            #if con:
            #    con.rollback()

            print ("Error %s:" % e.args[0])

        cur.execute("SELECT * FROM Units ORDER BY Id ASC")

        rows = [dict(row) for row in cur.fetchall()]

        for row in rows:
            print (row)
            

def createList():
    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        try:
            cur.execute("SELECT * FROM Units ORDER BY Id ASC")
            rows = [dict(row) for row in cur.fetchall()]
            print("Creating list:")

            for row in rows:
                print (row)
                
        except lite.Error as e:

            #if con:
            #    con.rollback()

            print ("Error %s:" % e.args[0])
                
        return rows



def checkId(ID):
    cur = con.cursor()
    cur.execute("SELECT * FROM Units WHERE Id=?", (ID,))
    rows = cur.fetchall()
    if rows:
        return True
    else:
        return False

#def alarmSwitcher(alarmType):
#    alarmString = {
#        1:  "alarm",
#        2:  "batteri",
#        3:  "check"
#    }
#    print (alarmType)
#    return alarmSwitcher.get(alarmType, "invalid alarm type")

def sendAlarm(ID):
    
    
    
    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        
        try:
            cur.execute("SELECT * FROM Units WHERE Id=?", (ID,))
            rows = [dict(row) for row in cur.fetchall()]
            print("Alarm type message")
            
            
            if (rows):
                print("ID eksisterer")
                enheder = rows[0]["Number"]
                print("Location check =",(rows[0]["Latitude"],rows[0]["Longitude"]))
                #global unitLatitude
                #global unitLongitude
                unitLatitude = rows[0]["Latitude"]
                unitLongitude = rows[0]["Longitude"]
                
                #result = notify_alarm(message)
                
                #notify_alarm()
                
            else:
                print("ID eksisterer ikke")
                print(ID)
                print("send unkendt id alarm")
                return 0
                
        except lite.Error as e:

            print ("Error %s:" % e.args[0])
    
        
    

def checkMessage(alarmType,ID):
    print("Checking message")
    if (alarmType == 1):
        sendAlarm(ID)
        
    elif (alamType == 2):
        sendBattery(ID)
        
    elif (alamType == 3):
        sendCheck(ID)
        
            
    

def compareUnit(ID): 
    
    cur = con.cursor()
    cur.execute("SELECT * FROM Units WHERE Id=?", (ID,))
    rows = cur.fetchone()
    
    #hent alarmtypen
    
    if (rows):
        print("correct ID tjekket")
        print(row)
        global unitLatitude
        global unitLongitude
        unitLatitude = row["latitude"]
        unitLongitude = row["longitude"]
        return 1
    else:
        print("forkert ID tjekket")
        print(ID)
        return 0
    
    
    

def deleteId(ID):
    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        
        try:
            cur.execute("SELECT * FROM Units WHERE Id=?", (ID,))
            rows = [dict(row) for row in cur.fetchall()]
            
            global enheder
            enheder = rows[0]["Number"]
            cur.execute("DELETE FROM Units WHERE Id=?", (ID,))
            print("Deleting units")
            
        except lite.Error as e:

            print ("Error %s:" % e.args[0])
            
    #if rows:
        #global enheder
        #enheder = row["Number"]
        #print(rows[])
        #cur.execute("DELETE FROM Units WHERE Id=?", (ID,))
        #print("Deleting units")


def createDevice(ID, ControlUnit=False, name="No Name", longitude ="0000", latitude ="0000"):
    print("make device")
    updateUnitNumber()
    if (ControlUnit):
        makeControlUnit(ID, name, longitude, latitude)
    else:
        makeUnit(ID, name, longitude, latitude)


def makeControlUnit(ID, name, longitude, latitude):
    if checkId(ID):
        deleteId(ID)
    
    
    #localString = "01, " + ID + name + longitude + latitude
    cur.execute("SELECT * FROM Units")
    li= (enheder, ID, 'ControlEnhed' , str(name), longitude, latitude)
    print("making ControlUnit")

    try:
        cur.execute('''INSERT INTO Units VALUES(?,?,?,?,?,?)''',(li[0],li[1],li[2],li[3],li[4],li[5]))
        #cur.execute('''INSERT INTO Units VALUES(01, ?, "ControlEnhed" , ?, ?, ?)''', (ID, name, longitude, latitude))

    except lite.Error as e:

        #if con:
        #    con.rollback()

        print ("Error %s:" % e.args[0])


def makeUnit(ID, name, longitude, latitude):
    if checkId(ID):
        deleteId(ID)
    
    
    global enheder
    print("making unit")
    #localString = "{0}, {1},".format(enheder, ID) + "DetektorEnhed, " + name + ", " + "{0}, {1}".format(longitude, latitude)
    #localString = str("'''")+ "INSERT INTO Units VALUES(" + localString + str(")'''")
    #print(localString)
    #localString = "01, " + str(ID) + str(name) + str(longitude) + str(latitude)
    li= (enheder, ID, 'DetektorEnhed' , str(name), longitude, latitude)
    
    
    cur.execute("SELECT * FROM Units")
    rows = cur.fetchall()
    
    try:
        cur.execute('''INSERT INTO Units VALUES(?,?,?,?,?,?)''',(li[0],li[1],li[2],li[3],li[4],li[5]))
        
    except lite.Error as e:
    
        #if con:
        #    con.rollback()
        
        print ("Error %s:" % e.args[0])


## MESSAGES

def alarmMessage(row):
    
    return 0
    
    
    

#with con:

#    cur = con.cursor()
#    cur.execute("CREATE TABLE Units (Id INT, Name TEXT, Latitude INT, longitude INT)")
    #cur.execute("INSERT INTO Area1 VALUES(1,"unit",10,20)")

#--------------------------------------------------#
#--------------WEBSOCKET SERVER--------------------#
#Event based program where unrelated tasks can be executed while await is called. 

logging.basicConfig()

STATE = {"value": 0}

USERS = set()

#-----------------Event functions -----------------#

def alarm_event():

    return json.dumps({"type": "alarm","latitude": unitLatitude, "longitude": unitLongitude})

def state_event():
    return json.dumps({"type": "state", **STATE})

#User event when another users connects to the server
def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})

#When a user connects an update of data is send in json format
def info_event():
    #cur = con.cursor()
    #cur.execute("SELECT * FROM Units")
    #rows = cur.fetchall()

    rows = createList()
    return json.dumps({"type": "info", "detectors": rows})

#-----------------Notify functions--------------------#

async def notify_state():
    if USERS:       # asyncio.wait doesn"t accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])
        
async def notify_alarm():
    if USERS:       # asyncio.wait doesn"t accept an empty list
        message = alarm_event()
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
async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)

    try:
        #Send updated information after connection register
        await notify_info()
        
        #Asyncron for-loop to handle messages fra client to websocket
        async for message in websocket:
        #await websocket.send(state_event())
            #the data received is loaded in json format
            data = json.loads(message)
            #Checks if the message received is a new device
            if data["action"] == "new_device":
                print("new device received")
                createDevice(data["deviceid"],0,"no name yet",data["longitude"],data["latitude"])
                
                
                print(data)
                #Needs to call a create unit function
            else:
                logging.error(
                "unsupported event: {}", data)
        #
        #     data = json.loads(message)
        #     if data["action"] == "info":
        #         print("Info request received")
        #         await notify_info()
        #
        #     elif data["action"] == "off":
        #         #Stop sending the alarm
        #         print("Turn off the alarm")
        #         alarmflag = 0
        #
            #
    finally:
        await unregister(websocket)

#---------Main initalization of the event driven system-----#

#Get the current event loop and run until the service is done
asyncio.get_event_loop().run_until_complete(
    websockets.serve(counter, "localhost", 6789))

#Initiation
createDevice(000,0)
createDevice(111,0,"bob",123,1234)
createDevice(112)
updateUnitNumber()
printTable()
checkMessage(1,111)


#The server keeps running ready for new users
asyncio.get_event_loop().run_forever()

#def main():
    #while True:
        
        
        
        
        #loop = asyncio.new_event_loop()
        #asyncio.set_event_loop(loop)
        #result = loop.run_until_complete
        #asyncio.get_event_loop().run_until_complete()
        
    
    
