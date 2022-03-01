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

logger = log4p.GetLogger(__name__, config=log_config)
log = logger.logger

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER_1 = 18
GPIO_ECHO_1 = 24
GPIO_TRIGGER_2 = 17
GPIO_ECHO_2 = 25

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER_1, GPIO.OUT)
GPIO.setup(GPIO_ECHO_1, GPIO.IN)
GPIO.setup(GPIO_TRIGGER_2, GPIO.OUT)
GPIO.setup(GPIO_ECHO_2, GPIO.IN)

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

def mesure_capteur_depart():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER_1, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER_1, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO_1) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO_1) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def mesure_capteur_fin():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER_2, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER_2, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO_2) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO_2) == 1:
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
       # lcd.lcd_display_string('Brancher le bras'.ljust(16),int(2))
       log.debug('Device ' + device + ' not found!')
       log.error("Arm is not connected to USB port!")
       time.sleep(2)
       sys.exit()

    # Open grbl serial port
    arduino_serial = serial.Serial(device, bauds)
    
    # Wake up grbl
    arduino_serial.write("\r\n\r\n")
    time.sleep(2)   # Wait for grbl to initialize
    arduino_serial.flushInput()  # Flush startup text in serial input

    log.info('Mise en position')
    #lcd.lcd_display_string('Mise en position'.ljust(16),int(2))

    grbl_out = 'n/a'
    dist_capteur_depart = 0
    dist_capteur_fin = 0
    rotation_coord = 0
    rotation_sens = '+'

    try:
        while True:
            dist_capteur_depart = mesure_capteur_depart()
            print ("Mesure capteur depart = %.1f cm" % dist_capteur_depart)

            # dist_capteur_fin = mesure_capteur_fin()
            # print ("Mesure capteur fin = %.1f cm" % dist_capteur_fin)
            time.sleep(0.5)
            
            # Si la distance mesuree par le capteur de depart est inerieure a 10cm : on monte la pince
            if dist_capteur_depart < 10 and rotation_sens == "+":
               arduino_serial.write('X-2.5 Y0.5\n')
               arduino_serial.write('Y4.6\n') 
               #rotation_sens = '+'
               continue
            
            # Si la distance mesuree par le capteur de depart est inerieure a 10cm : on descend la pince et on la ferme
            if dist_capteur_depart < 10 and rotation_sens == "-":
               arduino_serial.write('X0 Y0\n')
               time.sleep(0.2)
               arduino_serial.write('M3S50\n')
               rotation_sens = '+'
               continue

            # Si la distance mesuree par le capteur de depart est superieure a 10 cm : on tourne
            # if dist_capteur_depart > 10 and dist_capteur_fin > 20 :
            if dist_capteur_depart > 10:
               rotation_coord = rotation_coord + 0.1
               # print (rotation_coord)
               # print ('Z' + rotation_sens '%.1f' % rotation_coord)
               arduino_serial.write('Z%s%.1f \n' % (rotation_sens, rotation_coord))
               continue

             # Si la distance mesuree par le capteur de fin est inferieure a 20 cm : onfait une pause, on ouvre la pince et on inverse le sens de rotation
             if dist_capteur_fin < 20:
                time.sleep(0.2)
                arduino_serial.write('M3S0\n')
                time.sleep(0.2)
                rotation_sens = '-'
                continue

    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Stopped by User")
        GPIO.cleanup()
 
