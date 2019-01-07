#!/user/bin/python3

import os
import sys
import requests
import datetime
import time
import RPi.GPIO as GPIO
import configparser #module for the config file
import i2cPy3 #module that interfaces between i2c and DO sensor
from twython import Twython
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
import tkinter as tk
from tkinter import *
win=tk.Tk()
win.title('Garden Pi Status')
from w1thermsensor import W1ThermSensor 

## Output of High turns off valves, output of Low turns on valves

def load_config(filename='config.ini'):
    # opens the config file and tries to read it
    config = configparser.SafeConfigParser()
    this_dir = os.path.abspath(os.path.dirname(__file__))
    config.read(this_dir + '/' + filename)
    
    # checks to see if config file is in right place, if not gives error message
    if config.has_section('ValveConfig'):
        return {name:val for (name, val) in config.items('ValveConfig')}
    else:
        print('Unable to read file {} with section VavleConfig.'.format(filename))
        print('Make sure a file named config.ini lies in the directory {}.'.format(this_dir))
        raise Exception('Unable to find config file')


def load_bedConfig(filename='bed.ini'):
    # opens the file that keeps track of which bed is on
    bedConfig = configparser.SafeConfigParser()
    this_dir = os.path.abspath(os.path.dirname(__file__))
    bedConfig.read(this_dir + '/' + filename)

    # checks to see if bed config file is in right place, if not gives error message
    if bedConfig.has_section('CurrentBed'):
        return bedConfig
    else:
        print('Unable to read file {} with section CurrentBed.'.format(filename))
        print('Make sure a file named bed.ini lies in the directory {}.'.format(this_dir))
        raise Exception('Unable to find bed config file')


def tweet(message):
    # sends a tweet containing the message supplied
    C_key = "rRjHAXnZawtpqmbTwIqtws8SO"
    C_secret = "91Q7kDJefRor7Jg9Zp8HEX1oBTmPShDG4ORFndId4VhMNB8qOI"
    A_token = "1009920921820262400-GxLK5wZXE4AMR8ob5eSVNdWdjKfjyH"
    A_secret = "hKzwWsE240O2bKCcd0myGS90LiKnF4gDhPctowSijG6vx"

    try:
        myTweet = Twython(C_key, C_secret, A_token, A_secret)
        myTweet.update_status(status=message)
    except:
        # could not tweet due to error
        print('Could not tweet.')
    
def nextValve(bedConfig, current):
    # defines the current valve and switches to the next sequential valve
    current += 1
    if current > 4:
        current = 1

    # changes file to record new current value and writes file
    bedConfig['CurrentBed']['current_valve'] = str(current)
    filePath = os.path.abspath(os.path.dirname(__file__)) + '/bed.ini'
    with open(filePath, 'w') as configfile:
        bedConfig.write(configfile)

    # returns the value of the new valve
    return currentValve(bedConfig)


def currentValve(bedConfig):
    # returns the current valve being used
    return int(bedConfig['CurrentBed']['current_valve'])


def runGravelBed(config, bedConfig, logFile, doLevel, temp):
    # sets the next valve and returns it
    current = nextValve(bedConfig, currentValve(bedConfig))
    pin = 0
    runtime = float(config['runtime_min'])

    # changes the pin to the GPIO pin for the current valve
    if current == 1:
        # run gravel bed 1
        pin = int(config['gpio_bed1'])
    elif current == 2:
         # run gravel bed 2
        pin = int(config['gpio_bed2'])
    elif current == 3:
        # run gravel bed 3
        pin = int(config['gpio_bed3'])
    elif current == 4:
        #run gravel bed 4
        pin = int(config['gpio_bed4'])

    # opens and writes to the log file
    with open(logFile, 'a') as log_file:
        try:
            # sets up the GPIO and changes from high to low and back
            GPIO.setup(pin, GPIO.OUT)
            log_file.write('{}: Turning on valve {}.\n'.format(currentTime(), current))
            GPIO.output(pin, GPIO.LOW)
            log_file.flush()
            # runs GUI update before call to sleep for duration of runtime
            UpdateGUI(config, doLevel, temp)
            # lets the valve run for the specified amount of time
            time.sleep(runtime * 60) #converts value to minutes
            log_file.write('{}: Turning off valve {}.\n'.format(currentTime(), current))
            GPIO.output(pin, GPIO.HIGH)
        # catches errors
        except Exception as ex:
            log_file.write('\n{}: An error occured on valve {}.\n{}\n\n'.format(currentTime(), current, ex))
            GPIO.output(pin, GPIO.HIGH)
            message = '{} {}: An error occured on valve {}. {}'.format(date(), currentTime(), current, ex)
            tweet(message)
        

