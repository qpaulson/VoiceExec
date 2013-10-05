import os
import sys
import re
import ConfigParser
import pywapi

from googleSpeech import GoogleSpeech


class VoiceWeather:

    @staticmethod
    def speakWeather( config, string ):
        location_code = config.get( "weather", "weather_location_code" )

        weather_com_result = pywapi.get_weather_from_weather_com( str(location_code ))
        print weather_com_result
        print string


        lookupString = ''
        ### TODAY
        if ( re.compile( "today", re.IGNORECASE ).findall( string ,1 )):
            todayData = weather_com_result['forecasts'][0]
            if ( todayData['day']['text'] != 'N/A' ):
                    if ( int( todayData['day']['chance_precip'] ) > 40 ):
                        lookupString = "Today will be " + str( todayData['day']['text'] ) + " with a chance of showers and a high of " + str( todayData['high'] ) + "degrees"
                    else:
                        lookupString = "Today will be " + str( todayData['day']['text'] ) + " with a high of " + str( todayData['high'] ) + "degrees"
            else:
                    if ( int(todayData['night']['chance_precip'] ) > 40 ):
                        lookupString = "Tonight will be " + str( todayData['night']['text'] ) + " with a chance of showers"
                    else:
                        lookupString = "Tonight will be " + str( todayData['night']['text'] )


        ### TONIGHT
        elif ( re.compile( "tonight", re.IGNORECASE).findall( string ,1 )):
            todayData = weather_com_result['forecasts'][0]
            if ( int(todayData['night']['chance_precip'] ) > 40 ):
                lookupString = "Tonight will be " + str( todayData['night']['text'] ) + " with a chance of showers"
            else:
                lookupString = "Tonight will be " + str( todayData['night']['text'] )

        ### Tomorrow Night
        elif ( re.compile( "tomorrow night", re.IGNORECASE).findall( string ,1 )):
            todayData = weather_com_result['forecasts'][1]
            if ( int(todayData['night']['chance_precip'] ) > 40 ):
                lookupString = "Tomorrow night will be " + str( todayData['night']['text'] ) + " with a chance of showers"
            else:
                lookupString = "Tomorrow night will be " + str( todayData['night']['text'] )

        ### TODAY
        elif ( re.compile( "tomorrow", re.IGNORECASE ).findall( string ,1 )):
            todayData = weather_com_result['forecasts'][1]
            if ( todayData['day']['text'] != 'N/A' ):
                    if (( int( todayData['day']['chance_precip'] ) > 40 ) or ( int( todayData['night']['chance_precip'] ) > 40 )):
                        lookupString = "Tomorrow will be " + str( todayData['day']['text'] ) + " with a chance of showers and a high of " + str( todayData['high'] ) + " degrees"
                    else:
                        lookupString = "Tomorrow will be " + str( todayData['day']['text'] ) + " with a high of " + str( todayData['high'] ) + "degrees"


        else:
            lookupString = "It is currently " + str(weather_com_result['current_conditions']['text']) + " and " + weather_com_result['current_conditions']['temperature'] + "degrees.\n\n"


        print lookupString
        ## Work our magic
        if ( lookupString != '' ):
            GoogleSpeech.tts( lookupString )
        else:
            GoogleSpeech.tts( "Sorry, Weather information un-available at this time, please try again later" )




