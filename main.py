import RPi.GPIO as GPIO
import time
import glob
import os
from picamera import PiCamera
from dominate import document
from dominate.tags import *

camera = PiCamera()
camera.framerate = 15

#Create a glob of all video & photos
photos = glob.glob('media/photos/*.jpg')
videos = glob.glob('media/videos/*.mp4')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)         #Read output from PIR motion sensor
GPIO.setup(13, GPIO.IN)         #Read output from magnetic door switch


def snapshot():
    local = "/var/www/html/media/photos/" + str(time.asctime()) + ".jpg"
    camera.capture(local)

def vidClip():
    local = "/var/www/html/media/videos/" + str(time.asctime()) + ".h264"
    camera.start_recording(local)
    time.sleep(5)
    camera.stop_recording()
    os.system('for i in /var/www/html/media/videos/*.h264; do ffmpeg -i "$i" "${i%.*}.mp4"; done ; rm /var/www/html/media/videos/*.h264') #Convert H264 files to mp4 for web play

def update_web(): #Update the webpage with new images
    with document(title='Library') as doc:
        meta(name="viewport", content="width=device-width", scale="1.0")
        
        h1('Photos')
        for path in photos:
            humanReadPath = path.replace("media/photos/","")
            humanReadPath = humanReadPath.replace(".jpg","")
            div(h4(humanReadPath))
            div(img(src=path), _class='photo')

        h1('Videos')
        for path in videos:
            humanReadPath = path.replace("media/videos/","")
            humanReadPath = humanReadPath.replace(".mp4","")
            div(h4(humanReadPath))
            div(video(src=path, controls="controls"), _class='video')



    with open('/var/www/html/library', 'w') as f:
        f.write(doc.render())

def write_to_file(t): #Append warning message to log file
    log = open("/var/www/html/log.txt", "a")
    log.writelines(t)
    log.write('\n')
    log.close()
    
    
#main
while True:
    camera.start_preview()
    PIR=GPIO.input(11)
    MAG=GPIO.input(13)
    t = "NONE"
    local = ""
    time.sleep(1)

    if PIR==1 or MAG==1:

        if PIR==1 and MAG==1: #if PIR sensor & MAG switch is high
            t = ("PERSON DETECTED AND MAG OPEN AT ",time.asctime())

        elif PIR==1: #if PIR sensor is high write to log file
            t = ("PERSON DETECTED AT ",time.asctime())
            

        elif MAG==1: #if MAG switch is high write to log file
            t = ("MAG OPEN AT ",time.asctime())

        write_to_file(t)
        snapshot()
        time.sleep(0.1)
        vidClip()
        camera.stop_preview()
        update_web()