def runDOsystem(config, logFile):
    # checks the level of dissolved oxygen and stores it
    doLevel = checkDO()
    # checks the minimum acceptable value of dissolved oxygen and the necessary GPIO pin
    doMin = float(config['do_min'])
    pin = int(config['gpio_do_sprinkler'])
    with open(logFile, 'a') as log_file:
        log_file.write('{}: Dissolved oxygen level- {} mg/L.\n'.format(currentTime(), doLevel))

        GPIO.setup(pin, GPIO.OUT)
        # keeps sprinkler on if level is too low
        if float(doLevel) < doMin and not GPIO.input(pin):
            log_file.write('{}: Dissolved oxygen is too low. Sprinklers are already on.\n'.format(currentTime()))
            GPIO.output(pin, GPIO.LOW)

        # turns on the sprinkler system if level is too low
        elif float(doLevel) < doMin:
            log_file.write('{}: Dissolved oxygen is too low. Turning on sprinklers.\n\n'.format(currentTime()))
            GPIO.output(pin, GPIO.LOW)
            message = '{} {}: Dissolved oxygen is too low. Turning on sprinklers.\n\n'.format(date(), currentTime())
            tweet(message)
            
        # checks to see if pin is already outputting high
        elif not GPIO.input(pin):
            log_file.write('{}: Dissolved oxygen has returned to normal. Turning off sprinklers.\n\n'.format(currentTime()))
            GPIO.output(pin, GPIO.HIGH)
            message = '{} {}: Dissolved oxygen has returned to normal. Turning off sprinklers.\n\n'.format(date(), currentTime())
            tweet(message)

        # do level is good and sprinklers are off
        else:
            GPIO.output(pin, GPIO.HIGH)

    return doLevel
            

def checkDO():
    # returns the value of the dissolved oxygen given by the sensor
    level = i2cPy3.main()
    return level


def runWaterLevel(config, logFile):
    level = checkWL(config)
    pin = int(config['gpio_fill'])
    with open(logFile, 'a') as log_file:
        GPIO.setup(pin, GPIO.OUT)
        # turns on fill system if water level is too low
        if not GPIO.input(pin) and not level:
            log_file.write('{}: Water level is too low. Fill is already on.\n'.format(currentTime()))
            GPIO.output(pin, GPIO.LOW)

        elif not level:
            log_file.write('\n{}: Water level is too low. Turning on fill.\n'.format(currentTime()))
            GPIO.output(pin, GPIO.LOW)
            message = '{} {}: Water level is too low. Turning on fill.'.format(date(), currentTime())
            tweet(message)
            
        # checks to see if pin is already outputting high but is now good
        elif not GPIO.input(pin):
            log_file.write('{}: Water level has returned to normal. Turning off fill.\n\n'.format(currentTime()))
            GPIO.output(pin, GPIO.HIGH)
            message = '{} {}: Water level has returned to normal. Turning off fill.'.format(date(), currentTime())
            tweet(message)

        # do level is good and sprinklers are off
        else:
            GPIO.output(pin, GPIO.HIGH)
            log_file.write('{}: Water level is good.\n'.format(currentTime()))


# checks the water level sensor
def checkWL(config):
    pin = int(config['gpio_water_sensor'])
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # if there is no water, the pin will return a false
    if not GPIO.input(pin):
        return False
    # if there is water, the pin will return a true
    else:
        return True


# checks the temperature of the water
def checkTemp():
    sensor = W1ThermSensor()
    temperature_in_fahrenheit = sensor.get_temperature(W1ThermSensor.DEGREES_F)
    temperature_in_fahrenheit = '%.1f'%(temperature_in_fahrenheit)
    logFile = (os.path.abspath(os.path.dirname(__file__)) + '/Logs/' + date() + '/temperatureLog')
    with open(logFile, 'a') as log_file:
        log_file.write('{}: Water Temperature- {} ºF.\n'.format(currentTime(), temperature_in_fahrenheit))
    return temperature_in_fahrenheit


