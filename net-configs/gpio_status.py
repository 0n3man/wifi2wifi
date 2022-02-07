#! /usr/bin/python3
import os
import subprocess
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from time import sleep     # Import the sleep function from the time module

GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)   # Set pin 8 to be an output pin and set initial value to low (off)

internet_test_addr = "8.8.8.8" #example
ledState=0
sleepDelay=.5

while True: # Run forever

    index_status = os.system("ps -efw |grep index.js |grep -v grep")
    # if we're trying to conigure wifi
    if index_status == 0:
        print( "node index.js running")
        # if node index.js is running keep the light on
        ledState = 0
        sleepDelay = 1
    else:
        # at this point trying to bring up outbound internet connection
        wifi_status = subprocess.check_output("wpa_cli -iwlan0 status | sed -n -e '/^wpa_state=/{s/wpa_state=//;p;q}'", shell=True, text=True)
        if "COMPLETED" in wifi_status: 
            # The outbound connection has been made
            wifi_ssid = subprocess.check_output("wpa_cli -iwlan0 status | sed -n -e '/^ssid=/{s/ssid=//;p;q}'", shell=True, text=True)
            response = os.system("ping -c 1 " + internet_test_addr + "> /dev/null")
            # we can ping our test site 
            if response == 0:
                # all is good keep the light off
                print("Connected to " + wifi_ssid +  " and can reach outside world, all is good")

                # then keep the light off because everything is working
                ledState = 1
                sleepDelay = 30
            else:
                # connected to outbound wifi but can't ping test site
                # flip the light every half second
                print("Connected to " + wifi_ssid +  " but waiting for outside would connectivity")
                sleepDelay = 1

        # waiting for outbound wifi to connect to flip light every second
        else:
            print("Bring outbound wifi connection up")
            sleepDelay = .5


    if ledState == 0:
        ledState = 1
        GPIO.output(8, GPIO.HIGH) # Turn on
    else:
        ledState = 0
        GPIO.output(8, GPIO.LOW)  # Turn off

    sleep(sleepDelay)                  # Sleep for 1 second



