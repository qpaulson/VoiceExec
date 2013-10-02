#!/usr/bin/python

import atexit
import pyaudio
import wave
import audioop
import re
import urllib2
import time
import ConfigParser
import pprint
import sys, os, inspect


from collections import deque 
from subprocess import *


cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"src")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

#sys.path.append( os.getcwd() + "src" )
import voiceconfig



p = pyaudio.PyAudio()

def runCommand(cmd):
        p = Popen(cmd, shell=True, stdout=PIPE)
        textString = p.communicate()[0].rstrip()
	return textString


def initStream():
    #open stream

    # List and find the correct input device
    print "========================== DETECTING AVAILABLE AUDIO DEVICES ========================="
    device_index = None
    device_max_rate = vConfig.RATE
    device_max_channels = vConfig.CHANNELS

    for i in range( p.get_device_count() ):
       devinfo = p.get_device_info_by_index(i)
       print( "Device %d: %s"%(i,devinfo["name"]) )
       if ( int( devinfo["maxInputChannels"] ) > 0 ):
	    print( "        * Input Device" )
	    device_index = i
            device_max_rate = int(devinfo["defaultSampleRate"])
            device_max_channels = int(devinfo["maxInputChannels"])

    print "======================================================================================"
    if ( vConfig.DEVICE == -1 ):
        print "Using Detected Input Device: " + str(device_index)
    else:
	device_index = int(vConfig.DEVICE)
	print "Using Configured Input Device: " + str(device_index)

    if ( device_max_rate < vConfig.RATE ):
        print "Setting Record Rate to Device max of: " + str(device_max_rate)
	vConfig.RATE = device_max_rate

    if ( device_max_channels < vConfig.CHANNELS ):
        print "Setting Record Channels to Device max of: " + str(device_max_channels)
	vConfig.CHANNELS = device_max_channels

    print "================================ DEVICE DETAILS ======================================"
    devinfo = p.get_device_info_by_index(device_index)
    pp = pprint.PrettyPrinter(indent=4)    
    pp.pprint( devinfo )
    print "======================================================================================"
   
	
    stream  = p.open(   format = pyaudio.paInt16,
                         channels = vConfig.CHANNELS,
                         rate = vConfig.RATE,
                         input = True,
                         input_device_index = device_index,
                         frames_per_buffer = vConfig.INPUT_FRAMES_PER_BLOCK)
    print stream
    return stream



def listen_for_speech():
    """
    Does speech recognition using Google's speech  recognition service.
    Records sound from microphone until silence is found and save it as WAV and then converts it to FLAC. Finally, the file is sent to Google and the result is returned.
    """


    stream = initStream()

    print "* listening. CTRL+C to finish."
    all_m = []
    data = ''
    #SILENCE_LIMIT = 2
    rel = vConfig.RATE/vConfig.INPUT_FRAMES_PER_BLOCK
    slid_win = deque(maxlen=vConfig.SILENCE_LIMIT*rel)
    started = False
    
    while (True):
        data = stream.read(vConfig.INPUT_FRAMES_PER_BLOCK)
        slid_win.append (abs(audioop.avg(data, 2)))

        if(True in [ x>vConfig.THRESHOLD for x in slid_win]):
            if(not started):
                print "starting record"
            started = True
            all_m.append(data)
        elif (started==True):
            print "finished"
            #the limit was reached, finish capture and deliver
            filename = save_speech(all_m,p)
	    print filename
            stt_google(filename)
            #reset all
            started = False
            slid_win = deque(maxlen=vConfig.SILENCE_LIMIT*rel)
            all_m= []
	    stream = initStream()
            print stream
            print "listening ... again"

    print "* done recording"
    stream.close()
    #p.terminate()


def save_speech(data, p):
    filename = 'output_'+str(int(time.time()))
    # write data to WAVE file
    data = ''.join(data)
    wf = wave.open(filename+'.wav', 'wb')
    wf.setnchannels(vConfig.CHANNELS)
    wf.setsampwidth(p.get_sample_size( pyaudio.paInt16 ))
    #wf.setframerate(RATE)
    wf.setframerate(16000)
    wf.writeframes(data)
    wf.close()
    return filename



def tts_google( string ):
	#this will get the last remnants
	#wget -q -U Mozilla -O "$tmpDir/tmp.mp3" "http://translate.google.com/translate_tts?tl=${lang}&q=$string"
	#cat "$tmpDir/tmp.mp3" >> "$tmpDir/speak.mp3"
    lang_code='en'
    googl_speech_url = 'http://translate.google.com/translate_tts?tl='+lang_code+'&q='+string
    hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7"}
    req = urllib2.Request(googl_speech_url, headers=hrs)
    p = urllib2.urlopen(req)
    
    ## Get the date and play it 



def stt_google(filename):
    #Convert to flac
    print "Converting WAV to FLAC"
    os.system(FLAC_CONV+ filename+'.wav')
    f = open(filename+'.flac','rb')
    flac_cont = f.read()
    f.close()
    print "Complete"

    #post it
    print "------------------------ Posting FLAC to Google --------------------"
    lang_code='en-US'
    googl_speech_url = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=%s&maxresults=6'%(lang_code)
    hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",'Content-type': 'audio/x-flac; rate='+str(vConfig.RATE)}
    req = urllib2.Request(googl_speech_url, data=flac_cont, headers=hrs)
    p = urllib2.urlopen(req)
 
    print "Complete"
    #res = eval(p.read())['hypotheses']
    res = p.read()
    print res
    #print eval( str( eval(res)['hypotheses'] ))['utterance'][0]
    textString = ''
    if (res != None):
        #cmd = "echo \"" + str(res) + "\" | sed -e 's/[{}]/''/g'| awk -v k=\"text\" '{n=split($0,a,\",\"); for (i=1; i<=n; i++) print a[i]; exit }' | awk -F: 'NR==3 { print $3; exit }'"
        #p = Popen(cmd, shell=True, stdout=PIPE)
        #textString = p.communicate()[0].rstrip()
	#textString = runCommand( "echo \"" + str(res) + "\" | sed -e 's/[{}]/''/g'| awk -v k=\"text\" '{n=split($0,a,\",\"); for (i=1; i<=n; i++) print a[i]; exit }' | awk -F: 'NR==3 { print $3; exit }'" )
	p = re.compile('utterance\":\"([^\"]*)\"') 
	testlist=p.findall( res,1)
	textString = testlist[0]

    print "------------------------- RESULTS ----------------------------------"
    print "Google returned: '" + textString + "'"
    print "--------------------------------------------------------------------"
    if ( textString != '' ):
        #os.system( "say " + str(textString) )
	print "Initiating Configuration Lookup"
	cmd = vConfig.getConfig( textString )
        if ( cmd is not None ):
            runCommand(cmd)
         
    else:
        #os.system( "say \"Sorry, I could not understand what you said\"" )
	print "String not found"

    print "Deleting Temp AudioFiles" 
    map(os.remove, (filename+'.flac', filename+'.wav'))
    return res



def cleanup():
    print "Caught Exit.. Cleaning Up" 
    print "... Deleting any tmp audio files lying around"
    os.remove( "output_*" )

FLAC_CONV = 'flac --sample-rate=16000 -f ' # We need a WAV to FLAC converter.
if(__name__ == '__main__'):
    #atexit.register(cleanup)

    vConfig = voiceconfig.VoiceConfig()
    listen_for_speech()


