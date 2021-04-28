#!/usr/bin/python

import RPi.GPIO as GPIO
from datetime import datetime
from time import sleep
import os
from rpi_ws281x import *
import random

############
# CONSTANTS#
############
# Input pin is 15 (GPIO22)
INPUT_PIN = 15
# To turn on debug print outs, set to 1
DEBUG = 1

# LED strip configuration:
LED_COUNT      = 1      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

#LICHT
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()


###################
# INITIALIZE PINS #
###################
GPIO.setmode(GPIO.BOARD)
GPIO.setup(INPUT_PIN, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(INPUT_PIN, GPIO.IN)

# Main loop, listen for infinite packets
while True:
    print("\nWaiting for GPIO low")

    # If there was a transmission, wait until it finishes
    #GPIO.wait_for_edge(INPUT_PIN, GPIO.RISING)
    value = 1
    while value:
        sleep(0.001)
        #print("Last read value: {}".format(value))
        value = GPIO.input(INPUT_PIN)       

    # timestamps for pulses and packet reception
    startTimePulse = datetime.now()
    previousPacketTime = 0

    print("\nListening for an IR packet")

    # Buffers the pulse value and time durations
    pulseValues = []
    timeValues = []
    message = []
    data = []

    # Variable used to keep track of state transitions
    previousVal = 0

    # Inner loop 
    while True:
        # Measure time up state change
        if value != previousVal:
            # The value has changed, so calculate the length of this run
            now = datetime.now()
            pulseLength = now - startTimePulse
            startTimePulse = now

            # Record value and duration of current state
            pulseValues.append(value)
            timeValues.append(pulseLength.microseconds)
            
            # Detect short IR packet using packet length and special timing
            if(len(pulseValues) == 3):
                if(timeValues[1] < 3000):
                    print("Detected Short IR packet")
                    #print(pulseValues) so they don't show up every time
                    #print(timeValues)
                    break;

            # Detect standard IR packet using packet length 
            if(len(pulseValues) == 67):
                if(DEBUG==1):
                    print("Finished receiving standard IR packet")
                    #print(pulseValues) same reason as above
                    #print(timeValues)
                    #TODO: Decode packet and perform task
                
                    breaks = []

                    for x in timeValues[3:66:2]:
                        breaks.append(x)

                    bits = []

                    for x in breaks:
                        if x >= 1000:
                            bits.append(1)
                        else:
                            bits.append(0)
                        
                    address = bits[0:8]
                    data = bits[16:24]

                    address.reverse()
                    data.reverse()

                    decodedaddress = int("".join(str(x) for x in address), 2)
                    decodeddata = int("".join(str(x) for x in data), 2)
                    #I only needed this part during testing/programming
                    #print ("address ist " +  str(decodedaddress))
                    #print ("data ist " +  str(decodeddata))

                    colorlist = [(0,255,0),(255,0,0),(10,10,10),(40,100,100),(0,0,225),(0,50,50),(150,255,0),(74,253,255),(10,180,180),(85,150,200),(50,100,100)]

                    #If( timing of up key is detected) then increase-led-brightness()
                    #Für Herr Parget: mein bester Guess, der aber nicht funktioniert hat:
                    if decodeddata == 24:
                        #versuch, mit i nach jedem button press immer eine Farbe 
                        #weiter zu schalten aus der colorlist
                        #auch ein Problem: was, wenn dann der letzte Index erreicht wird?
                        #wird eine Fehlermeldung geben, aber für die Aufgabe wahrsch. zu aufwändig
                        #diese mit einzuberechnen
                        #Rückmeldung aus Terminal: es fehlen die zwei Angaben zu Blau und Grün
                        i = 0
                        strip.setPixelColor(0, Color(colorlist[i]))
                        strip.show()
                        i += 1
                        print("up")

                    elif decodeddata == 82:
                        #wenn ich schon nicht schaffe, dass die Farben der Liste nach wechseln
                        #wenigstens random eine neue farbe aussucht, aber auch das hat nicht geklappt
                        strip.setPixelColor(0, Color(random.choice(colorlist)))
                        strip.show()
                        print("down")

                    elif decodeddata == 8:
                        #falls dann mal eine möglichkeit zum umschalten da ist, diese Logik auch für 
                        #die Helligkeit anwenden in 25er schritten
                        strip.setBrightness(100)
                        strip.show()
                        print("left")

                    elif decodeddata == 90:
                        strip.setBrightness(200)
                        strip.show()
                        print("right")
                    
                    #to kinda turn off the LED when press "enter" on the remote
                    elif decodeddata == 28:
                        strip.setPixelColor(0, Color(0, 0, 0))
                        strip.show()
                
                    break;

        # save state
        previousVal = value
        # read GPIO pin
        value = GPIO.input(INPUT_PIN)