# returns the date
def date():
    return datetime.datetime.now().strftime('%Y-%m-%d')
# returns the time
def currentTime():
    return datetime.datetime.now().strftime('%H:%M:%S')


def createLogs(filePath):
    # creates the log files for each day
    os.makedirs(filePath)
    with open((filePath + '/DOsensorLog'), 'a') as log_file1:
        log_file1.write('''Dissolved Oxygen Log File for {}
---------------------------------------
'''.format(date()))
    with open((filePath + '/waterLevelLog'), 'a') as log_file2:
        log_file2.write('''Water Level Log File for {}
---------------------------------------
'''.format(date()))
    with open((filePath + '/bedValvesLog'), 'a') as log_file3:
        log_file3.write('''Gravel Bed Log File for {}
---------------------------------------
'''.format(date()))
    with open((filePath + '/temperatureLog'), 'a') as log_file3:
        log_file3.write('''Temperature Log File for {}
---------------------------------------
'''.format(date()))
    

# creates a GUI that shows the status of the valves and the values of the sensors
def UpdateGUI(config, doLevel, temp):
    pinBed1 = int(config['gpio_bed1'])
    pinBed2 = int(config['gpio_bed2'])
    pinBed3 = int(config['gpio_bed3'])
    pinBed4 = int(config['gpio_bed4'])
    pinDO = int(config['gpio_do_sprinkler'])
    pinFill = int(config['gpio_fill'])
    GPIO.setup((pinBed1, pinBed2, pinBed3, pinBed4, pinDO, pinFill), GPIO.OUT)
    
    # gravel beds section
    label_gravelBeds = tk.Label(win, text='Gravel Beds', relief = RAISED, width=30, font = ('Helvetica', 24)).grid(row=0,column=0, columnspan=2)
    label_bed1 = tk.Label(win, text='Bed 1', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=1,column=0)
    label_bed2 = tk.Label(win, text='Bed 2', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=2,column=0)
    label_bed3 = tk.Label(win, text='Bed 3', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=3,column=0)
    label_bed4 = tk.Label(win, text='Bed 4', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=4,column=0)
    if not GPIO.input(pinBed1):
        label_bed1_status = tk.Label(win, text='ON', relief = SUNKEN, width=15, bg='green', font = ('Helvetica', 20)).grid(row=1,column=1)
    else:
        label_bed1_status = tk.Label(win, text='OFF', relief = SUNKEN, width=15, bg='red', font = ('Helvetica', 20)).grid(row=1,column=1)
    
    if not GPIO.input(pinBed2):
        label_bed2_status = tk.Label(win, text='ON', relief = SUNKEN, width=15, bg='green', font = ('Helvetica', 20)).grid(row=2,column=1)
    else:
        label_bed1_status = tk.Label(win, text='OFF', relief = SUNKEN, width=15, bg='red', font = ('Helvetica', 20)).grid(row=2,column=1)

    if not GPIO.input(pinBed3):
        label_bed3_status = tk.Label(win, text='ON', relief = SUNKEN, width=15, bg='green', font = ('Helvetica', 20)).grid(row=3,column=1)
    else:
        label_bed1_status = tk.Label(win, text='OFF', relief = SUNKEN, width=15, bg='red', font = ('Helvetica', 20)).grid(row=3,column=1)

    if not GPIO.input(pinBed4):
        label_bed4_status = tk.Label(win, text='ON', relief = SUNKEN, width=15, bg='green', font = ('Helvetica', 20)).grid(row=4,column=1)
    else:
        label_bed1_status = tk.Label(win, text='OFF', relief = SUNKEN, width=15, bg='red', font = ('Helvetica', 20)).grid(row=4,column=1)

    # dissolved oxygen sensor section
    label_gravelBeds = tk.Label(win, text='Dissolved Oxygen', relief = RAISED, width=30, font = ('Helvetica', 24)).grid(row=5,column=0, columnspan=2)
    label_DOlevel = tk.Label(win, text='Level', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=6,column=0)
    label_DOvalve = tk.Label(win, text='Sprinklers', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=7,column=0)
    label_DOlevel_status = tk.Label(win, text='{} mg/L'.format(doLevel), relief = SUNKEN, bg='white', width=15, font = ('Helvetica', 20)).grid(row=6,column=1)
    if not GPIO.input(pinDO):
        label_DOvalve_status = tk.Label(win, text='ON', relief = SUNKEN, width=15, bg='green', font = ('Helvetica', 20)).grid(row=7,column=1)
    else:
        label_DOvalve_status = tk.Label(win, text='OFF', relief = SUNKEN, width=15, bg='red', font = ('Helvetica', 20)).grid(row=7,column=1)

    # water level section
    label_waterLevel = tk.Label(win, text='Water Level', relief = RAISED, width=30, font = ('Helvetica', 24)).grid(row=8,column=0, columnspan=2)
    label_fillValve = tk.Label(win, text='Filling', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=9,column=0)
    if not GPIO.input(pinFill):
        label_fillValve_status = tk.Label(win, text='ON', relief = SUNKEN, width=15, bg='green', font = ('Helvetica', 20)).grid(row=9,column=1)
    else:
        label_fillValve_status = tk.Label(win, text='OFF', relief = SUNKEN, width=15, bg='red', font = ('Helvetica', 20)).grid(row=9,column=1)

    # temperature section
    label_temperature = tk.Label(win, text='Water Temperature', relief = RAISED, width=30, font = ('Helvetica', 24)).grid(row=10,column=0, columnspan=2)
    label_currentTemp = tk.Label(win, text='Current Temp', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=11,column=0)
    label_currentTemp_status = tk.Label(win, text='{} ºF'.format(temp), relief = SUNKEN, width=15, bg='white', font = ('Helvetica', 20)).grid(row=11,column=1)

    label_buffer = tk.Label(win, text='Please do not close GUI', relief = RAISED, width=30, font = ('Helvetica', 24)).grid(row=12,column=0, columnspan=2)
    # updates the GUI before the sleep call
    win.update()
    

