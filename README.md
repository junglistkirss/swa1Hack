# swa1Hack
Reprogrammation d'une prise de type "swa1", en micropython.

# Liens
http://docs.micropython.org/en/v1.9.2/esp8266/index.html
https://hackaday.io/project/21243/instructions
https://majenko.co.uk/blog/hacking-swa1-smart-wifi-power-switch
https://github.com/espressif/esptool/
https://learn.adafruit.com/micropython-basics-load-files-and-run-code/overview

# Branchements

Le daétail des pins est visible dans les liens
A droite l'adaptateur et à gauche le swa1
DTR ==> None
RXD ==> TX
TXD ==> RX
5V  ==> 5V
CTS ==> None
GND ==> GND + GPIO0

# Installation

On utilise ici un convertisseur USB tio UART, pour interagir en série avec la carte
installer le driver de l'USB to UART ==> ici ; Silicon Labs CP210x...

esptool est requis pour flasher la carte (ici un ESP8266EX)
pip install esptool

esptool.py --port COM35 --baud 460800 erase_flash
esptool.py --port COM35 --baud 460800 write_flash --flash_mode dout --flash_size 2MB 0 .\esp8266-20181116-v1.9.4-684-g51482ba92.bin

# WEB Repl
import webrepl_setup


# Ampy (cf liens)

import esp
esp.osdebug(None)


ampy --port COM35 run [...].py
ampy --port COM35 put [...].py [rename].py

ampy --port COM35 get [...].py
ampy --port COM35 get [...].py [rename].py

ampy --port /serial/port mkdir /foo/bar
ampy --port /serial/port ls
