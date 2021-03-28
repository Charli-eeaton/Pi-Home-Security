import RPi.GPIO as GPIO
import time
import os
import glob
from dominate import document
from dominate.tags import *

photos = glob.glob('media/photos/*.jpg')
videos = glob.glob('media/videos/*.mp4')
snapshot = 'DATE=$(date +"%Y-%m-%d_%H:%M.%S") && fswebcam -r 1280x720 /var/www/html/media/photos/$DATE.jpg' #Take snapshot 
vidClip = 'DATE=$(date +"%Y-%m-%d_%H:%M.%S") && ffmpeg -f v4l2 -framerate 7 -video_size 640x480 -i /dev/video0 -t 10 /var/www/html/media/videos/$DATE.mp4' #Take 30 second video clip

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)         #Read output from PIR motion sensor
GPIO.setup(13, GPIO.IN)         #Read output from magnetic door switch


def update_web(): #Update the webpage with new images
    with document(title='Library') as doc:
        h1('Photos')
        meta(name="viewport", content="width=device-width", scale="1.0")
        for path in photos:
            humanReadPath = path.replace("media/photos/","")
            humanReadPath = humanReadPath.replace(".jpg","")
            div(h4(humanReadPath))
            div(img(src=path, width="320", height="180"), _class='photo')

        h1('Videos')
        for path in videos:
            humanReadPath = path.replace("media/videos/","")
            humanReadPath = humanReadPath.replace(".mp4","")
            div(h4(humanReadPath))
            div(video(src=path, width="640", height="480", controls="controls"), _class='video')

    with open('/var/www/html/library.html', 'w') as f:
        f.write(doc.render())

def write_to_file(t): #Append warning message to log file
    log = open("/var/www/html/log.txt", "a")
    log.writelines(t)
    log.write('\n')
    log.close()
    
    
#main
while True:
    PIR=GPIO.input(11)
    MAG=GPIO.input(13)
    t = "NONE"
    time.sleep(1)

    if PIR==1 or MAG==1:

        if PIR==1 and MAG==1: #if PIR sensor & MAG switch is high
            t = ("PERSON DETECTED AND MAG OPEN AT ",time.asctime())

        elif PIR==1: #if PIR sensor is high write to log file
            t = ("PERSON DETECTED AT ",time.asctime())
            

        elif MAG==1: #if MAG switch is high write to log file
            t = ("MAG OPEN AT ",time.asctime())

        write_to_file(t)
        os.system(snapshot)
        time.sleep(0.1)
        os.system(vidClip)
        update_web()
