import pyrebase
from datetime import datetime

firebaseConfig = {"apiKey": "AIzaSyAdNxdx-VKLVy1bT_R86p2GPlIs59jSH_0",
                  "authDomain": "instalacions-interactives.firebaseapp.com",
                  "databaseURL": "https://instalacions-interactives-default-rtdb.europe-west1.firebasedatabase.app",
                  "projectId": "instalacions-interactives",
                  "storageBucket": "instalacions-interactives.appspot.com",
                  "messagingSenderId": "1013681284704",
                  "appId": "1:1013681284704:web:cfcce9b84960e132784505"
                  }

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()


# Define of function that upload the image to the Firebase Database
def upload_img(name):
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
    storage.child("images").child("image_" + dt_string + ".png").put(name)


# Define of function that upload the video to the Firebase Database
def upload_video(dt_string):
    storage.child("videos").child("video_" + dt_string + ".mp4").put("videos/" + dt_string + ".h264")
