#!/usr/bin/python
##
## Searches for a torrent on pirate bay, sorts by peers and posts the magnet link to your transmission server
##

import sys
import urllib
import urllib2
import base64
import re

class VoiceDownloader:

	@staticmethod
	def searchTorrents( site, string ):
	    encodedString = urllib.quote_plus( string )
	    #print encodedString
	    torrentSearchUrl = ''		
	    reg = re.compile("")
            if ( site == "thepiratebay" ):
		    torrentSearchUrl = 'http://thepiratebay.sx/search/' + encodedString + '/0/7/0'
		    reg = re.compile("<a href=\"magnet:(.+?)\" ")
	    else:
		    torrentSearchUrl = 'http://publichd.se/index.php?page=torrents&active=1&search=' + encodedString + '&order=5&by=2'
		    reg = re.compile("<a href=magnet:(.+?)>")

	    hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7"}
	    req = urllib2.Request( torrentSearchUrl, headers=hrs)
	    res = urllib2.urlopen(req)

	    #write intermediate MP3 file
	    html_body = res.read()
	    print html_body
	    linksList = reg.findall( html_body, 1)

	    if ( len(linksList) > 0 ):
		return "magnet:" + linksList[0]
	    else:
		print "No downloads available for: " + string
                return None

	@staticmethod
	def postMagnetLink( url, username, password, magneturl, destination ):
	    trans_rpc = url + '/transmission/rpc'

	    print "Posting torrent link to: " + trans_rpc

	    postData = '{"method":"torrent-add","arguments":{"paused":false,"download-dir":"'+ str( destination ) + '","filename":"' + magneturl + '"}}'


	    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
	    req = urllib2.Request( trans_rpc, postData )
	    req.add_header("Authorization", "Basic %s" % base64string)
	    req.add_header( "User-Agent", "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7" )
	    req.add_header( "Content-Type", "application/json" )
	    #req.add_header( "X-Transmission-Session-Id:", "neEyk19o9RDDRZtMc9myro5Zs50Yz0tylWCRsvvGCcyU9m43" )

	    session_id = ''
	    try:
		res = urllib2.urlopen( req )
	    except urllib2.HTTPError as e:
		session_id = e.info().getheader( 'X-Transmission-Session-Id' )

	    req.add_header( "X-Transmission-Session-Id", session_id )
	    try:
		res = urllib2.urlopen( req )
		return "Successfully initialized download"
	    except urllib2.HTTPError as e:
		return "There was an error initiating the magnet link in your transmission server, please try again"
	    

	@staticmethod
	def download( vConfig, string ):
	    trans_url = vConfig.get( "downloader", "trans_url" )
	    trans_user = vConfig.get( "downloader", "trans_user" )
	    trans_pass = vConfig.get( "downloader", "trans_pass" )
	    trans_destination = vConfig.get( "downloader", "trans_destination" )
	    site = vConfig.get( "downloader", "torrent_site" )

	    linkUrl = VoiceDownloader.searchTorrents( site, str( string ))
	    if ( linkUrl is not None ):
		return VoiceDownloader.postMagnetLink( trans_url, trans_user, trans_pass,  linkUrl , trans_destination )
	    else:
		return "No downloads available for: " + string
		
		

if(__name__ == '__main__'):

	#Pull the args into a single string to search for
	searchTerms = sys.argv
	searchTerms.pop(0)
	searchString = ' '.join(str(x) for x in searchTerms)

        # This can be built up to work outside of VoiceExec.. but I've not done anything with this part other than for testing	
	trans_url = "http://192.168.1.88:9091"
	trans_user = "trans_user"
	trans_pass = "trans_pass"
	trans_destination = "/Volumes/Downloads/incoming"

	linkUrl = VoiceDownloader.searchTorrents( 'not_thepiratebay', str( searchString ))
	if ( linkUrl is not None ):
		VoiceDownloader.postMagnetLink( trans_url, trans_user, trans_pass,  linkUrl , trans_destination )



