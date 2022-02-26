#!/usr/bin/env python
# #!/bin/bash
#
#
# 3 options :
# - screen $DEVICE $BAUDS
# - simple_stream.py
# - socat TCP4-LISTEN:25555,reuseaddr,fork /dev/ttyACM0,b38400,raw,echo=0
# DEVICE="/dev/ttyACM0"
# BAUDS=115200
##########################################################################


#Libraries
import RPi.GPIO as GPIO
import time

# import grbl
import os, serial, signal, sys
import ConfigParser, log4p

config_file = '../conf/c2irobot.conf'

if len(sys.argv) > 1   :
    config_file = sys.argv[1]

config = ConfigParser.ConfigParser()
config.read(config_file)

conf_dir = config.get('general', 'conf_dir')
log_config = config.get('general', 'log_config')
device = config.get('bras', 'device')
bauds = config.get('bras', 'bauds')
gcode_debut = config.get('bras', 'gcode_debut')
gcode_boucle = config.get('bras', 'gcode_boucle')
gcode_fin = config.get('bras', 'gcode_fin')

logger = log4p.GetLogger(__name__, config=log_config)
log = logger.logger

def readConfiguration(signalNumber, frame):
    log.info('(SIGHUP) reading configuration')
    return

def terminateProcess(signalNumber, frame):
    global ending
    ending = True
    log.info('(SIGTERM) terminating the process')
    #lcd.lcd_display_string('Arret demande'.ljust(16),int(2))
    return

def interruptProcess(signalNumber, frame):
    global ending
    ending = True
    log.info('(SIGINT) interrupt the process')
    #lcd.lcd_display_string('Arret demande'.ljust(16),int(2))
    return

def receiveSignal(signalNumber, frame):
    log.info('Received:', signalNumber)
    return

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
     
if __name__ == '__main__':
    # register the signals to be caught
    signal.signal(signal.SIGHUP, readConfiguration)
    signal.signal(signal.SIGINT, interruptProcess)
    signal.signal(signal.SIGQUIT, receiveSignal)
    signal.signal(signal.SIGILL, receiveSignal)
    signal.signal(signal.SIGTRAP, receiveSignal)
    signal.signal(signal.SIGABRT, receiveSignal)
    signal.signal(signal.SIGBUS, receiveSignal)
    signal.signal(signal.SIGFPE, receiveSignal)
    #signal.signal(signal.SIGKILL, receiveSignal)
    signal.signal(signal.SIGUSR1, receiveSignal)
    signal.signal(signal.SIGSEGV, receiveSignal)
    signal.signal(signal.SIGUSR2, receiveSignal)
    signal.signal(signal.SIGPIPE, receiveSignal)
    signal.signal(signal.SIGALRM, receiveSignal)
    signal.signal(signal.SIGTERM, terminateProcess)

    log.info('Initialisation')
    
    time.sleep(1)
    if not os.path.exists(device):
      #lcd.lcd_display_string('Brancher le bras'.ljust(16),int(2))
      log.debug('Device ' + device + ' not found!')
      log.error("Arm is not connected to USB port!")
      time.sleep(2)
      sys.exit()

    # Open grbl serial port
    s = serial.Serial(device, bauds)
    
        # Wake up grbl
    s.write("\r\n\r\n")
    time.sleep(2)   # Wait for grbl to initialize
    s.flushInput()  # Flush startup text in serial input

    log.info('Mise en position')
    #lcd.lcd_display_string('Mise en position'.ljust(16),int(2))

    grbl_out = 'n/a'
    
    
    try:
        while True:
            dist = distance()
            print ("Measured Distance = %.1f cm" % dist)
            print (dist)
            time.sleep(1)
            
            if dist < 10:
			   # montee de la pince
               s.write('X-2.5 Y0.5\n') 
            
            coord = 0
            while dist > 10:
				coord = coord + 0.1
				print (coord)
				print ('Z+%.1f' % coord)
				s.write('Z+%.1f \n' % coord)
 
            
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
 
