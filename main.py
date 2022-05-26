import signal
import socket
import mediapipe as mp
import numpy as np
import cv2
import os

from numpy import size

from Photo import Photo
from PIL import Image
import random
from bbddFirebase import upload_img

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("192.168.199.32", 4444))
server.listen()
print("Servidor creat.")


def mp_segmentation(photo):
    # For static img:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    BG_COLOR = (255, 255, 255)  # white
    array_color = [(0, 135, 255), (25, 203, 250), (179, 122, 55), (10, 10, 10), (200, 200, 200)]
    with mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.6) as body_seg:
        try:
            image = cv2.imread(photo.get_original_path())
            # results = body_seg.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))  # change bgr to rgb

            # To improve segmentation around boundaries, consider applying a joint
            # bilateral filter to "results.segmentation_mask" with "image".
            condition = np.stack((body_seg.process(image).segmentation_mask,) * 3, axis=-1) > 0.1
            # Generate solid color img for showing the output  segmentation mask.
            fg_image = np.zeros(image.shape, dtype=np.uint8)
            fg_image[:] = array_color[random.randint(0, 4)]
            bg_image = np.zeros(image.shape, dtype=np.uint8)
            bg_image[:] = BG_COLOR
            output_image = np.where(condition, fg_image, bg_image)
        except TypeError:
            print("No s'ha detectat cap persona.")
            return "no"

        return output_image


def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder, filename))

        if img is not None:
            images.append(Photo(filename, os.path.join(folder, filename)))

    return images


def put_together(photos):
    positionsx = [-50, 800, 400, 600, 600]
    positionsy = [50, 0, 100, 0, 500]
    background = Image.open("background/background.jpg")
    background = background.resize((int(1920 / 1.5), int(1080 / 1.5)))

    bg_w, bg_h = background.size
    i = 0
    for photo in photos:
        img = Image.open('shadows/' + photo.get_name() + '.png')
        img_w, img_h = img.size
        img = img.resize((int(img_w / 3), int(img_h / 3)))
        img_w, img_h = img.size
        offset = positionsx[i], positionsy[i]
        i += 1
        background.paste(img, offset, img)

    background.save('out.png')
    immm = cv2.imread('out.png', 1)
    cv2.imshow('Script 3', immm)
    cv2.waitKey(0)


def Signal_Handler(signal, frame):
    print("Tancant servidor.")
    server.close()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, Signal_Handler)
    img_count = 0
    os.system("rmdir /s /q img ")
    os.system("mkdir img")
    os.system("cd shadows && del /s /q *")
    while True:
        # Socket connection that recieves the image from the raspberry pi 4
        print("Esperant connexions...")
        client_socket, client_address = server.accept()
        if img_count > 4:
            os.system("cd img && del imatge" + str(img_count - 5) + ".jpg")
            os.system("cd shadows && del imatge" + str(img_count - 5) + ".png")
        file = open('img/imatge' + str(img_count) + '.jpg', "wb+")
        img_count += 1
        image_chunk = client_socket.recv(2048)

        while image_chunk:
            file.write(image_chunk)
            image_chunk = client_socket.recv(2048)
        file.close()



        photos = load_images_from_folder("img")
        for e in photos:
            print("Foto: " + e.get_name())
        for photo in photos:
            img = mp_segmentation(photo)
            if img == "no":
                print("Borrant imatge...")
                img_count -= 1
                print("Borrant " + str(img_count))
                os.system("cd img && del imatge" + str(img_count) + ".jpg")
                os.system("cd shadows && del imatge" + str(img_count) + ".png")
                # photos.pop(img_count - 1)
                break
            else:
                blurred_mask = cv2.medianBlur(img, 11)
                frame = cv2.cvtColor(blurred_mask, cv2.COLOR_BGR2BGRA)
                frame[np.all(frame == [255, 255, 255, 255], axis=2)] = [0, 0, 0, 0]
                print(photo.get_name())
                cv2.imwrite('shadows/imatge' + str(img_count - 1) + '.png', frame)
        put_together(photos)
