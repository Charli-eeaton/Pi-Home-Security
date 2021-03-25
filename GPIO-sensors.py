import RPi.GPIO as GPIO
import time
import os

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)         #Read output from PIR motion sensor
GPIO.setup(13, GPIO.IN)         #Read output from magnetic door switch
snapshot = 'DATE=$(date +"%Y-%m-%d_%H:%M") && fswebcam -r 1280x720 /var/www/media/photos/$DATE.jpg' #Take snapshot 
while True:
    #Set variables
    PIR=GPIO.input(11)
    MAG=GPIO.input(13)
    time.sleep(0.25)
    if PIR==1: #if PIR sensor is high write to log file
        t = ("PERSON DETECTED AT ",time.asctime())
        #Append warning message to log file
        log = open("html/log.txt", "a")
        log.writelines(t)
        log.write('\n')
        log.close()
        os.system(snapshot)

    if MAG==1: #if MAG switch is high write to log file
        t = ("MAG OPEN AT ",time.asctime())
        #Append warning message to log file
        log = open("html/log.txt", "a")
        log.writelines(t)
        log.write('\n')
        log.close()
        os.system(snapshot)
