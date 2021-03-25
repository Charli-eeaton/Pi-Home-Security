import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)         #Read output from PIR motion sensor
GPIO.setup(13, GPIO.IN)         #Read output from magnetic door switch

while True:
    #Set variables
    PIR=GPIO.input(11)
    MAG=GPIO.input(13)
    time.sleep(0.25)
    if PIR==1: #if PIR sensor is high write to log file
        t = ("PERSON DETECTED AT ",time.asctime())
        log = open("log.txt", "a")
        log.writelines(t)
        log.write('\n')
        log.close()
    if MAG==1: #if MAG switch is high write to log file
        t = ("MAG OPEN AT ",time.asctime())
        log = open("log.txt", "a")
        log.writelines(t)
        log.write('\n')
        log.close()

