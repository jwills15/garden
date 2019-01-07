from w1thermsensor import W1ThermSensor

sensor = W1ThermSensor()
temperature_in_celsius = sensor.get_temperature()
temperature_in_fahrenheit = sensor.get_temperature(W1ThermSensor.DEGREES_F)
print(temperature_in_celsius)
temperature_in_fahrenheit = '%.1f'%(temperature_in_fahrenheit)
print(temperature_in_fahrenheit)
