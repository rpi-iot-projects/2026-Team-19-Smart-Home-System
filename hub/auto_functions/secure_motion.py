"""
This code reads data from a HC-SR501 motion sensor and saves images to
a local "images" filder when motion is detected.


Refrence tutorial for learn RasPi camera implentation:
    https://projects.raspberrypi.org/en/projects/getting-started-with-picamera
"""


from gpiozero import MotionSensor
from picamera2 import Picamera2
from pathlib import Path
from time import sleep

pir = MotionSensor(4)
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()
sleep(2)

folder = Path.home() / "Desktop" / "images"
folder.mkdir(exist_ok=True)

number = 1
while (folder / f"image_{number}.jpg").exists():
    number += 1

# picture is taken a at the time that motion is detected
while True:
    pir.wait_for_motion()
    print("Motion Sensed! Want a picture?")

    name = f"image_{number}.jpg"
    camera.capture_file(str(folder / name))

    print(f"Image saved as {name}")

    number += 1
    pir.wait_for_no_motion()