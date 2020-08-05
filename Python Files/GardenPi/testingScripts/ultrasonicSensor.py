import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

#set GPIO pins
GPIO_trig = 36
GPIO_echo = 38

GPIO.setup(GPIO_trig, GPIO.OUT)
GPIO.setup(GPIO_echo, GPIO.IN)

time.sleep(5)

# set Trigger to HIGH
GPIO.output(GPIO_trig, True)
 
# set Trigger after 0.01ms to LOW
time.sleep(0.00001)
GPIO.output(GPIO_trig, False)
 
StartTime = time.time()
StopTime = time.time()
 
# save StartTime
while GPIO.input(GPIO_echo) == 0:
    StartTime = time.time()

# save time of arrival
while GPIO.input(GPIO_echo) == 1:
    StopTime = time.time()
 
# time difference between start and arrival
TimeElapsed = StopTime - StartTime
# multiply with the sonic speed (34300 cm/s)
# and divide by 2, because there and back
distance = (TimeElapsed * 34300) / 2

print(distance)
