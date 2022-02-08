#! /usr/bin/python3
import os
import drivers
import subprocess
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from time import sleep     # Import the sleep function from the time module

GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)   # Set pin 8 to be an output pin and set initial value to low (off)

internet_test_addr = "8.8.8.8" #example
ledState=0
sleepDelay=.5
display = drivers.Lcd()

#grep wpa_passphrase /etc/hostapd/wlan1.conf |cut -d '=' -f 2
#grep ssid /etc/hostapd/wlan1.conf |cut -d '=' -f 2

my_pw = subprocess.check_output("grep wpa_passphrase /etc/hostapd/hostapd.conf |cut -d '=' -f 2 |tr '\n' ' '", shell=True, text=True)
my_ssid = subprocess.check_output("grep ssid /etc/hostapd/hostapd.conf |cut -d '=' -f 2| tr '\n' ' '", shell=True, text=True)

loop=0

try:
    while True: # Run forever

        index_status = os.system("ps -efw |grep index.js |grep -v grep")
        # if we're trying to conigure wifi
        if index_status == 0:
            #print( "node index.js running:" + my_ssid + " " + my_pw)
            if loop == 0:
                loop = 1
                display.lcd_display_string("SSID:" + my_ssid + "                ", 1)
                display.lcd_display_string("PP:" + my_pw + "               ",2)
            else:
                loop = 0
                display.lcd_display_string("Need input      ", 1)
                display.lcd_display_string("http-172.16.33.1", 2)

            # if node index.js is running keep the light on
            ledState = 0
            sleepDelay = 2 
        else:
            # at this point trying to bring up outbound internet connection
            wifi_status = subprocess.check_output("wpa_cli -iwlan0 status | sed -n -e '/^wpa_state=/{s/wpa_state=//;p;q}'", shell=True, text=True)
            wifi_ssid = subprocess.check_output("wpa_cli -iwlan0 status | sed -n -e '/^ssid=/{s/ssid=//;p;q}' |tr '\n' ' '", shell=True, text=True)
            if "COMPLETED" in wifi_status: 
                # The outbound connection has been made
                response = os.system("ping -c 1 " + internet_test_addr + "> /dev/null")
                # we can ping our test site 
                if response == 0:
                    # all is good keep the light off
                    if loop == 0:
                       loop = 1
                       display.lcd_display_string("SSID:" + my_ssid + "                ", 1)
                       display.lcd_display_string("PP:" + my_pw + "               ",2)
                    else:
                        loop = 0
                        #print("Connected to " + wifi_ssid +  " and can reach outside world, all is good")
                        display.lcd_display_string("Connected to    ", 1)
                        display.lcd_display_string(wifi_ssid + "                 ", 2)

                    # then keep the light off because everything is working
                    ledState = 1
                    sleepDelay = 30
                else:
                    # connected to outbound wifi but can't ping test site
                    # flip the light every half second
                    #print("Connected to " + wifi_ssid +  " but waiting for outside would connectivity")
                    display.lcd_display_string("Trying internet ", 1)
                    display.lcd_display_string("on " + wifi_ssid + "             ", 2)
                    sleepDelay = 1

            # waiting for outbound wifi to connect to flip light every second
            else:
                display.lcd_display_string("Connecting to   ", 1)
                display.lcd_display_string(wifi_ssid + "                ", 2)
                #print("Bring outbound wifi connection up")
                sleepDelay = .5


        if ledState == 0:
            ledState = 1
            GPIO.output(8, GPIO.HIGH) # Turn on
        else:
            ledState = 0
            GPIO.output(8, GPIO.LOW)  # Turn off

        sleep(sleepDelay)                  # Sleep for 1 second

except KeyboardInterrupt:
    # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    #print("Cleaning up!")
    display.lcd_clear()