def test():
    # tests the status of each valve and the value of the sensors

    # loads the config files
    config = load_config()
    bedConfig = load_bedConfig()

    # checks which bed is being filled
    print('Gravel bed {} is currently being filled.'.format(currentValve(bedConfig)))
    
    GPIO.setup((int(config['gpio_bed1']), int(config['gpio_bed2']), int(config['gpio_bed3']),
                            int(config['gpio_bed4']), int(config['gpio_do_sprinkler']),
                            int(config['gpio_fill'])), GPIO.OUT)
    # checks if the valve for bed 1 is open
    if not GPIO.input(int(config['gpio_bed1'])):
        print('The valve to gravel bed 1 is open.')
    else:
        print('The valve to gravel bed 1 is closed.')
    # checks if the valve for bed 2 is open
    if not GPIO.input(int(config['gpio_bed2'])):
        print('The valve to gravel bed 2 is open.')
    else:
        print('The valve to gravel bed 2 is closed.')
    # checks if the valve for bed 3 is open
    if not GPIO.input(int(config['gpio_bed3'])):
        print('The valve to gravel bed 3 is open.')
    else:
        print('The valve to gravel bed 3 is closed.')
    # checks if the valve for bed 4 is open
    if not GPIO.input(int(config['gpio_bed4'])):
        print('The valve to gravel bed 4 is open.')
    else:
        print('The valve to gravel bed 4 is closed.')
        
    # checks if the sprinkler system is on
    if not GPIO.input(int(config['gpio_do_sprinkler'])):
        print('The dissolved oxygen sprinkler system is on.')
    else:
        print('The dissolved oxygen sprinkler system is off.')
    # checks if the tank is filling
    if not GPIO.input(int(config['gpio_fill'])):
        print('The tank fill valve is open.')
    else:
        print('The tank fill valve is closed.')

    # prints the values of the sensors
    sensorValues = sensors()
    print(sensorValues)
    

def sensors():
    # returns the dissolved oxygen level
    DOlevel = checkDO()
    DOoutput = ('Dissolved Oxygen Level: {} mg/L.\n'.format(DOlevel))

    # returns the water temperature
    tempString = 'Water Temperature: {} ºF.\n'.format(checkTemp())
    
    # returns the water level
    config = load_config()
    waterLevel = checkWL(config)
    wlString = ''
    if waterLevel:
        wlString = 'The water level is good.'
    else:
        wlString = 'The water level is too low.'

    # returns the combined string from sensors
    return (DOoutput + tempString + wlString)


