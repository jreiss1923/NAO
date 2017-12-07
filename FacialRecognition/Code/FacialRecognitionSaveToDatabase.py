# -*- encoding: UTF-8 -*- 

import time

from naoqi import ALProxy

from Tkinter import *

IP = '10.31.85.117'
PORT = 9559
faceProxy = -1;

def ip_connect():
    global e
    global w
    global IP
    global faceProxy
    IP = e.get()
    
    print IP
    
    # Create a proxy to ALFaceDetection
    try:
        faceProxy = ALProxy("ALFaceDetection", IP, PORT)
    except Exception, ex:
        print "Error when creating face detection proxy:"
        print str(ex)
         #exit(1)
    #faceProxy.clearDatabase() 
    e.delete(0, END)
    w['text'] = "Look directly at the robot and enter your name"
    b['command'] = learn_face
        
def learn_face():
    global e
    global w
    global b
    global faceProxy
    name = e.get()
    
    print name
    
    b.pack_forget()
    
    
    
    w['text'] = "Detecting face"
    
    faceRecognized = faceProxy.learnFace(name)

    if(faceRecognized):
        print "Face saved"
        w['text'] = "Face saved"
    else:
        w['text'] = "Face not saved, please try again"
        #exit(1)
        
    learnedFaces = faceProxy.getLearnedFacesList()

    for face in learnedFaces:
        print face
        
    #root.quit()
    
root = Tk()

w = Label(root, text = "Enter your robot's IP")
w.pack()

e = Entry(root)
e.pack()
e.focus_set()

b = Button(root,text='Next',command=ip_connect)
b.pack(side='bottom')

root.mainloop()


#faceProxy.clearDatabase() # COMMENT THIS OUT AFTER YOU'VE DONE IT ONCE

#faceProxy.setRecognitionEnabled(False)
#faceProxy.setTrackingEnabled(False)