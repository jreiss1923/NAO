# -*- encoding: UTF-8 -*- 

import time

from naoqi import ALProxy

IP = "10.11.25.212"  # Replace here with your NaoQi's IP address.
PORT = 9559

# Create a proxy to ALFaceDetection
try:
    faceProxy = ALProxy("ALFaceDetection", IP, PORT)
except Exception, e:
    print "Error when creating face detection proxy:"
    print str(e)
    exit(1)

faceProxy.clearDatabase() # COMMENT THIS OUT AFTER YOU'VE DONE IT ONCE

time.sleep(10)

print "Face saving beginning"

#faceProxy.setRecognitionEnabled(False)
#faceProxy.setTrackingEnabled(False)

faceRecognized = faceProxy.learnFace("Ohm")

if(faceRecognized):
    print "Face saved"
else:
    print "Face not saved"
    exit(1)

learnedFaces = faceProxy.getLearnedFacesList()

for face in learnedFaces:
    print face
