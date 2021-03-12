import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(13, GPIO.IN)         #Read output from magnetic door switch

while True:
    i=GPIO.input(13)
    if i==0:                 #When output from motion sensor is LOW
        print ("CLOSED",i)
        time.sleep(0.1)
    elif i==1:               #When output from motion sensor is HIGH
        print ("OPEN",i)
        time.sleep(0.1)

