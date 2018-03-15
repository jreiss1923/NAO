# -*- encoding: UTF-8 -*- 

from naoqi import ALProxy

from Tkinter import *

# default values, not important
IP = '' 
faceProxy = -1
PORT = 9559 # default port for the NAO robot, don't change unless you know what you're doing

def ip_connect():
    # tkinter display elements
    global text_entry_field 
    global display_text
    
    # setting scope for these vars to global
    global IP
    global faceProxy
    IP = text_entry_field.get()
    
    #print IP
    
    # Create a proxy to ALFaceDetection
    try:
        faceProxy = ALProxy("ALFaceDetection", IP, PORT)
    except Exception, ex:
        print "Error when creating face detection proxy:"
        print str(ex)
        #exit(1)
    #faceProxy.clearDatabase() use this if you need to start clean on a new robot
    text_entry_field.delete(0, END) # clears the entry field
    display_text['text'] = "Look directly at the robot and enter your name"
    button['command'] = learn_face # sets the user up to proceed to the next phase (the face learning)
        
def learn_face():
    # tkinter display elements
    global text_entry_field
    global display_text
    global button
    
    # setting scope for these vars to global
    global faceProxy
    
    # gets name based on user input
    name = text_entry_field.get()
    
    # print name use this to debug whether the name was picked up correctly
    
    # delete button
    button.pack_forget()
    
    # start face learning and notify user of its success
    display_text['text'] = "Detecting face"
    faceRecognized = faceProxy.learnFace(name)
    if(faceRecognized):
        #print "Face saved"
        display_text['text'] = "Face saved"
    else:
        display_text['text'] = "Face not saved, please try again"
        #exit(1)
    
    # use this to see which faces have saved successfully
    """
    learnedFaces = faceProxy.getLearnedFacesList()
    for face in learnedFaces:
        print face
    """
# initializes tkinter    
root = Tk()

#initializes tkinter display elements
display_text = Label(root, text = "Enter your robot's IP")
display_text.pack()

text_entry_field = Entry(root)
text_entry_field.pack()
text_entry_field.focus_set()

button = Button(root,text='Next',command=ip_connect)
button.pack(side='bottom')

#starts the gui
root.mainloop()