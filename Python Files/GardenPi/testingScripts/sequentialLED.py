import os
import sys
import requests
import datetime
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

pinRed = 7
pinBlue = 11
pinYellow = 13
pinGreen = 15

def main():
    GPIO.setup(pinRed,GPIO.OUT)
    GPIO.setup(pinBlue,GPIO.OUT)
    GPIO.setup(pinYellow,GPIO.OUT)
    GPIO.setup(pinGreen,GPIO.OUT)

    GPIO.output(pinRed,GPIO.LOW)
    GPIO.output(pinBlue,GPIO.LOW)
    GPIO.output(pinYellow,GPIO.LOW)
    GPIO.output(pinGreen,GPIO.LOW)

    sequential()


def sequential():
    for x in range(12):
        if GPIO.input(pinRed):
            GPIO.output(pinRed,GPIO.LOW)
            GPIO.output(pinBlue,GPIO.HIGH)
        elif GPIO.input(pinBlue):
            GPIO.output(pinBlue,GPIO.LOW)
            GPIO.output(pinYellow,GPIO.HIGH)
        elif GPIO.input(pinYellow):
            GPIO.output(pinYellow,GPIO.LOW)
            GPIO.output(pinGreen,GPIO.HIGH)
        elif GPIO.input(pinGreen):
            GPIO.output(pinGreen,GPIO.LOW)
            GPIO.output(pinRed,GPIO.HIGH)
        else:
            GPIO.output(pinRed,GPIO.HIGH)
        time.sleep(1)
    GPIO.cleanup()


if __name__ == '__main__': main()
