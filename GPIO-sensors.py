import RPi.GPIO as GPIO
import time
import os

import glob
from dominate import document
from dominate.tags import *

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)         #Read output from PIR motion sensor
GPIO.setup(13, GPIO.IN)         #Read output from magnetic door switch

snapshot = 'DATE=$(date +"%Y-%m-%d_%H:%M.%S") && fswebcam -r 1280x720 /var/www/html/media/photos/$DATE.jpg' #Take snapshot 

#Append warning message to log file
def write_to_file(t):
        log = open("html/log.txt", "a")
        log.writelines(t)
        log.write('\n')
        log.close()
        os.system(snapshot)

while True:
    #Set variables
    PIR=GPIO.input(11)
    MAG=GPIO.input(13)
    time.sleep(1)
    
    if PIR==1 or MAG==1:
        if PIR==1: #if PIR sensor is high write to log file
            t = ("PERSON DETECTED AT ",time.asctime())
            write_to_file(t)

        if MAG==1: #if MAG switch is high write to log file
            t = ("MAG OPEN AT ",time.asctime())
            write_to_file(t)
