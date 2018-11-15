# // Button: GPIO13
# // Blue LED: GPIO4
# // Red LED + Relay: GPIO5
# // Extra Pin: GPIO14

from machine import Pin

# from machine import PWM
# BLUE = PWM(4)

BLUE = Pin(4, Pin.OUT)
RELAY = Pin(5, Pin.OUT)
BTN = Pin(13)


def button_falling(p):
    pass


def button_rising(p):
    pass

BTN.irq(trigger=Pin.IRQ_FALLING, handler=button_falling)
BTN.irq(trigger=Pin.IRQ_RISING, handler=button_rising)
