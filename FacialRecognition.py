# -*- encoding: UTF-8 -*- 
# This test demonstrates how to use the ALFaceDetection module.
# Note that you might not have this module depending on your distribution
#
# - We first instantiate a proxy to the ALFaceDetection module
#     Note that this module should be loaded on the robot's naoqi.
#     The module output its results in ALMemory in a variable
#     called "FaceDetected"

# - We then read this ALMemory value and check whether we get
#   interesting things

import time

from naoqi import ALProxy

IP = "10.31.81.136"  # Replace here with your NaoQi's IP address.
PORT = 9559

# Create a proxy to ALFaceDetection
try:
    faceProxy = ALProxy("ALFaceDetection", IP, PORT)
except Exception, e:
    print "Error when creating face detection proxy:"
    print str(e)
    exit(1)

time.sleep(10)

print "Face saving beginning"

faceProxy.setRecognitionEnabled(False)
faceProxy.setTrackingEnabled(False)

faceRecognized = faceProxy.learnFace("Aakash")

if(faceRecognized):
    print "Face saved"
else:
    print "Face not saved"
    exit(1)

learnedFaces = faceProxy.getLearnedFacesList()

for face in learnedFaces:
    print face
