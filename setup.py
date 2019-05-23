import paho.mqtt.client as mqtt
import json
import sqlite3
import time
from sqlalchemy import *

def create_tables():
    db = create_engine('sqlite:///door_rfid.sqlite')
    db.echo = False
    metadata = MetaData(db)

    users = Table('users', metadata,
                  Column('chip_id', Integer, primary_key=True),
                  Column('name', String(40)),
                  Column('surname', String(40)),
                  )

    doors = Table('doors', metadata,
                 Column('door_id', Integer),
                 Column('door_name', String(10)),
                 )

    boot = Table('boot', metadata,
                 Column('door_id', Integer),
                 Column('time', String(8)),
                 Column('date', String(10)),
                 )

    heartbeat = Table('heartbeat', metadata,
                 Column('door_id', Integer),
                 Column('time', String(8)),
                 Column('date', String(10)),
                 )

    accesslog = Table('accesslog', metadata,
                      Column('chip_id', Integer),
                      Column('door_id', Integer),
                      Column('time', String(8)),
                      Column('date', String(10)),
                      )

    metadata.create_all(db)

def set_intro_data():
    pass

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("kolarna")
    client.subscribe("hlavni")

def on_message(client, userdata, msg):

    message = msg.payload.decode("UTF_8")
    jmessage = json.loads(message)


    if msg.topic == "kolarna":
        door_id = 1
    if msg.topic == "hlavni":
        door_id = 2

    time_now = time.strftime("%H:%M:%S", time.localtime())
    date_now = time.strftime("%m.%d.%Y", time.localtime())

    conn = sqlite3.connect('rfid.db')
    cur = conn.cursor()


    if jmessage["type"] == "access":
        cur.execute('INSERT INTO log VALUES (?, ?, ?, ?)', (door_id, jmessage["uid"], time_now, date_now))
        print("Access, ", jmessage["username"], ", " ,door_id, ", ", time_now, ", ", date_now)
    if jmessage["type"] == "boot":
        cur.execute('INSERT INTO boot VALUES (?, ?, ?)', (door_id, time_now, date_now))
        print("Boot, ", door_id, ", ", time_now, ", ", date_now)
    if jmessage["type"] == "heartbeat":
        cur.execute('INSERT INTO heartbeat VALUES (?, ?, ?)', (door_id, time_now, date_now))
        print("Heartbeat, " ,door_id,", ",time_now,", ",date_now)
    conn.commit()
    conn.close()


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.1.50", 1883, 60)






create_tables()
client.loop_forever()

