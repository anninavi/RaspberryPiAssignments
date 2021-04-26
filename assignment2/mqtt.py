import time
import ttn
import json
from base64 import b64decode,b64encode
from datetime import datetime,timezone
import requests
import struct


# --- TTN VARIABLES --------------------------
app_id = "lr1110_tracking"
access_key = "ttn-account-v2.TuVkiEtlXdJhXZMuER2YGqNqIUZc0QIewLHk5avvPxs"

def uplink_callback(data, client):
    print("Received uplink from ", data.dev_id)

    if(data is None):
        print("Empty Payload")
        return

    # print(data);
    print("Raw Payload: {}".format(data.payload_raw))
    # print("metadata: {}".format (data.metadata))
    print("modulation: {}".format(data.metadata.modulation))
    print("airtime: {} ms".format(data.metadata.airtime/pow(10,6)))
    print("data_rate: {}".format(data.metadata.data_rate))
    print("Number of GW's: {}".format(len(data.metadata.gateways)))
    for i in range(len(data.metadata.gateways)):
        print("{}th rssi: {}".format (i,data.metadata.gateways[i].rssi))
    print("")

# create ttn connection
handler = ttn.HandlerClient(app_id, access_key)
# use mqtt client
mqtt_client = handler.data()
mqtt_client.set_uplink_callback(uplink_callback)
mqtt_client.connect()
time.sleep(60000)
mqtt_client.close()