import pyaudio
import wave
import audioop
import os
import urllib2
import time
from collections import deque 
from subprocess import *
 

#confi
RATE = 44100
CHANNELS = 1
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
FORMAT = pyaudio.paInt16
THRESHOLD = 10 #The threshold intensity that defines silence signal (lower than).
SILENCE_LIMIT = 3 #Silence limit in seconds. The max ammount of seconds where only silence is recorded. When this time passes the recording finishes and the file is delivered.


p = pyaudio.PyAudio()

def initStream():
    #open stream

    # List and find the correct input device
    device_index = None
    for i in range( p.get_device_count() ):
        devinfo = p.get_device_info_by_index(i)
        print( "Device %d: %s"%(i,devinfo["name"]) )
        for keyword in ["mic","input"]:
	    if keyword in devinfo["name"].lower():
	        print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
	        device_index = i

    stream  = p.open(   format = FORMAT,
                         channels = CHANNELS,
                         rate = RATE,
                         input = True,
                         input_device_index = device_index,
                         frames_per_buffer = INPUT_FRAMES_PER_BLOCK)
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
    rel = RATE/INPUT_FRAMES_PER_BLOCK
    slid_win = deque(maxlen=SILENCE_LIMIT*rel)
    started = False
    
    while (True):
        data = stream.read(INPUT_FRAMES_PER_BLOCK)
        slid_win.append (abs(audioop.avg(data, 2)))

        if(True in [ x>THRESHOLD for x in slid_win]):
            if(not started):
                print "starting record"
            started = True
            all_m.append(data)
        elif (started==True):
            print "finished"
            #the limit was reached, finish capture and deliver
            filename = save_speech(all_m,p)
	    print filename
            stt_google_wav(filename)
            #reset all
            started = False
            slid_win = deque(maxlen=SILENCE_LIMIT*rel)
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
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    #wf.setframerate(RATE)
    wf.setframerate(16000)
    wf.writeframes(data)
    wf.close()
    return filename


def stt_google_wav(filename):
    #Convert to flac
    print "Converting WAV to FLAC"
    os.system(FLAC_CONV+ filename+'.wav')
    f = open(filename+'.flac','rb')
    flac_cont = f.read()
    f.close()
    print "Complete"

    #post it
    print "Posting FLAC to Google"
    lang_code='en-US'
    googl_speech_url = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=%s&maxresults=6'%(lang_code)
    hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",'Content-type': 'audio/x-flac; rate='+str(RATE)}
    req = urllib2.Request(googl_speech_url, data=flac_cont, headers=hrs)
    p = urllib2.urlopen(req)
 
    print "Complete"
    #res = eval(p.read())['hypotheses']
    res = p.read()
    textString = ''
    if (res != None):
        cmd = "echo \"" + str(res) + "\" | sed -e 's/[{}]/''/g'| awk -v k=\"text\" '{n=split($0,a,\",\"); for (i=1; i<=n; i++) print a[i]; exit }' | awk -F: 'NR==3 { print $3; exit }'"
        p = Popen(cmd, shell=True, stdout=PIPE)
        textString = p.communicate()[0].rstrip()

    print "Google returned: '" + textString + "'"
    if ( textString != '' ):
        os.system( "say " + str(textString) )
    else:
        os.system( "say \"Sorry, I could not understand what you said\"" )

    print "Deleting Temp AudioFiles" 
    map(os.remove, (filename+'.flac', filename+'.wav'))
    return res

FLAC_CONV = 'flac --sample-rate=16000 -f ' # We need a WAV to FLAC converter.
if(__name__ == '__main__'):
    listen_for_speech()
