# -*- encoding: UTF-8 -*-
""" Say 'hello, you' each time a human face is detected

"""

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

from Tkinter import *

import os.path

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = '1801b5eb14204841bc316201153a8bf7'

NAO_IP = "10.11.26.173"


# Global variable to store the HumanGreeter module instance
HumanGreeter = None
memory = None
isTalking = False
isReady = False
answer = "n"

def check_name():
    global answer
    global isReady
    
    answer = e.get()
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
                
                w['text'] = "I detected that" + faceLabel + " is there. Am I right? [y/n]"
                b['command'] = check_name
                
                self.tts.say("I detected that " + faceLabel + " is there. Am I right?")
                
                global answer
                global isReady
                
                while not isReady:
                    time.sleep(0.1)
                    
                isReady = False
                
                if(answer.toLower() == "y"):
                    memory.unsubscribeToEvent("FaceDetected", "HumanGreeter")
                    self.conversation(faceLabel)
                else:
                    w['text'] = "Would you like me to try to detect you again? You can manually input your name otherwise. [y/n]"
                    self.tts.say("Would you like me to try to detect you again? You can manually input your name otherwise.")
                    
                    while not isReady:
                        time.sleep(0.1)
                         
                    isReady = False
                                        
                    if(answer.toLower() != "y"):
                        w['text'] = "Enter your name"
                        self.tts.say("Enter your name")
                        
                        while not isReady:
                            time.sleep(0.1)
                         
                        isReady = False
                        
                        memory.unsubscribeToEvent("FaceDetected", "HumanGreeter")
                        self.conversation(answer)
                
                
        except IndexError:
            print("Index error")
        
        isTalking = False
        
    def conversation(self, name):
        """
        if faceLabel in tokenlist.keys() : 
            CLIENT_ACCESS_TOKEN = tokenlist[faceLabel]
        else:
            print("Name does not have a conversation set associated with it")
            return
        """
        
        global isReady
        
        w['text'] = "Hello!"
        self.tts.say("Hello!")
        
        ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
        
        while(True):
            request = ai.text_request()
    
            request.lang = 'en'  # optional, default value equal 'en'
        
            #request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
            
            while not isReady:
                time.sleep(0.1)
    
            isReady = False
    
            request.query = answer
            #print(request.query)
        
            response = request.getresponse()
            
            answer = response.read()
            start_index = answer.find( '"speech": ' )
            start_index += 11
            end_index = answer.find( '"', start_index )
            
            substring = answer[start_index:end_index]
            
            #print(start_index)
            #print(end_index)
            
            w['text'] = substring
            self.tts.say(substring)
            print(">" + substring)




def ip_connect():
    """ Main entry point

    """
    NAO_IP = e.get()
    
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


    # Warning: HumanGreeter must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global HumanGreeter
    HumanGreeter = HumanGreeterModule("HumanGreeter")


root = Tk()

w = Label(root, text = "Enter your robot's IP")
w.pack()

e = Entry(root)
e.pack()
e.focus_set()

b = Button(root,text='Next',command=ip_connect)
b.pack(side='bottom')

root.mainloop()
