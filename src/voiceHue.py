import urllib2
import phue
import re

class VoiceHue:

	def __init__(self):
    	    #Get IP address of the HUE
	    url = "http://www.meethue.com/api/nupnp"

            hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7"}
            req = urllib2.Request( url, headers=hrs)
            res = urllib2.urlopen(req)

            #write intermediate MP3 file
            hue_info = eval( res.read()[1:-1] )
	    self.bridge_ip = hue_info['internalipaddress']
	    self.bridge_id = hue_info['id']

 	    print self.bridge_id
	    print self.bridge_ip

	    try:
	        self.bridge = phue.Bridge(self.bridge_ip)

	    except phue.PhueRegistrationException as e:
		print "Not registered with Bridge, please press the button on the bridge and re-try your command"



	def getLights(self):
		return self.bridge.get_light_objects('id')

	def getGroups(self):
		return self.bridge.get_group()
	    

	## Toggle a group or a light by name.. If a group exists it will toggle the group, if not it will check for a light and toggle it instead
	def toggleByName(self, name ):
		group = self.bridge.get_group()
		if ( len( group ) > 0 ):
			## do something with the group
			print group
		else:
			## do something with the light
			light_names = self.bridge.get_light_objects('name')
			print light_names
			for light in light_names:
				if ( str( light ).lower() == str( name ).lower() ):
					if ( light_names[light].on ):
						print "HUE: Light - " + light + " on, Turning off"
						light_names[light].on = False
					else:
						print "HUE: Light - " + light + " off, Turning on"
						light_names[light].on = True



	def dimByName(self, name, dimFactor ):
		group = self.bridge.get_group()
		if ( len( group ) > 0 ):
			## do something with the group
			print group
		else:
			## do something with the light
			light_names = self.bridge.get_light_objects('name')
			print light_names
			for light in light_names:
				if ( str( light ).lower() == str( name ).lower() ):
					if ( light_names[light].on ):
						brightness = light_names[light].brightness 
						#dimFactor = 50

						print "HUE: Light - " + light + " at brightness: " + str( brightness ) + " altering by " + str( dimFactor ) 
						result = brightness + dimFactor
						if ( result > 254 ):
							result = 254

						if ( result < 1 ):
							result = 0
						
						light_names[light].brightness = result



	def controlByCommand(self, command ):
		words = command.split( " " )
		light_group = words[1]
		print light_group
		print words[-1]
		try:
			inter = int(float( words[-1] ))
			print "found Int"
			dimreg = re.compile("dim|reduce")
			increg = re.compile("increase|brighter")
			
			if ( dimreg.search( command )):
				print "reduce brightness"
				self.dimByName( light_group, ( inter*-1 ))

			if ( increg.search( command )):
				print "increase brightnes"
				self.dimByName( light_group, inter )


		except  ValueError:
			maxreg = re.compile("maximum|max|maximize")
			minreg = re.compile("minimize|minimum")
			offonreg = re.compile("off|on|toggle")

			if ( maxreg.search( command )):
				print "Set max brightness"
				self.dimByName( light_group, 254 )
			
			if ( minreg.search( command )):
				print "Set max brightness"
				self.dimByName( light_group, -254 )

			if ( offonreg.search( command )):
				self.toggleByName(light_group)


			print "found string"

	
	def getIP(self):
	    return self.bridge_ip

	def getID(self):
	    return self.bridge_id



if(__name__ == '__main__'):
	hueController = VoiceHue()
        lights = hueController.getLights()
	print lights

	groups = hueController.getGroups()
	print groups

	#hueController.toggleByName( "kitchen" )
	#hueController.dimByName( "kitchen" , -50)
	#hueController.dimByName( "kitchen" , +50)

	hueController.controlByCommand( "lights kitchen off" )
	hueController.controlByCommand( "lights kitchen on" )
	#hueController.controlByCommand( "lights kitchen dim by 50" )
	#hueController.controlByCommand( "lights kitchen set brighter by 50" )
	#hueController.controlByCommand( "lights kitchen reduce brightness by 50" )
	#hueController.controlByCommand( "lights kitchen increase brightness by 50" )

	#hueController.controlByCommand( "lights kitchen set brightnes to minimum")
	#hueController.controlByCommand( "lights kitchen set brightnes to maximum")

	#lights[1].brightness = 254

