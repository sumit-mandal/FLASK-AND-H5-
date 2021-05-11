#in this file we make connection between drive and the simulator
import socketio
import eventlet
from flask import Flask
import numpy as np
from keras.models import load_model
import base64
import cv2
from io import BytesIO
from PIL import Image

sio = socketio.Server()
#socket is used to perform realtime communication between client and
#the Server. We use as middleware to dispatch traffic to socket.io webapplication



app = Flask(__name__)#'__main__'
speed_limit = 10


def img_preprocess(img):
    img = img[60:135,:,:]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img,  (3, 3), 0)
    img = cv2.resize(img, (200, 66))
    img = img/255
    return img #we have copied this function from colab behavioural_cloning



@sio.on('telemetry')#registering event handler
def telemetry(sid,data):
    speed = float(data['speed'])
#we are listening for updates that eill be sent to telemetry from the simulator
    image = Image.open(BytesIO(base64.b64decode(data['image'])))#obtaining current image. it is base64 encoded.Then decoding it
     # we need to use a buffer module to mimic our data like a normal file which we can further use for processing we use BytesIO for this
    image =np.asarray(image) #converting image into array
    image = img_preprocess(image)
    image = np.array([image])
    steering_angle = float(model.predict(image))
    throttle = 1.0-speed/speed_limit #initial speed is, 0 , therefore 0/10 = 0. SO throttle will begin by 1.The car will then keep speeding up.
    #And so how does this ensure that our car doesn't surpass the speed limits well the initial speed is going to be zero.
    # as 0/10 = 0. so throttle will start from 1 and speed increases by the time it reaches 10. then 1- 10/10 =1 -1 = 0. thus enforcing constant speed
    print('{} {} {}'.format(steering_angle, throttle, speed))

    send_control(steering_angle,throttle)






@sio.on('connect')
def connect(sid, environ):
    print('Connected')
    send_control(0, 0)

def send_control(steering_angle, throttle):
    sio.emit('steer', data = {
        'steering_angle': steering_angle.__str__(),
        'throttle': throttle.__str__()
    })


if __name__ == '__main__':
    model = load_model('model.h5')#loading the model
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app) #4567 is port and '' is ip address
    #requests will be sent to app
