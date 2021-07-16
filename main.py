import RPi.GPIO as GPIO
import socketserver
import logging
import time
import glob
import os
import io
#import picamera
from threading import Condition
from picamera import PiCamera
from dominate import document
from dominate.tags import *
from http import server

PAGE="""\
<html>
<center><img src="stream.mjpg" width="720" height="480"></center>
</body>
</html>
"""

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

camera = PiCamera()
camera.framerate = 24
camera.resolution='720x480'

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
    with document(title='library') as doc:
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

    if PIR==0 and MAG==0:
        print("Nope Nobody")
        with camera:
            output = StreamingOutput()
            camera.start_recording(output, format='mjpeg')
            try:
                address = ('', 8000)
                server = StreamingServer(address, StreamingHandler)
                server.serve_forever()
            finally:
                camera.stop_recording()

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

