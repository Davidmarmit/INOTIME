import os
import signal
import socket

import RPi.GPIO as GPIO
import sys
import time

from picamera import PiCamera
from datetime import datetime

GPIO.setmode(GPIO.BCM)
sensor_trig = 18
sensor_echo = 24
GPIO.setup(sensor_trig, GPIO.OUT)
GPIO.setup(sensor_echo, GPIO.IN)


# It gets the distance between an object and the ultrasonic sensor
def get_distance():
    # turn on/off the sensor trigger
    GPIO.output(sensor_trig, True)
    GPIO.output(sensor_trig, False)

    # Save the start and stop time  to current time
    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(sensor_echo) == 0:
        start_time = time.time()

    while GPIO.input(sensor_echo) == 1:
        stop_time = time.time()

    total_time = stop_time - start_time
    # Operation to get the distance in cm between the sensor and the object
    distance = (total_time * 34300) / 2  # sonic speed= 34300 cm/s

    return distance


# Define of function that detects if there is someone in the defined distance
def detect_people(debug):
    dist = get_distance()
    if debug:
        print("Distance: ", dist)
    if dist < 40:
        print("Detected an object at %.2f cm" % dist)
        return True
    else:
        return False


# Define of function that takes a picture
def send_image(img):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.199.32", 4444))
    file = open(img, "rb")
    image_data = file.read(2048)
    while image_data:
        client.send(image_data)
        image_data = file.read(2048)
    file.close()
    client.close()


def take_photo():
    camera = PiCamera()
    camera.rotation = 180
    # camera.start_preview(alpha=200)
    # camera.start_preview()
    time.sleep(9)
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
    camera.capture("images/" + dt_string + '.jpg')
    camera.stop_preview()
    send_image("images/" + dt_string + '.jpg')
    camera.close()
    print("Photo has been taken!")
    time.sleep(12)


def Signal_Handler(signal, frame):
    print('You pressed Ctrl+C!')
    GPIO.cleanup()
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, Signal_Handler)
    while True:
        time.sleep(1)
        if detect_people(1):
            print("Image starting")
            os.popen("vlc -f --play-and-exit /home/pi/Downloads/video.mp4 > /dev/null 2>&1")  # take_photo()
            take_photo()
            # print("Photo has been taken!")
