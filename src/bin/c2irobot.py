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

import os, serial, time, signal, sys
import ConfigParser, log4p
import i2c_lcd

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

lcd = i2c_lcd.lcd()
time.sleep(.1)
lcd.lcd_clear()
time.sleep(.1)
lcd.backlight_on(True)
lcd.lcd_display_string('   C2I  Robot'.ljust(16),int(1))

def readConfiguration(signalNumber, frame):
    log.info('(SIGHUP) reading configuration')
    return

def terminateProcess(signalNumber, frame):
    global ending
    ending = True
    log.info('(SIGTERM) terminating the process')
    lcd.lcd_display_string('Arret demande'.ljust(16),int(2))
    return

def interruptProcess(signalNumber, frame):
    global ending
    ending = True
    log.info('(SIGINT) interrupt the process')
    lcd.lcd_display_string('Arret demande'.ljust(16),int(2))
    return

def receiveSignal(signalNumber, frame):
    log.info('Received:', signalNumber)
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

    log.info('Initialisation')
    lcd.lcd_display_string('Initialisation'.ljust(16),int(2))
    time.sleep(2)
    if not os.path.exists(device):
      lcd.lcd_display_string('Brancher le bras'.ljust(16),int(2))
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
    lcd.lcd_display_string('Mise en position'.ljust(16),int(2))

    grbl_out = 'n/a'

    # Open g-code files
    f_init = open(conf_dir + '/' + gcode_debut,'r');

    # Stream init g-code to grbl
    for line_init in f_init:
        l = line_init.strip() # Strip all EOL characters for consistency
        log.debug('Sending: ' + l)
        s.write(l + '\n') # Send g-code block to grbl
        grbl_out = s.readline() # Wait for grbl response with carriage return
        log.debug('Return information : ' + grbl_out.strip())

    f_init.close()

    log.info('Debut du cycle')
    lcd.lcd_display_string('Execution ...'.ljust(16),int(2))

    ending = False
    # Start loop
    while True:
        # Open g-code files
        f_loop = open(conf_dir + '/' + gcode_boucle,'r');

        # Stream loop g-code to grbl
        for line_loop in f_loop:
            l = line_loop.strip() # Strip all EOL characters for consistency
            log.debug('Sending: ' + l)
            s.write(l + '\n') # Send g-code block to grbl
            # BDT : bug la commande s.read plante lorsque le programme recoit un SIGTERM
            #       le port serie est occupe. On contourne le pb en faisant une pause.
            time.sleep(2)
            grbl_out = s.readline() # Wait for grbl response with carriage return
            log.debug('Return information : ' + grbl_out.strip())

        f_loop.close()

        log.debug('flag de fin de boucle : ' + str(ending))

        # On teste la variable ending qui est modifiee par les fonctions executees
        # lorsque des signaux sont envoyes au processus. ending == True pour arrete la boucle.
        if ending == True:
            break

    log.info('Fin du cycle')
    lcd.lcd_display_string('Fin du cycle'.ljust(16),int(2))

    log.info('Retour en position initiale')
    # Open g-code files
    f_finish = open(conf_dir + '/' + gcode_fin,'r');

    # Stream finish g-code to grbl
    for line_finish in f_finish:
        l = line_finish.strip() # Strip all EOL characters for consistency
        log.debug('Sending: ' + l)
        s.write(l + '\n') # Send g-code block to grbl
        grbl_out = s.readline() # Wait for grbl response with carriage return
        log.debug('Return information : ' + grbl_out.strip())

    f_finish.close()

    # Wait here until grbl is finished to close serial port and file.
    time.sleep(5)

    # Close file and serial port
    s.close()

    # Turn off LCD screen
    lcd.lcd_display_string('Fin de session'.ljust(16),int(2))
    time.sleep(3)
    lcd.lcd_clear()
    time.sleep(.1)
    lcd.backlight_on(False)

    log.info('Fin de session')
