import os
import sys
import time


def init():
    n = 0
    try:
        while n < 12:
            n += 1
            os.system('python3 /home/pi/GardenPi/main.py')
    except KeyboardInterrupt:
        pass

if __name__ == "__main__": init()
