# -*- encoding: UTF-8 -*-

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

from Tkinter import *

import apiai

#168.229.109.34

CLIENT_ACCESS_TOKEN = '1801b5eb14204841bc316201153a8bf7'

NAO_IP = "10.11.26.173"


# Global variable to store the HumanGreeter module instance
HumanGreeter = None
memory = None
isTalking = False
isReady = False
answer = "n"
numTimes = 0

student_access_codes = {}

def check_name():
    global answer
    global isReady
    
    answer = e.get()
    e.delete(0, 'end')
    isReady = True

class HumanGreeterModule(ALModule):
    """ A simple module able to react
    to facedetection events

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
        global isTalking
        global numTimes
        if(isTalking):
            return
        
        isTalking = True

        print("found a face")
        
        try:
            infos = value[1]
            faceInfo = infos[0]
            extraInfo = faceInfo[1]
            faceLabel =  extraInfo[2]
            if(faceLabel != ""):
                
                print(faceLabel)
                
                w['text'] = "I detected that " + faceLabel + " is there. Am I right? [y/n]"
                b['command'] = check_name
                
                self.tts.say("I detected that " + faceLabel + " is there. Am I right?")
                
                global answer
                global isReady
                
                while not isReady:
                    time.sleep(0.05)
                    
                isReady = False
                
                if(answer.lower() == "y"):
                    memory.unsubscribeToEvent("FaceDetected", "HumanGreeter")
                    self.conversation(faceLabel)
                else:
                    w['text'] = "Would you like me to try to detect you again? You can manually input your name otherwise. [y/n]"
                    self.tts.say("Would you like me to try to detect you again? You can manually input your name otherwise.")
                    
                    while not isReady:
                        time.sleep(0.05)
                         
                    isReady = False
                                        
                    if(answer.lower() != "y"):
                        w['text'] = "Enter your name"
                        self.tts.say("Enter your name")
                        
                        while not isReady:
                            time.sleep(0.05)
                         
                        isReady = False
                        
                        memory.unsubscribeToEvent("FaceDetected", "HumanGreeter")
                        self.conversation(answer)
            elif numTimes >= 10:
                w['text'] = "Would you like me to try to detect you again? You can manually input your name otherwise. [y/n]"
                self.tts.say("I haven't been able to detect a specific person. Would you like me to try to detect you again? You can manually input your name otherwise.")
                
                numTimes = 0
                
                while not isReady:
                    time.sleep(0.05)
                     
                isReady = False
                                    
                if(answer.lower() != "y"):
                    w['text'] = "Enter your name"
                    self.tts.say("Enter your name")
                    
                    while not isReady:
                        time.sleep(0.05)
                     
                    isReady = False
                    
                    memory.unsubscribeToEvent("FaceDetected", "HumanGreeter")
                    self.conversation(answer)
            else:
                w['text'] = "Looking for faces"
                numTimes += 1
                
                   
        except IndexError:
            print("Index error")
        
        isTalking = False
        
    def conversation(self, name):
        name = name.lower()
        if name in list(student_access_codes.keys()) : 
            CLIENT_ACCESS_TOKEN = student_access_codes[name]
        else:
            w['text'] = "This name doesn't have an access token associated with it. Please check the access token file and restart the program"
            self.tts.say("This name doesn't have an access token associated with it. Please check the access token file and restart the program!")
            return
        
        global isReady
        
        w['text'] = "Hello!"
        self.tts.say("Hello!")
        
        ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
        
        while(True):
            request = ai.text_request()
    
            request.lang = 'en'  # optional, default value equal 'en'
        
            #request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
            
            while not isReady:
                time.sleep(0.05)
    
            isReady = False
    
            request.query = answer
            #print(request.query)
        
            response = request.getresponse()
            
            reply = response.read()
            start_index = reply.find( '"speech": ' )
            start_index += 11
            end_index = reply.find( '"', start_index )
            
            substring = reply[start_index:end_index]
            
            #print(start_index)
            #print(end_index)
            
            w['text'] = substring
            self.tts.say(substring)
            print(">" + substring)




def ip_connect():
    """ Main entry point

    """
    w['text'] = "Connecting..."
    NAO_IP = e.get()
    e.delete(0, 'end')
    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=NAO_IP,
        pport=9559)

    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port

    w['text'] = "Looking for faces"
    # Warning: HumanGreeter must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global HumanGreeter
    HumanGreeter = HumanGreeterModule("HumanGreeter")


accessCodeFile = open("student_access_codes.txt", "r")
associations = accessCodeFile.readlines()
for line in associations:
    student,code = line.split(" ")  
    student_access_codes[student] = code
    print student
    print code

root = Tk()

w = Label(root, text = "Enter your robot's IP")
w.pack()

e = Entry(root)
e.pack()
e.focus_set()

b = Button(root,text='Next',command=ip_connect)
b.pack(side='bottom')

root.mainloop()
