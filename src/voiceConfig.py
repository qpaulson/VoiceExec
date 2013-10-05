import os
import sys
import re
import ConfigParser

class VoiceConfig:

    def __init__(self):
        INPUT_BLOCK_TIME = 0.05
        self.configuration = ConfigParser.RawConfigParser()
        self.RATE = 44100
        self.CHANNELS = 2
        self.DEVICE = -1
        self.THRESHOLD = 10
        self.SILENCE_LIMIT = 3
        self.INPUT_FRAMES_PER_BLOCK = int(self.RATE * INPUT_BLOCK_TIME)
        self.loadConfig()



    def loadConfig(self):
        print 'CONFIG: Loading Configuration File'
        self.configuration.read(['conf/voiceExec.conf', os.path.expanduser('~/.voiceExec.conf')])
        #print self.configuration.items('System Commands')
        print 'CONFIG: Configuration File Loaded'
        key = 'record_rate'
        if self.configuration.has_option('System Config', key):
            self.RATE = int(self.configuration.get('System Config', key))
            print 'CONFIG: ' + key + ' in configuration, setting to: ' + str(self.RATE)
        else:
            print 'CONFIG: ' + key + ' not found, using default: ' + str(self.RATE)
        key = 'record_device'
        if self.configuration.has_option('System Config', key):
            self.DEVICE = int(self.configuration.get('System Config', key))
            print 'CONFIG: ' + key + ' in configuration, setting to: ' + str(self.DEVICE)
        else:
            print 'CONFIG: ' + key + ' not found, using default: AUTO DETECT'
        key = 'record_silence_threshold'
        if self.configuration.has_option('System Config', key):
            self.THRESHOLD = int(self.configuration.get('System Config', key))
            print 'CONFIG: ' + key + ' in configuration, setting to: ' + str(self.THRESHOLD)
        else:
            print 'CONFIG: ' + key + ' not found, using default: ' + str(self.THRESHOLD)



    def matchCommand(self, voicecommand, inputvoice):
        p = re.compile(voicecommand, re.IGNORECASE)
        return p.search(inputvoice)



    def parserPer(self, value, inputvoice):
        if '$1' in value:
            inputvoice = inputvoice.strip()
            args = inputvoice.split(' ')
            i = 1
            for arg in args:
                value = value.replace('$' + str(i), arg)
                i = i + 1

        elif '...' in value:
            value = value.replace('...', inputvoice)
        return value



    def getConfig(self, string):
        keys = self.configuration.items('System Commands')
        try:
            for (key, value,) in keys:
                print 'CONFIG checking: ' + key
                if self.matchCommand(key, string):
                    string = re.sub(key, '', string)
                    cmd = self.parserPer(value, string)
                    print 'CONFIG: Matched'
                    print value
                    print cmd
                    return cmd

        except Exception as e:
            print e
            print 'Command not found configured: ' + string



    def matchInputVoiceCommand(self, inputvoice):
        d = self.loadCommandConf('voicecommand.conf')
        for (k, v,) in d.iteritems():
            if self.matchCommand(k, inputvoice):
                inputvoice = re.sub(k, '', inputvoice)
                cmd = self.parserPer(v, inputvoice)
                print v
                print cmd
                os.system(cmd)

    def get(self, section, key ):
	return self.configuration.get( section, key )

