import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        if GPIO.input(18):
            print('There is water')
        else:
            print('No water')
        time.sleep(3)
except KeyboardInterrupt:
    pass
