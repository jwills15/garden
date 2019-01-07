import os
import sys
import datetime
import configparser
import time


def init():
    for x in range(20):
        config = configparser.ConfigParser()
        config.read('current.ini')
        current = int(config['CurrentValue']['current'])
        current += 1
        if current > 4:
            current = 1

        config['CurrentValue']['current'] = str(current)
        with open('current.ini', 'w') as configfile:
            config.write(configfile)

        fileName = datetime.datetime.now().strftime('%Y-%m-%d')
        this_dir = os.path.abspath(os.path.dirname(__file__))
        filePath = (this_dir + '/Logs/' + fileName)
        currentTime = datetime.datetime.now().strftime('%H:%M:%S')
        if os.path.isfile(filePath):
            with open(filePath, 'a') as log_file:
                log_file.write('current time: {}. Value: {}\n'.format(currentTime, current))
        else:
            with open(filePath, 'a') as log_file:
                log_file.write('''Log file for {}

current time: {}. Value: {}\n'''.format(fileName, currentTime, current))
        time.sleep(1)

if __name__ == "__main__": init()
