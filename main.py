import socket
import mediapipe as mp
import numpy as np
import cv2
from PIL import Image
from bbddFirebase import upload_img

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("192.168.1.46", 4444))
server.listen()
print("Servidor creat.")


# Function thats edits the image, making it to only show the silhouette of the subject
def edit_image(img):
    # mediapipe body segmentation:
    mp_pose = mp.solutions.pose
    bg_colour = (255, 255, 255)  # white
    mask_colour = (10, 10, 10)  # dark grey
    with mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.6) as body_seg:
        try:
            mask_condition = np.stack((body_seg.process(img).segmentation_mask,) * 3, axis=-1) > 0.1
            fg_image = np.zeros(img.shape, dtype=np.uint8)
            fg_image[:] = mask_colour
            bg_image = np.zeros(img.shape, dtype=np.uint8)
            bg_image[:] = bg_colour
            masked_image = np.where(mask_condition, fg_image, bg_image)
            blurred_mask = cv2.medianBlur(masked_image, 11)
            img_png = cv2.cvtColor(blurred_mask, cv2.COLOR_BGR2BGRA)
            img_png[np.all(img_png == [255, 255, 255, 255], axis=2)] = [0, 0, 0, 0]
            path_edit = "pepe.png"
            cv2.imwrite("edit/" + path_edit, img_png)
            return path_edit
        # If no person has been detected, we control the exception thrown out.
        except TypeError:
            print("No s'ha detectat cap persona. ")
            return "no"


# Function that shows the edited image while blending it with the background
def show_edited_img(png_path, bg_path):
    img = Image.open("edit/" + png_path)
    img_w, img_h = img.size
    img = img.resize((int(img_w / 2), int(img_h / 2)))
    background = Image.open(bg_path)
    background = background.resize((int(1920 / 1.5), int(1080 / 1.5)))
    img_w, img_h = img.size
    bg_w, bg_h = background.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)  # background image center
    background.paste(img, offset, img)  # pastes the png image on the background center
    background.save("final/" + png_path)
    upload_img("final/" + png_path)
    bkg = cv2.imread("final/" + png_path)
    cv2.imshow('Output', bkg)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        while True:
            # Socket connection that recieves the image from the raspberry pi 4
            print("Esperant connexions...")
            client_socket, client_address = server.accept()

            file = open('img/imatge.jpg', "wb+")
            image_chunk = client_socket.recv(2048)

            while image_chunk:
                file.write(image_chunk)
                image_chunk = client_socket.recv(2048)

            file.close()
            image = cv2.imread("img/imatge.jpg")
            path = edit_image(image)
            if path != "no":
                show_edited_img(path, "background/background.jpg")

    except KeyboardInterrupt:
        print("Tancant servidor.")
        server.close()
