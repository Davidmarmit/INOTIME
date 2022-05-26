import time
import pygame
import random
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import os
from random import randint

from Obstacle import Obstacle
from Photo import Photo

from Shadow import Shadow

global img_count


def mp_segmentation(photo):
    # For static img:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    BG_COLOR = (255, 255, 255)  # white
    with mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.6) as body_seg:
        try:
            image = cv2.imread(photo.get_original_path())

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
            print("Error: No pose detected in " + photo.get_name())
            return "no"

        return output_image


def load_images_from_folder(folder):
    images = []
    img_count = 0
    for filename in os.listdir(folder):

        img = cv2.imread(os.path.join(folder, filename))

        if img is not None:
            img_count += 1
            images.append(Photo(filename, os.path.join(folder, filename)))

    return images


def put_together(photos):
    positionsx = [-50, 800, 400, 600, 600]
    positionsy = [50, 0, 100, 0, 500]

    background = Image.open("background.jpg")
    background = background.resize((int(1920 / 1.5), int(1080 / 1.5)))

    bg_w, bg_h = background.size
    i = 0
    for photo in photos:
        img = Image.open('shadows/' + photo.get_name() + '.png')
        img_w, img_h = img.size
        img = img.resize((int(img_w / 3), int(img_h / 3)))
        img_w, img_h = img.size
        # offset = ((bg_w - img_w) // random.randint(1, 9), (bg_h - img_h) // random.randint(1, 9))
        offset = positionsx[i], positionsy[i]
        i += 1
        background.paste(img, offset, img)

    background.save('out.png')
    immm = cv2.imread('out.png', 1)
    cv2.imshow('Script 3', immm)
    cv2.waitKey(0)


def play_scene(shadows):
    positions_x = [-50, 800, 400, 600, 600]
    positions_y = [50, 0, 100, 0, 500]
    pygame.display.set_caption("INOTIME")
    # set_background()

    icon = pygame.image.load("logo.png").convert_alpha()
    pygame.display.set_icon(icon)


# OBSTACLES
def create_obstacles_map1():
    obstacles.add(Obstacle(screen, 1920, 100, 0, 950))  # Horizontal Bottom
    obstacles.add(Obstacle(screen, 1920, 100, 0, 0))  # Horizontal top
    obstacles.add(Obstacle(screen, 100, 1000, 100, 0))  # Vertical left
    obstacles.add(Obstacle(screen, 100, 1000, 1700, 0))  # Vertical right


def get_shadow():
    photos = load_images_from_folder("img")
    for photo in photos:
        image = mp_segmentation(photo)
        if image == "no":
            print("Borrant imatge...")
            print("Borrant " + str(img_count))
            img_count -= 1
            os.system("cd img && del imatge" + str(img_count) + ".jpg")
            os.system("cd shadows && del imatge" + str(img_count) + ".png")
            break
        else:
            blurred_mask = cv2.medianBlur(image, 11)
            frame = cv2.cvtColor(blurred_mask, cv2.COLOR_BGR2BGRA)
            frame[np.all(frame == [255, 255, 255, 255], axis=2)] = [0, 0, 0, 0]
            # frame[np.all(frame == [10], axis=2)] = [255, 0, 0]

            # frame[np.where((frame == [0, 0, 0, 0]).all(axis=1))] = [0, 0, 255, 255]
            cv2.imwrite('shadows/' + photo.get_name() + '.png', frame)


def start_pygame():
    array_shadows = []
    pygame.init()
    clock = pygame.time.Clock()
    create_obstacles_map1()

    # Creating a boolean variable that
    # we will use to run the while loop
    run = True

    start = time.time()

    end = time.time()
    print(end - start)

    for photo in edited_photos:
        array_shadows.append(Shadow(screen, 200, 700, photo.get_original_path(), obstacles))

    ss = False
    change_every_x_milliseconds = 5000.
    current_color = array_color[0]
    while run:
        new_images = load_images_from_folder("shadows")
        if len(edited_photos) != len(new_images):
            array_shadows.append(
                Shadow(screen, 200, 700, new_images[len(new_images) - 1].get_original_path(), obstacles))
        for ob in obstacles:
            ob.update_obstacle()
        for shadow in array_shadows:

            # STATIC FOTO DURING 5 SECS
            if not ss and time.time() - start >= randint(2, 5):
                shadow.set_shadow()
                ss = True
            if ss:
                shadow.move(array_shadows)
            else:
                shadow.set_shadow()

            # TIMER
            if time.time() - start >= 5:
                start = time.time()

            shadow.fill(pygame.Color(current_color))
            if current_color == (255, 255, 255):
                array_shadows.remove(shadow)
            else:
                current_color = shadow.fade_color(current_color)

        # Setting the framerate to 60fps
        clock.tick(60)
        # Updating the display surface
        pygame.display.update()
        # Filling the window with white color
        screen.fill((255, 255, 255))


if __name__ == '__main__':
    img_count = 0
    # COLOR ARRAY
    array_color = [(207, 92, 54), (202, 103, 2), (238, 155, 0), (255, 207, 0), (73, 167, 155), (10, 147, 150),
                   (0, 96, 115), (0, 52, 89), (0, 18, 25), (52, 58, 64), (173, 181, 189), (218, 221, 223),
                   (255, 255, 255)]
    baseColor = (187, 62, 3)  # ORANGE
    screen = pygame.display.set_mode((1920, 1080))
    obstacles = pygame.sprite.Group()
    get_shadow()
    edited_photos = load_images_from_folder("shadows")
    # mirar la size de shadows
    start_pygame()  # adjuntarli l'array d'imatges o d'objectes shadow
    # if hi ha imatge nova afegir al pygame
