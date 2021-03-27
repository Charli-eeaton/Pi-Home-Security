import RPi.GPIO as GPIO
import time
import os

import glob
from dominate import document
from dominate.tags import *

photos = glob.glob('media/photos/*.jpg')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)         #Read output from PIR motion sensor
GPIO.setup(13, GPIO.IN)         #Read output from magnetic door switch

snapshot = 'DATE=$(date +"%Y-%m-%d_%H:%M.%S") && fswebcam -r 1280x720 /var/www/html/media/photos/$DATE.jpg' #Take snapshot 

def update_web(photos): #Update the webpage with new images
    with document(title='Library') as doc:
        h1('Photos test')
        meta(name="viewport", content="width=device-width", scale="1.0")
        for path in photos:
            humanReadPath = path.replace("media/photos/","")
            humanReadPath = humanReadPath.replace(".jpg","")
            div(h4(humanReadPath))
            div(img(src=path, width="320", height="180"), _class='photo')

    with open('library.html', 'w') as f:
        f.write(doc.render())

def write_to_file(t): #Append warning message to log file and take snapshot
    log = open("log.txt", "a")
    log.writelines(t)
    log.write('\n')
    log.close()
    os.system(snapshot)
    

while True:
    PIR=GPIO.input(11)
    MAG=GPIO.input(13)
    time.sleep(1)

    if PIR==1 or MAG==1:
        if PIR==1: #if PIR sensor is high write to log file
            t = ("PERSON DETECTED AT ",time.asctime())
            write_to_file(t)
            update_web(photos)

        if MAG==1: #if MAG switch is high write to log file
            t = ("MAG OPEN AT ",time.asctime())
            write_to_file(t)
            update_web(photos)
