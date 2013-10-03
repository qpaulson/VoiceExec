#import atexit
#import pyaudio
#import wave
#import audioop
import os
import re
import urllib
import urllib2
import time
#import ConfigParser
#import pprint

#from collections import deque
#from subprocess import *


class GoogleSpeech:

	@staticmethod
	def tts(string ):
		#this will get the last remnants
		#wget -q -U Mozilla -O "$tmpDir/tmp.mp3" "http://translate.google.com/translate_tts?tl=${lang}&q=$string"
		#cat "$tmpDir/tmp.mp3" >> "$tmpDir/speak.mp3"
		lang_code='en'
		google_speech_url = 'http://translate.google.com/translate_tts?tl='+lang_code+'&q='+urllib.quote_plus( string )
		hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7"}
		req = urllib2.Request( google_speech_url, headers=hrs)
		res = urllib2.urlopen(req)

		#write intermediate MP3 file
		filename = 'output_'+str(int(time.time()))
		ofp = open(filename+'.mp3','wb')
		ofp.write(res.read())
		ofp.close()

		os.system( 'play '+filename+'.mp3' )

		## Get the date and play it 



	@staticmethod
	def stt( filename, RATE):
		FLAC_CONV = 'flac --sample-rate=16000 -f ' # We need a WAV to FLAC converter.
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
		hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",'Content-type': 'audio/x-flac; rate='+str(RATE)}
		req = urllib2.Request(googl_speech_url, data=flac_cont, headers=hrs)
		p = urllib2.urlopen(req)

		print "Complete"
		res = p.read()
		print res
		textString = ''
		testlist = []
		if (res != None):
			p = re.compile('utterance\":\"([^\"]*)\"')
			testlist=p.findall( res,1)
			if ( len( testlist ) >= 1 ):
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


