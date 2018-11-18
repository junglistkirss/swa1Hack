import time
import network
from utils import get_machine_guid

AUTHMODE = {0: "open", 1: "WEP", 2: "WPA-PSK", 3: "WPA2-PSK", 4: "WPA/WPA2-PSK"}

GUID = get_machine_guid()

# new wifi network
AP = network.WLAN(network.AP_IF)
AP.active(True)
AP.config(essid='WiFi_%s' % GUID, password='swa1%s' % GUID, authmode=3)

# local wifi network
STA = network.WLAN(network.STA_IF)
STA.active(True)


def do_connect(ssid, password):
    STA.active(True)
    if STA.isconnected():
        STA.disconnect()
    print('Trying to connect to %s...' % ssid)
    STA.connect(ssid, password)
    for retry in range(100):
        connected = STA.isconnected()
        if connected:
            break
        time.sleep(0.1)
        print('.')
    if connected:
        print('\nConnected. Network config: ', STA.ifconfig())
    else:
        print('\nFailed. Not Connected to: ' + ssid)
        STA.disconnect()
        STA.connect('', '')
        STA.active(False)
    return connected


def IP():
    return (STA.ifconfig(), AP.ifconfig())
