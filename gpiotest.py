import RPi.GPIO as gpio
import time


gpio.setmode(gpio.BOARD)

gpio.setup(3, gpio.OUT,initial=1)
gpio.setup(5, gpio.OUT,initial=1)
gpio.setup(7, gpio.OUT,initial=1)
gpio.setup(8, gpio.OUT,initial=1)

def turnOn(pin):
    gpio.output(pin,0)
    time.sleep(0.3)
    gpio.output(pin,1)
    print('set on: %s'%pin)
