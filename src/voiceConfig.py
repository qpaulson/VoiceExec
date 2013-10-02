#import atexit
#import pyaudio
#import wave
#import audioop
import os
import re
#import urllib2
#import time
import ConfigParser
#import pprint

#from collections import deque
#from subprocess import *


class VoiceConfig:
    def __init__(self):
	INPUT_BLOCK_TIME = 0.05

        self.configuration = ConfigParser.RawConfigParser()
	self.RATE = 44100
	self.CHANNELS = 2
	self.DEVICE = -1

	self.THRESHOLD = 10 #The threshold intensity that defines silence signal (lower than).
	self.SILENCE_LIMIT = 3 #Silence limit in seconds. The max ammount of seconds where only silence is recorded. When this time passes the recording finishes and the file is delivered.

	self.INPUT_FRAMES_PER_BLOCK = int(self.RATE*INPUT_BLOCK_TIME)
	
	self.loadConfig()

    def loadConfig(self):
        print "CONFIG: Loading Configuration File"

        #config = ConfigParser.ConfigParser()
        self.configuration.read( ['conf/voiceExec.conf', os.path.expanduser('~/.voiceExec.conf')] )
        print self.configuration.items( "System Commands" )
        print "CONFIG: Configuration File Loaded"
        #configuration = config
    
	key = "record_rate"
        if ( self.configuration.has_option( "System Config", key )):
    	    self.RATE = int( self.configuration.get( "System Config", key ))
	    print "CONFIG: " + key + " in configuration, setting to: " + str(self.RATE)
        else:
	    print "CONFIG: " + key + " not found, using default: " + str(self.RATE)

	key = "record_device"
        if ( self.configuration.has_option( "System Config", key )):
    	    self.DEVICE = int( self.configuration.get( "System Config", key ))
	    print "CONFIG: " + key + " in configuration, setting to: " + str(self.DEVICE)
        else:
	    print "CONFIG: " + key + " not found, using default: AUTO DETECT"

	key = "record_silence_threshold"
        if ( self.configuration.has_option( "System Config", key )):
    	    self.THRESHOLD = int( self.configuration.get( "System Config", key ))
	    print "CONFIG: " + key + " in configuration, setting to: " + str(self.THRESHOLD)
        else:
	    print "CONFIG: " + key + " not found, using default: " + str(self.THRESHOLD)



    def getConfig(self, string):
    	    keys = self.configuration.items( "System Commands" )
    
	    try:
		    for key,value in keys:
			    #do regex here
			    p = re.compile( key, re.IGNORECASE )
			    print "CONFIG checking: "+ key
			    if p.search( string ):
	 			    print "CONFIG: Matched"
				    cmd = value
    
		    #cmd = configuration.get( "System Commands", string)
		    return cmd 
	    except Exception as e:
		    print e
		    print "Command not found configured: " + string


