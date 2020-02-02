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

import os
import serial
import time
import signal
import sys
import ConfigParser
import i2c_lcd

config_file = '../conf/c2irobot.conf'

if len(sys.argv) > 1   :
    config_file = sys.argv[1]

config = ConfigParser.ConfigParser()
config.read(config_file)
device = config.get('bras', 'device')
bauds = config.get('bras', 'bauds')
gcode_debut = config.get('bras', 'gcode_debut')
gcode_boucle = config.get('bras', 'gcode_boucle')
gcode_fin = config.get('bras', 'gcode_fin')

lcd = i2c_lcd.lcd()
time.sleep(.1)
lcd.lcd_clear()
time.sleep(.1)
lcd.lcd_display_string('   C2I  Robot',int(1))

def readConfiguration(signalNumber, frame):
    print ('(SIGHUP) reading configuration')
    return

def terminateProcess(signalNumber, frame):
    print ('(SIGTERM) terminating the process')
    lcd.lcd_display_string('Arret demande',int(2))
    global ending
    ending = True
    return

def interruptProcess(signalNumber, frame):
    print ('(SIGINT) interrupt the process')
    lcd.lcd_display_string('Arret demande',int(2))
    global ending
    ending = True
    return

def receiveSignal(signalNumber, frame):
    print('Received:', signalNumber)
    return

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

    lcd.lcd_display_string('Initialisation',int(2))
    time.sleep(2)
    if not os.path.exists(device):
      lcd.lcd_display_string('Brancher le bras',int(2))
      time.sleep(10)
      sys.exit()


    lcd.lcd_display_string('Demarrage',int(2))
    # Open grbl serial port
    s = serial.Serial(device, bauds)

    # Wake up grbl
    s.write("\r\n\r\n")
    time.sleep(2)   # Wait for grbl to initialize
    s.flushInput()  # Flush startup text in serial input

    # Open g-code files
    f_init = open('../conf/' + gcode_debut,'r');

    # Stream init g-code to grbl
    for line_init in f_init:
        l = line_init.strip() # Strip all EOL characters for consistency
        print 'Sending: ' + l,
        s.write(l + '\n') # Send g-code block to grbl
        grbl_out = s.readline() # Wait for grbl response with carriage return
        print ' : ' + grbl_out.strip()

    f_init.close()

    lcd.lcd_display_string('Execution ...',int(2))
    ending = False
    # Start loop
    while True:
        # Open g-code files
        f_loop = open('../conf/' + gcode_boucle,'r');

        # Stream loop g-code to grbl
        for line_loop in f_loop:
            l = line_loop.strip() # Strip all EOL characters for consistency
            print 'Sending: ' + l,
            s.write(l + '\n') # Send g-code block to grbl
            grbl_out = s.readline() # Wait for grbl response with carriage return
            print ' : ' + grbl_out.strip()

        #print 'DEBUG: end f_loop %r' % ending

        f_loop.close()

        if ending == True:
            break

    lcd.lcd_display_string('Fin du cycle',int(2))
    # Open g-code files
    f_finish = open('../conf/' + gcode_fin,'r');

    # Stream finish g-code to grbl
    for line_finish in f_finish:
        l = line_finish.strip() # Strip all EOL characters for consistency
        print 'Sending: ' + l,
        s.write(l + '\n') # Send g-code block to grbl
        grbl_out = s.readline() # Wait for grbl response with carriage return
        print ' : ' + grbl_out.strip()

    f_finish.close()

    # Wait here until grbl is finished to close serial port and file.
    # raw_input("  Press <Enter> to exit and disable grbl.")
    lcd.lcd_display_string('Fin',int(2))
    time.sleep(5)

    # Close file and serial port
    s.close()

    lcd.lcd_clear()
