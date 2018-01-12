# -*- encoding: UTF-8 -*-
""" Say 'hello, you' each time a human face is detected

"""

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

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
                good = raw_input("I detected that " + faceLabel + " is there. Am I right? [y/n]")
                self.tts.say("I detected that " + faceLabel + " is there. Am I right? [y/n]")
                
                if(good == "y"):
                    memory.unsubscribeToEvent("FaceDetected", "HumanGreeter", "onFaceDetected")
                    self.conversation(faceLabel)
                else:
                    good = raw_input("Would you like me to try to detect you again? You can manually input your name otherwise. [y/n]")
                    self.tts.say("Would you like me to try to detect you again? You can manually input your name otherwise. [y/n]")
                    
                    if(good != "y"):
                        name = raw_input("Enter your name")
                        self.tts.say("Enter your name")
                        
                        memory.unsubscribeToEvent("FaceDetected", "HumanGreeter", "onFaceDetected")
                        self.conversation(name)
                
                
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
        ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    
        while(True):
            request = ai.text_request()
    
            request.lang = 'en'  # optional, default value equal 'en'
        
            #request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
    
            request.query = raw_input()
            #print(request.query)
        
            response = request.getresponse()
            
            answer = response.read()
            start_index = answer.find( '"speech": ' )
            start_index += 11
            end_index = answer.find( '"', start_index )
            
            substring = answer[start_index:end_index]
            
            #print(start_index)
            #print(end_index)
            
            print(">" + substring)




def main():
    """ Main entry point

    """
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

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)



if __name__ == "__main__":
    main()