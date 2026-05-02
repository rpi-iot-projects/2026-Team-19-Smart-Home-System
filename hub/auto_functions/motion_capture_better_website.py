# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 22:06:05 2026

@author: Emerson


This code hosts the livestream from the RasPi on the local network,
    so only those on the network can see the feed
    
I modified website.py by combining it with secure_motion.oy logic.
This way, the website also displays the motion capture images.
I implemented this so we could display the the motion capture images without 
    a monitier, because we were not provided a moniter during the live demo.
    
I also changed the display of the site and mirrored/fliped the images
    since the camera can only be comfortably be placed upsidedown & backwards.
    
    
    
Code Reference & sources:
# from https://randomnerdtutorials.com/raspberry-pi-mjpeg-streaming-web-server-picamera2/
# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-mjpeg-streaming-web-server-picamera2/
# Mostly copied from https://picamera.readthedocs.io/en/release-1.13/recipes2.html
# Run this script, then point a web browser at http:<this-ip-address>:7123
# Note: needs simplejpeg to be installed (pip3 install simplejpeg).
"""


from gpiozero import MotionSensor
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from libcamera import Transform

import io
import logging
import socketserver
from http import server
from threading import Condition, Thread, Lock
from datetime import datetime
from time import sleep




""" set up """
PORT = 7123
PIR_PIN = 4
MAX_IMAGES_ON_SITE = 20
pir = MotionSensor(PIR_PIN)
snapshots = []
snapshots_lock = Lock()


""" livestreaming code from camera tutorial"""
# livestream
class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

PAGE = """\
<html>
<head>
<title>Motion Camera Website</title>
<style>
body {
    font-family: Arial;
    background: #111;
    color: white;
    text-align: center;
}
img {
    border: 3px solid white;
    margin: 10px;
}
.snapshot {
    width: 320px;
}
</style>
</head>

<body>
<h1>Raspberry Pi Motion Camera</h1>

<h2>Live Stream</h2>
<img src="/stream.mjpg" width="640" height="480">

<h2>Motion Detected Images</h2>
<div id="gallery"></div>

<script>
function updateGallery() {
    fetch("/gallery")
    .then(response => response.text())
    .then(html => {
        document.getElementById("gallery").innerHTML = html;
    });
}

setInterval(updateGallery, 2000);
updateGallery();
</script>

</body>
</html>
"""


""" 
I modified the livestreaming logic from the tutorial in order to display
snapshots from the moments when movement is detected by the motion sensor
"""
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        global output  #added this
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()
        elif self.path == "/index.html":
            content = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Age", 0)
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except Exception as e:
                logging.warning("Removed streaming client %s: %s", self.client_address, str(e))
        
        # MODIFIED CODE FOR MOTION CAPTURE
        # Here, i aded an extra condition to to set up a place for each image to go
        # I go through each image to give it a label and set up the html
        elif self.path == "/gallery":
            with snapshots_lock:
                html = ""
                for i, item in enumerate(snapshots):
                    html += f"""
                    <div>
                        <p>{item["time"]}</p>
                        <img class="snapshot" src="/snapshot/{i}.jpg">
                    </div>
                    """
            #I followed the image desription settings in the totorial for formatting
            content = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)

        # MORE MODIFIED CODE FOR MOTION CAPTURE
        # Here, i send each new image to the website
        #I keep the tutorials error checking & sending
        elif self.path.startswith("/snapshot/"):
            try:
                index_text = self.path.replace("/snapshot/", "").replace(".jpg", "")
                index = int(index_text)

                with snapshots_lock:
                    frame = snapshots[index]["frame"]
                
                #I followed the image desription settings in the totorial for formatting
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", len(frame))
                self.end_headers()
                self.wfile.write(frame)

            except:
                self.send_error(404)
                self.end_headers()

        else:
            self.send_error(404)
            self.end_headers()


""" same as website.py """
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

""" 
Here, I added the code

"""
def motion_loop():
    global snapshots

    while True:
        pir.wait_for_motion()
        print("Motion detected!")

        # pics should be upsidedown and mirrored
        with output.condition:
            frame = output.frame

        # same basic display as livestram
        if frame is not None:
            t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # now with motion captures
            with snapshots_lock:
                snapshots.insert(0, {"time": t,"frame": frame})

                snapshots = snapshots[:MAX_IMAGES_ON_SITE]
            print("Motion Detected! Sending pic")
        pir.wait_for_no_motion()


picam2 = Picamera2()

"""make camera upside down and mirrored"""
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}, transform=Transform(hflip=0, vflip=1)))
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

#I have it sleep so it doesnt take pictures too fast
sleep(2)

""" check for motion with thread """
Thread(target=motion_loop, daemon=True).start()


""" same launching logic as website.py"""
try:
    address = ("", PORT)
    website = StreamingServer(address, StreamingHandler)
    website.serve_forever()
finally:
    picam2.stop_recording()