import configparser
config = configparser.ConfigParser()

config.read('configfile.ini')
current = int(config['DEFAULT']['whichValve'])
current += 1
config['DEFAULT']['whichValve'] = str(current)

print(config['DEFAULT']['whichValve'])
if current >= 4:
    config['DEFAULT']['whichValve'] = '0'

print(config['DEFAULT']['whichValve'])

with open('configfile.ini', 'w') as configfile:
    config.write(configfile)
