import os
import sys
import time

def init():
    fileName = 'log.py'
    this_dir = os.path.abspath(os.path.dirname(__file__))
    filePath = (this_dir + '/' + fileName)

    for x in range(4):
        os.system('python3 {}'.format(filePath))
        time.sleep(1)

if __name__ == "__main__": init()
