import cv2

from azure.cognitiveservices.vision.computervision import ComputerVisionClient


from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time

import io

mainCamera = cv2.VideoCapture(0)

if not mainCamera.isOpened():
    print('Unable to load right camera.')
    mainCamera = None
    exit #camera is mandatory

subscription_key = ""
endpoint = ""

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

while True:

        ret, frame = mainCamera.read()
        image_features = ["objects"]

        encodedframe = cv2.imencode(".jpg", frame)[1].tostring()
        stream = io.BytesIO(encodedframe)

        r = computervision_client.analyze_image_in_stream(stream, visual_features=image_features, details=None, language='en', description_exclude=None, custom_headers=None, raw=False, callback=None)

        if r != None and r.objects != None and r.objects != []:
            for i in r.objects:
                #print (i.object_property)
                r = i.rectangle

                cv2.rectangle(frame, (r.x, r.y), (r.x+r.w, r.y+r.h), (0, 255, 0), 2)
                cv2.putText(frame,i.object_property, (r.x+10, r.y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                cv2.putText(frame,str(round(i.confidence*100,1))+"%", (r.x+10, r.y+50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        cv2.imshow("Analise em Tempo Real", frame)

mainCamera.release()

