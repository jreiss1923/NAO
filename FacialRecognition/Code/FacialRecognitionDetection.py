# -*- encoding: UTF-8 -*-

import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

from Tkinter import *

import apiai

# default values, not important
CLIENT_ACCESS_TOKEN = ''
NAO_IP = ''
PORT = 9559 # default port for the NAO robot, don't change unless you know what you're doing

# global vars
HumanGreeter = None # the face detection module, needed to facilitate the face detected event
memory = None # the NAO memory unit, used to subscribe to events
inFaceDetected = False # whether or not the NAO is currently in the face detected event
enteredNewResponse = False # used to determine whether the user has entered a new response yet
userResponse = "n" # used to track user responses
numTimes = 0 # used to determine how many times a face is detected display_text/o a specific name (if this happens too much, a failsafe will be triggered)
student_access_codes = {} # a dictionary that will store the DialogFlow access codes for each student

# this function is used to get new user input
def check_name():
    global userResponse
    global enteredNewResponse
    
    userResponse = text_entry_field.get()
    text_entry_field.delete(0, 'end')
    enteredNewResponse = True

class HumanGreeterModule(ALModule):
    """ A simple module able to react
    to face detection events
    """
    def __init__(self, name):
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy to ALTextToSpeech for later use
        self.tts = ALProxy("ALTextToSpeech")

        # Subscribe to the FaceDetected event:
        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("FaceDetected",
            "HumanGreeter",
            "onFaceDetected")
        
    def onFaceDetected(self, eventName, value, subscriberIdentifier):
        """ This will be called each time a face is
        detected.

        """
        global inFaceDetected
        global numTimes
        
        # we don't want this function to be called multiple times at once
        if(inFaceDetected):
            return
        inFaceDetected = True
        
        try:
            """ this part looks a little rough, but is based on the NAOqi API's description of these 
            face data arrays. The "face label" is the person's name. Visit here if you need clarification:
            http://doc.aldebaran.com/2-1/naoqi/peopleperception/alfacedetection.html#alfacedetection
            """
            infos = value[1]
            faceInfo = infos[0]
            extraInfo = faceInfo[1]
            faceLabel =  extraInfo[2]
            
            """ if a named face is detected, then check whether it is the correct name. If it is, continue
            to the dialogue portion of the program. Otherwise, either try to detect the correct face or prompt
            the user to enter their name manually, based on their preference
            """
            if(faceLabel != ""):
                
                #print(faceLabel)
                
                display_text['text'] = "I detected that " + faceLabel + " is there. Am I right? [y/n]"
                button['command'] = check_name
                
                self.tts.say("I detected that " + faceLabel + " is there. Am I right?")
                
                global userResponse
                global enteredNewResponse
                
                while not enteredNewResponse:
                    time.sleep(0.05)
                    
                enteredNewResponse = False
                
                if(userResponse.lower() == "y"):
                    memory.unsubscribeToEvent("FaceDetected", "HumanGreeter")
                    self.conversation(faceLabel)
                else:
                    display_text['text'] = "Would you like me to try to detect you again? You can manually input your name otherwise. [y/n]"
                    self.tts.say("Would you like me to try to detect you again? You can manually input your name otherwise.")
                    
                    while not enteredNewResponse:
                        time.sleep(0.05)
                         
                    enteredNewResponse = False
                                        
                    if(userResponse.lower() != "y"):
                        display_text['text'] = "Enter your name"
                        self.tts.say("Enter your name")
                        
                        while not enteredNewResponse:
                            time.sleep(0.05)
                         
                        enteredNewResponse = False
                        
                        memory.unsubscribeToEvent("FaceDetected", "HumanGreeter")
                        self.conversation(userResponse)
            # if an unnamed face is detected 10 times in a row, the option will be presented to the user to 
            # either manually input their name or have the robot continue to try to detect them 
            elif numTimes >= 10:
                display_text['text'] = "Would you like me to try to detect you again? You can manually input your name otherwise. [y/n]"
                self.tts.say("I haven't been able to detect a specific person. Would you like me to try to detect you again? You can manually input your name otherwise.")
                
                numTimes = 0
                
                while not enteredNewResponse:
                    time.sleep(0.05)
                     
                enteredNewResponse = False
                                    
                if(userResponse.lower() != "y"):
                    display_text['text'] = "Enter your name"
                    self.tts.say("Enter your name")
                    
                    while not enteredNewResponse:
                        time.sleep(0.05)
                     
                    enteredNewResponse = False
                    
                    memory.unsubscribeToEvent("FaceDetected", "HumanGreeter")
                    self.conversation(userResponse)
            else:
                display_text['text'] = "Looking for faces"
                numTimes += 1
                
                   
        except IndexError:
            print("Index error")
        
        inFaceDetected = False
        
    """ starts a conversation based on the student's DialogFlow conversation set. If none exists, the program will
    end and prompt the user to check the access token file
    """
    def conversation(self, name):
        name = name.lower()
        if name in list(student_access_codes.keys()) : 
            CLIENT_ACCESS_TOKEN = student_access_codes[name]
        else:
            display_text['text'] = "This name doesn't have an access token associated with it. Please check the access token file and restart the program"
            self.tts.say("This name doesn't have an access token associated with it. Please check the access token file and restart the program!")
            return
        
        global enteredNewResponse
        
        display_text['text'] = "Hello!"
        self.tts.say("Hello!")
        
        ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
        
        while(True):
            request = ai.text_request()
    
            request.lang = 'en'  # optional, default value equal 'en'
        
            #request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
            
            while not enteredNewResponse:
                time.sleep(0.05)
    
            enteredNewResponse = False
    
            request.query = userResponse
            #print(request.query)
        
            response = request.getresponse()
            
            reply = response.read()
            start_index = reply.find( '"speech": ' )
            start_index += 11
            end_index = reply.find( '"', start_index )
            
            substring = reply[start_index:end_index]
            
            #print(start_index)
            #print(end_index)
            
            display_text['text'] = substring
            self.tts.say(substring)
            print(">" + substring)



# function to connect to the NAO robot and start the HumanGreeter Module (this will manage the face detection)
def ip_connect():
    display_text['text'] = "Connecting..."
    NAO_IP = text_entry_field.get()
    text_entry_field.delete(0, 'end')
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       NAO_IP,         # parent broker IP
       PORT)       # parent broker port

    display_text['text'] = "Looking for faces"
    # Warning: HumanGreeter must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global HumanGreeter
    HumanGreeter = HumanGreeterModule("HumanGreeter")
    
"""
gets the access codes for the students from a local text file, format:
student1 accesscode1
student2 accesscode2
"""
accessCodeFile = open("student_access_codes.txt", "r")
associations = accessCodeFile.readlines()

""" use this code to test if your text file is reading correctly
for line in associations:
    student,code = line.split(" ")  
    student_access_codes[student] = code
    print student
    print code
"""
# initializes tkinter
root = Tk()

# initializes tkinter elements
display_text = Label(root, text = "Enter your robot's IP")
display_text.pack()

text_entry_field = Entry(root)
text_entry_field.pack()
text_entry_field.focus_set()

button = Button(root,text='Next',command=ip_connect)
button.pack(side='bottom')

# starts the gui
root.mainloop()