def main():
    # load the config file and the bed config file
    config = load_config()
    bedConfig = load_bedConfig()

    #check for log file for the day
    filePath = (os.path.abspath(os.path.dirname(__file__)) + '/Logs/' + date())
    if not os.path.exists(filePath):
        createLogs(filePath)
            
    # sensors run first so that they are not stopped by the sleep() in running the gravel bed
    
    # takes measurement from the oxygen sensor and takes appropriate measures
    doLog = (filePath + '/DOsensorLog')
    doLevel = runDOsystem(config, doLog)
    # takes measurement from water level and takes appropriate measures
    wlLog = (filePath + '/waterLevelLog')
    runWaterLevel(config, wlLog)
    # takes the measurement from the water level
    tempLog = (filePath + '/temperatureLog')
    temp = checkTemp()
    
    # fills the gravel beds
    gravelLog = (filePath + '/bedValvesLog')
    runGravelBed(config, bedConfig, gravelLog, doLevel,  temp)
    

def init(start=False, end=False):
    # run when the Pi restarts, makes sure that all the pins are set as outputs and low
    config = load_config()
    pinBed1 = int(config['gpio_bed1'])
    pinBed2 = int(config['gpio_bed2'])
    pinBed3 = int(config['gpio_bed3'])
    pinBed4 = int(config['gpio_bed4'])
    pinDO = int(config['gpio_do_sprinkler'])
    pinWLsensor = int(config['gpio_water_sensor'])
    pinFill = int(config['gpio_fill'])
    GPIO.setup((pinBed1, pinBed2, pinBed3, pinBed4, pinDO, pinFill), GPIO.OUT)
    GPIO.output((pinBed1, pinBed2, pinBed3, pinBed4, pinDO, pinFill), GPIO.HIGH)
    GPIO.setup(pinWLsensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    #check for log file for the day
    filePath = (os.path.abspath(os.path.dirname(__file__)) + '/Logs/' + date())
    if not os.path.exists(filePath):
        createLogs(filePath)
            
    # logs that the pi restarted
    if start:
        # logs that the pi got ready for the day
        with open(filePath + '/bedValvesLog', 'a') as log_file:
            log_file.write('{}: The Pi is ready for the day.\n\n'.format(currentTime()))
        message = ('{} {}: The Pi is ready for the day.'.format(date(), currentTime()))
        tweet(message)
    elif end:
        # logs that the pi initiated turned off valves for the day
        with open(filePath + '/bedValvesLog', 'a') as log_file:
            log_file.write('\n{}: The Pi is done for the day.\n\n'.format(currentTime()))
    else:
        # logs that the pi restarted to the bed valves log
        with open(filePath + '/bedValvesLog', 'a') as log_file:
            log_file.write('\n{}: The Pi restarted.\n\n'.format(currentTime()))
        # waits for internet connection for 60 seconds
        counter = 0
        internet = False
        while counter < 60 and not internet:
            try:
                urllib2.urlopen('https://google.com')
                internet = True
            except:
                time.sleep(5)
                counter = counter + 5
        # sends a tweet notifying that the pi restarted
        message = ('{} {}: The Pi restarted.'.format(date(), currentTime()))
        tweet(message)

    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        # normal
        main()
    elif len(sys.argv) == 2 and sys.argv[1] == 'test':
        # test that the valves are on and the sensors are returning values
        # run by console, type in 'python3 /home/pi/GardenPi/main.py test'
        test()
    elif len(sys.argv) == 2 and sys.argv[1] == 'sensors':
        # checks the values of the sensors
        # run by console, type in 'python3 /home/pi/GardenPi/main.py sensors'
        sensorValues = sensors()
        print(sensorValues)
    elif len(sys.argv) == 2 and sys.argv[1] == 'init':
        # runs when the Raspberry Pi restarts
        init()
    elif len(sys.argv) == 2 and sys.argv[1] == 'startup':
        # runs at the beginning of each day
        init(True, False)
    elif len(sys.argv) == 2 and sys.argv[1] == 'shutdown':
        # runs at the end of each day
        init(False, True)
    else:
        print('Unknown inputs ', sys.argv)
