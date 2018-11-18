import machine
from machine import Timer
from utime import sleep
# from utime import sleep_ms, sleep
from pinout import PWM_LED, BLUE, RELAY, BTN, EventHandler
# from utils import read_json, write_json, get_machine_guid
from wifi import do_connect
from wifi import STA, AP
from ubinascii import hexlify
from uServerBase import uWebServer

blue_led = PWM_LED(BLUE, 4)
blue_led.lum(400)

RELAY.off()

sleep(5)

if STA.isconnected():
    blue_led.lum(800)
    sleep(2)
else:
    # STA.active(False)
    blue_led.lum(1)
    sleep(5)

blue_led.stop()


def _reset_credentials(t):
    STA.connect('', '')
    STA.disconnect()
    machine.reset()


def click(d):
    if d > 5000:
        machine.reset()
    elif d > 10000:
        reboot = Timer(-1)
        reboot.init(period=2000, mode=Timer.ONE_SHOT, callback=_reset_credentials)
    else:
        if RELAY.value() == 0:
            RELAY.on()
        else:
            RELAY.off()


BTN__OnClick = EventHandler(BTN)
# BTN__OnClick.add(debug)
BTN__OnClick.add(click)


def _handle_reset(httpClient, httpResponse):
    httpResponse.WriteResponseJSONOk(headers=None, obj={'reset': True})
    machine.reset()


def _handle_reset_credentials(httpClient, httpResponse):
    httpResponse.WriteResponseJSONOk(headers=None, obj={'_reset_credentials': True})
    reboot = Timer(-1)
    reboot.init(period=2000, mode=Timer.ONE_SHOT, callback=_reset_credentials)


def _handle_wifiscan(httpClient, httpResponse):
    result = [{'ssid': ssid, 'bssid': hexlify(bssid), 'channel': channel, 'RSSI': RSSI, 'authmode': authmode, 'hidden': hidden} for (ssid, bssid, channel, RSSI, authmode, hidden) in STA.scan()]
    httpResponse.WriteResponseJSONOk(headers=None, obj=result)


def _parse_ifconfig(ip, subnet, gateway, dns):
    return {'ip': ip, 'subnet': subnet, 'gateway': gateway, 'dns': dns}


def _handle_ifconfig(httpClient, httpResponse):
    ap_ip, ap_subnet, ap_gateway, ap_dns = AP.ifconfig()
    sta_ip, sta_subnet, sta_gateway, sta_dns = STA.ifconfig()
    result = {'AP': _parse_ifconfig(ap_ip, ap_subnet, ap_gateway, ap_dns),
              'STA': _parse_ifconfig(sta_ip, sta_subnet, sta_gateway, sta_dns)}
    httpResponse.WriteResponseJSONOk(headers=None, obj=result)


def _handle_relay_status(httpClient, httpResponse, routeArgs=None):
    if routeArgs is not None:
        try:
            st = routeArgs['status']
            if st == 'on':
                RELAY.on()
            elif st == 'off':
                RELAY.off()
        except Exception as e:
            httpResponse.WriteResponseJSONError(headers=None, code=500, obj={'message': e.message})
    status = {'state': RELAY.value()}
    httpResponse.WriteResponseJSONOk(headers=None, obj=status)

_generic_page = """
<!DOCTYPE html>
<html>
    <head>
        <title>%(title)s</title>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" type="text/css" href="style.css" />
    </head>
    <body>
        %(content)s
    </body>
</html>
"""


def _handle_generic(httpClient, httpResponse, routeArgs=None):
    title = "index"
    inner = 'No page content'
    if routeArgs is not None:
        if 'page' in routeArgs:
            title = routeArgs['page']
    content = _generic_page % {'title': title, 'content': inner or 'No generic content'}
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=content)


def _handle_get_wifi(httpClient, httpResponse):
    status = STA.isconnected()
    content = """
    <h1><a href='wifi'> Wifi</a></h1>
    <h2>Connection : %(status)s</h2>
    <form method="POST" action="/wifi">
        <label for="login">Login</label>
        <input type="TEXT" name="login"/>
        <label for="passwd">Password</label>
        <input type="PASSWORD" name="passwd"/>
        <button type="submit">Connect wifi</button>
    </form>
    """ % {'status': 'Oui' if status else 'Non'}
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=_generic_page % {'title': 'WiFi', 'content': content})


def _handle_post_wifi(httpClient, httpResponse):
    datas = httpClient.ReadRequestPostedFormData()
    if 'passwd' in datas and 'login' in datas:
        do_connect(datas['login'], datas['passwd'])
    _handle_get_wifi(httpClient, httpResponse)

mws = uWebServer(routeHandlers=[
                 # JSON responses
                 ('/set/<status>', 'GET', _handle_relay_status),
                 ('/set', 'GET', _handle_relay_status),
                 ('/get', 'GET', _handle_relay_status),
                 ('/scan', 'GET', _handle_wifiscan),
                 ('/ifconfig', 'GET', _handle_ifconfig),
                 ('/reset', 'GET', _handle_reset),
                 ('/reset_credentials', 'GET', _handle_reset_credentials),
                 # ('/reset_credentials', 'GET', _handle_reset_credentials),
                 # ('/ap_state', 'GET', _handle_ifconfig),
                 # ('/ap_enable', 'GET', _handle_ifconfig),
                 # ('/ap_disable', 'GET', _handle_ifconfig),
                 # HTMH responses
                 ('/wifi', 'GET', _handle_get_wifi),
                 ('/wifi', 'POST', _handle_post_wifi),
                 ('/<page>', 'GET', _handle_generic),
                 ('', 'GET', _handle_generic)
                 ],
                 port=80,
                 bindIP='0.0.0.0',  # '192.168.1.23'
                 webPath='/www')
mws.Start()
