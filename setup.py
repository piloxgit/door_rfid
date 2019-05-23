import paho.mqtt.client as mqtt
import json
import sqlite3
import time

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("kolarna")
    client.subscribe("hlavni")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

'''def save_user(chip_number, name, surname):

    conn = sqlite3.connect('rfid.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO users VALUES (?, ?, ?)', (chip_number, name, surname))
    conn.commit()

    conn.close()'''

def save_to_db(sql):

    conn = sqlite3.connect('rfid.db')
    cur = conn.cursor()

    door_id =4
    chip_number = 89898
    time = 999
    date =8888
    cur.execute(sql)
   # cur.execute('INSERT INTO log VALUES (?, ?, ?, ?)', ("1", "33", "sdfsdf", "sdf"))
    #cur.execute('INSERT INTO log VALUES (?, ?, ?, ?)', (door_id, chip_number, time, date))
    conn.commit()

    conn.close()

# The callback for when a PUBLISH message is received from the server.

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

client.connect("192.168.254.223", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()