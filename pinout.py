# // Blue LED: GPIO4
# // Button: GPIO13
# // Extra Pin: GPIO14
# // Red LED + Relay: GPIO5

from machine import Pin, PWM
from utime import ticks_ms, ticks_diff

BLUE = Pin(4, Pin.OUT)
RELAY = Pin(5, Pin.OUT)
BTN = Pin(13, Pin.IN, Pin.PULL_UP)


class EventHandler:

    def __init__(self, btn):
        self._b = btn
        self._b.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.validate)
        self._handlers = list()
        self._t = None

    def add(self, value):
        self._handlers.append(value)

    def validate(self, p):
        if self._b.value() == Pin.IN:
            self._t = ticks_ms()
        if self._b.value() == Pin.OUT and self._t is not None:
            d = ticks_diff(ticks_ms(), self._t)
            self._t = None
            for handle in self._handlers:
                handle(d)


class PWM_LED:

    def __init__(self, pin, frequency=1):
        self._pwm = PWM(pin)
        self.blink(frequency)

    def stop(self):
        self.lum(1023)
        # self.blink(0)

    def lum(self, value):
        self._pwm.duty(max(0, min(value, 1023)))

    def blink(self, value):
        self._pwm.freq(max(0, min(value, 1000)))
