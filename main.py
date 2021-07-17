import RPi.GPIO as GPIO
import socketserver
import logging
import _thread
import threading
import picamera
import time
import glob
import os
import io
from threading import Condition
from picamera import PiCamera
from dominate import document
from dominate.tags import *
from http import server

camera = PiCamera()
camera.framerate = 24
camera.resolution='720x480'
address = ('', 8000)

#Create a glob of all video & photos
photos = glob.glob('media/photos/*.jpg')
videos = glob.glob('media/videos/*.mp4')

#Initalise GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.IN)         #Read output from PIR motion sensor
GPIO.setup(40,GPIO.IN)         #Read output from magnetic door switch

#Create webpage for livestreaming
PAGE="""\
<html>
<center><img src="stream.mjpg" width="720" height="480"></center>
</body>
</html>
"""
##Code required for supporting streaming
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

#function for taking a still image
def snapshot():
    local = "/var/www/html/media/photos/" + str(time.asctime()) + ".jpg"#path to save image with current Date & Time added
    camera.capture(local, use_video_port=True) #Use video port option allows snapshots without dropped frames

def vidClip():
    local = "/var/www/html/media/videos/" + str(time.asctime()) + ".h264"#path to save video with current Date & Time added. The Pi can only record in h264, this will need to be converted
    camera.stop_recording()# Stop the stream
    time.sleep(0.5)
    camera.start_recording(local)
    time.sleep(5) #How long of a clip to record
    camera.stop_recording()

    #Resume the livestream after stopping it to record the clip
    camera.start_recording(output, format='mjpeg')

    #Convert H264 files to mp4 for web play 
    os.system('for i in /var/www/html/media/videos/*.h264; do ffmpeg -i "$i" "${i%.*}.mp4"; done ; rm /var/www/html/media/videos/*.h264') 
    



#Update the webpage with new images and video
def update_web(): 
    with document(title='library') as doc:
        meta(name="viewport", content="width=device-width", scale="1.0") #set web page scale to that of the device
        
        h1('Photos') 
        for path in photos: #auto generate web page with all the files in the photos folder
            humanReadPath = path.replace("media/photos/","")
            humanReadPath = humanReadPath.replace(".jpg","")
            div(h4(humanReadPath))
            div(img(src=path), _class='photo')

        h1('Videos')
        for path in videos: #auto generate web page with all the files in the video folder
            humanReadPath = path.replace("media/videos/","")
            humanReadPath = humanReadPath.replace(".mp4","")
            div(h4(humanReadPath))
            div(video(src=path, controls="controls"), _class='video')

    with open('/var/www/html/library', 'w') as f:
        f.write(doc.render())

#Append message to log file on which if any sensors has been tripped
def write_to_file(t): 
    log = open("/var/www/html/log.txt", "a")
    log.writelines(t)
    log.write('\n')
    log.close()

#main
def main():
    camera.start_preview()
    while True:
        time.sleep(1)
        update_web()
        PIR=GPIO.input(8)
        MAG=GPIO.input(40)

        #uncomment no write nobody detected when niether sensor is tripped
        #if PIR==0 and MAG==0:
        #    t = ("Nope Nobody",time.asctime())
            
        #If either sensor is tripped
        if PIR==1 or MAG==1:
            #camera.stop_recording()

            if PIR==1 and MAG==1: #if PIR sensor & MAG switch is high
                t = ("PERSON DETECTED AND MAG OPEN AT ",time.asctime())

            elif PIR==1: #if PIR sensor is high write to log file
                t = ("PERSON DETECTED AT ",time.asctime())
                

            elif MAG==1: #if MAG switch is high write to log file
                t = ("MAG OPEN AT ",time.asctime())

            write_to_file(t)
            snapshot()
            vidClip()


#Start the main thread
_thread.start_new_thread(main, tuple())

#Begin live stream
output = StreamingOutput()  
camera.start_recording(output, format='mjpeg')
server = StreamingServer(address, StreamingHandler)
server.serve_forever()
