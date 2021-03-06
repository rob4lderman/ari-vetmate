#!/usr/bin/python3
#
# ENV VARS:
# ARI_MONGO_URI
# ARI_CREDS
#
#


import json         
import getopt       # for parsing cli args
import sys          # for parsing cli args
import os           # for reading env vars

import requests     # for making http requests

from pymongo import MongoClient

from mailer import Mailer
from mailer import Message

from postmark import PMMail

#        datestr = datestr + " {}".format( date.today().year )
#        tmpdate = datetime.strptime(datestr, "%b %d %Y")
#        return tmpdate.strftime("%m/%d/%y")
# https://docs.python.org/3.3/library/datetime.html#strftime-strptime-behavior
from datetime import date, datetime, timedelta, timezone
import pytz

#
# API: https://www.dlitz.net/software/pycrypto/api/current/
#
from Crypto.Cipher import AES
from Crypto import Random
import base64


#
# Print to STDOUT
#
def logTrace( *objs ):
    print(*objs)

#
# Print to STDERR
#
def logError( *objs ):
    print( *objs, file=sys.stderr )

#
# Prints to STDERR
#
def logInfo( *objs ):
    logError( *objs )


#
# Parse command line args  
#
# @return a dictionary of opt=val
#
def parseArgs():
    long_options = [ "action=", 
                     "startdate=", 
                     "inputfile=", 
                     "mongouri=",
                     "zipcode=",
                     "notificationEmail=",
                     "gmailuser=",
                     "gmailpass=",
                     "outputfile=",
                     "inputfile=",
                     "toaddr=",
                     "subject=",
                     "msg=",
                     "user=",
                     "pass="]
    opts, args = getopt.getopt( sys.argv[1:], "", long_options )
    retMe = {}
    for opt,val in opts:
       retMe[ opt ] = val
    return retMe

#
# Verify the args map contains the given required_args
#
# @return args
#
# @throws RuntimeError if required_arg is missing.
#
def verifyArgs( args, required_args ):
    for arg in required_args:
        if arg not in args:
            raise RuntimeError( 'Argument %r is required' % arg )
        elif len(args[arg]) == 0:
            raise RuntimeError( 'Argument %r is required' % arg )
    return args


#
# Write the given json object to the given file
#
def writeJson( jsonObj, filename ):
    print( "writeJson: writing to file " + filename + "...");
    f = open(filename, "w")
    f.write( json.dumps( jsonObj, indent=2, sort_keys=True) )
    f.close()


#
# @return a jsonobj as read from the given json file
#
def readJson( filename ):
    print( "readJson: reading from file " + filename + "...");
    f = open(filename, "r")
    jsonObj = json.load(f)
    f.close()
    return jsonObj


#
# Send notification!
# Note: need to enable "less secure apps" in gmail: https://www.google.com/settings/security/lesssecureapps
#
def sendNotificationViaGmail( fromAddr, fromPass, toAddr, subject, msg):

    logTrace("sendNotificationViaGmail: fromAddr:", fromAddr,
                                       "fromPass:", ("x" * len(fromPass) ),
                                       "toAddr:", toAddr,
                                       "subject:", subject,
                                       "msg:", msg )

    message = Message(From=fromAddr,
                      To=toAddr)

    message.Subject = subject
    message.Body = msg
    # message.Html = "".join( emailLinesHtml )

    sender = Mailer('smtp.gmail.com', 
                     port=587,
                     use_tls=True, 
                     usr=fromAddr,
                     pwd=fromPass )
    sender.send(message)


#
# Send notification!
# Note: need to enable "less secure apps" in gmail: https://www.google.com/settings/security/lesssecureapps
#
def sendNotificationViaPostmark( fromAddr, toAddr, subject, msg):

    logTrace("sendNotificationViaPostmark: fromAddr:", fromAddr,
                                           "toAddr:", toAddr,
                                           "subject:", subject,
                                            "msg:", msg )

    message = PMMail(api_key = os.environ.get('POSTMARK_API_TOKEN'),
                     subject = subject,
                     sender = fromAddr,
                     to = toAddr,
                     text_body = msg,
                     tag = "ari") 
    message.send()

#
# Send an email.
#
def sendEmail(args):

    gmailcreds = decryptCreds( os.environ["ARI_CREDS"] )
    args['--gmailuser'] = gmailcreds.split(":",1)[0]
    args['--gmailpass'] = gmailcreds.split(":",1)[1]

    args = verifyArgs( args , required_args = [ '--toaddr', '--subject', '--msg', '--gmailuser', '--gmailpass' ] )

    sendNotificationViaGmail( args['--gmailuser'],
                              args['--gmailpass'],
                              args['--toaddr'],
                              args['--subject'],
                              args['--msg'] )


#
# @return a ref to the mongo db by the given name.
#
def getMongoDb( mongoUri ):
    dbname = mongoUri.split("/")[-1]
    hostname = mongoUri.split("@")[-1]
    mongoClient = MongoClient( mongoUri )
    print("getMongoDb: connected to mongodb://{}, database {}".format( hostname, dbname ) )
    return mongoClient[dbname]


#
#
#  {
#       "response": {
#           "version":"0.1",
#           "termsofService":"http://www.wunderground.com/weather/api/d/terms.html",
#           "features": {
#               "alerts": 1 ,
#               "hourly": 1
#           }
# 	    },
# 	    "hourly_forecast": [
# 	    	{
# 	    	    "FCTTIME": {
# 	    	        "hour": "18",
#                   "hour_padded": "18",
#                   "min": "00",
#                   "min_unpadded": "0",
#                   "sec": "0",
#                   "year": "2016",
#                   "mon": "4",
#                   "mon_padded": "04",
#                   "mon_abbrev": "Apr",
#                   "mday": "21",
#                   "mday_padded": "21",
#                   "yday": "111",
#                   "isdst": "1",
#                   "epoch": "1461283200",
#                   "pretty": "6:00 PM MDT on April 21, 2016",
#                   "civil": "6:00 PM",
#                   "month_name": "April",
#                   "month_name_abbrev": "Apr",
#                   "weekday_name": "Thursday",
#                   "weekday_name_night": "Thursday Night",
#                   "weekday_name_abbrev": "Thu",
#                   "weekday_name_unlang": "Thursday",
#                   "weekday_name_night_unlang": "Thursday Night",
#                   "ampm": "PM",
#                   "tz": "",
#                   "age": "",
#                   "UTCDATE": ""
# 	    	    },
# 	    	    "temp": {"english": "62", "metric": "17"},
# 	    	    "dewpoint": {"english": "37", "metric": "3"},
# 	    	    "condition": "Clear",                                       <----------------- https://www.wunderground.com/weather/api/d/docs?d=resources/phrase-glossary
# 	    	    "icon": "clear",
# 	    	    "icon_url":"http://icons.wxug.com/i/c/k/clear.gif",
# 	    	    "fctcode": "1",                                             <----------------- https://www.wunderground.com/weather/api/d/docs?d=resources/phrase-glossary
# 	    	    "sky": "13",
# 	    	    "wspd": {"english": "6", "metric": "10"},
# 	    	    "wdir": {"dir": "S", "degrees": "186"},
# 	    	    "wx": "Sunny",
# 	    	    "uvi": "1",
# 	    	    "humidity": "39",
# 	    	    "windchill": {"english": "-9999", "metric": "-9999"},
# 	    	    "heatindex": {"english": "-9999", "metric": "-9999"},
# 	    	    "feelslike": {"english": "62", "metric": "17"},
# 	    	    "qpf": {"english": "0.0", "metric": "0"},
# 	    	    "snow": {"english": "0.0", "metric": "0"},
# 	    	    "pop": "0",
# 	    	    "mslp": {"english": "30.04", "metric": "1017"}
# 	    	},
#             {
#                 ...
#             }
# 	    ],
#       "query_zone": "039",
# 	    "alerts": [
#           {
#               "type": "HEA",
#               "description": "Heat Advisory",
#               "date": "11:14 am CDT on July 3, 2012",
#               "date_epoch": "1341332040",
#               "expires": "7:00 AM CDT on July 07, 2012",
#               "expires_epoch": "1341662400",
#               "message": "\u000A...Heat advisory remains in effect until 7 am CDT Saturday...\u000A\u000A* temperature...heat indices of 100 to 105 are expected each \u000A afternoon...as Max temperatures climb into the mid to upper \u000A 90s...combined with dewpoints in the mid 60s to around 70. \u000A Heat indices will remain in the 75 to 80 degree range at \u000A night. \u000A\u000A* Impacts...the hot and humid weather will lead to an increased \u000A risk of heat related stress and illnesses. \u000A\u000APrecautionary/preparedness actions...\u000A\u000AA heat advisory means that a period of hot temperatures is\u000Aexpected. The combination of hot temperatures and high humidity\u000Awill combine to create a situation in which heat illnesses are\u000Apossible. Drink plenty of fluids...stay in an air-conditioned\u000Aroom...stay out of the sun...and check up on relatives...pets...\u000Aneighbors...and livestock.\u000A\u000ATake extra precautions if you work or spend time outside. Know\u000Athe signs and symptoms of heat exhaustion and heat stroke. Anyone\u000Aovercome by heat should be moved to a cool and shaded location.\u000AHeat stroke is an emergency...call 9 1 1.\u000A\u000A\u000A\u000AMjb\u000A\u000A\u000A",
#               "phenomena": "HT",
#               "significance": "Y",
#               "ZONES": [
#                   {
#                       "state":"UT",
#                       "ZONE":"001"
#                   }
#               ],
#               "StormBased": {
#                   "vertices":[
#                       {
#                           "lat":"38.87",
#                           "lon":"-87.13"
#                       },
#                       {
#                           "lat":"38.89",
#                           "lon":"-87.13"
#                       },
#                       {
#                           "lat":"38.91",
#                           "lon":"-87.11"
#                       },
#                       {
#                           "lat":"38.98",
#                           "lon":"-86.93"
#                       },
#                       {
#                           "lat":"38.87",
#                           "lon":"-86.69"
#                       },
#                       {
#                           "lat":"38.75",
#                           "lon":"-86.3"
#                       },
#                       {
#                           "lat":"38.84",
#                           "lon":"-87.16"
#                       }
#                   ],
#                   "Vertex_count":7,
#                   "stormInfo": {
#                       "time_epoch": 1363464360,
#                       "Motion_deg": 243,
#                       "Motion_spd": 18,
#                       "position_lat":38.90,
#                       "position_lon":-86.96
#                   }
#               }
#           }
#       ]
#  }
#
# Hourly forecast fctcode and condition
# 1	Clear	
# 2	Partly Cloudy	
# 3	Mostly Cloudy	
# 4	Cloudy	
# 5	Hazy	
# 6	Foggy	
# 7	Very Hot	
# 8	Very Cold	
# 9	Blowing Snow	
# 10	Chance of Showers	
# 11	Showers	
# 12	Chance of Rain	
# 13	Rain	
# 14	Chance of a Thunderstorm	
# 15	Thunderstorm	
# 16	Flurries	
# 17	OMITTED	
# 18	Chance of Snow Showers	
# 19	Snow Showers	
# 20	Chance of Snow	
# 21	Snow	
# 22	Chace of Ice Pellets	
# 23	Ice Pellets	
# 24	Blizzard	
# 
#
# @return the data in a dict
# @throws raise_for_status() if a non-200 status_code
#
def fetchWeatherData(zipcode):

    logTrace("fetchWeatherData: for zipcode", zipcode)

    r = requests.get('http://api.wunderground.com/api/3d32d71a6c117bb4/alerts/hourly/q/{0}.json'.format(zipcode))
    if (r.status_code == 200):
        return r.json()
    else:
        r.raise_for_status()



#
# condition               - icon              - coarse
# Chance of Flurries	    chanceflurries	--> snow
# Chance of Rain	        chancerain	    --> rain
# Chance Rain	            chancerain	    --> rain
# Chance of Freezing Rain	chancesleet	    --> snow
# Chance of Sleet	        chancesleet	    --> snow
# Chance of Snow	        chancesnow	    --> snow
# Chance of Thunderstorms	chancetstorms	--> tstorms
# Chance of a Thunderstorm	chancetstorms	--> tstorms
# Clear	                    clear	        --> sunny
# Cloudy	                cloudy	        --> cloudy
# Flurries	                flurries	    --> snow
# Fog	                    fog	            --> rain
# Haze	                    hazy	        --> sunny
# Mostly Cloudy	            mostlycloudy	--> cloudy
# Mostly Sunny	            mostlysunny	    --> sunny
# Partly Cloudy	            partlycloudy	--> cloudy
# Partly Sunny	            partlysunny	    --> sunny
# Freezing Rain	            sleet	        --> snow
# Rain	                    rain	        --> rain
# Sleet	                    sleet	        --> snow
# Snow	                    snow	        --> snow
# Sunny	                    sunny	        --> sunny
# Thunderstorms	            tstorms	        --> tstorms
# Thunderstorm	            tstorms	        --> tstorms
# Unknown	                unknown	        --> sunny
# Overcast	                cloudy	        --> cloudy
# Scattered Clouds	        partlycloudy	--> cloudy
#
# @return the more coarse-grained label for the given icon
#
def mapIconToCoarseLabel( icon ):

    iconMap = {
        "chanceflurries":   "snow",
        "chancerain":       "rain",
        "chancerain":       "rain",
        "chancesleet":      "snow",
        "chancesleet":      "snow",
        "chancesnow":       "snow",
        "chancetstorms":    "t-storms",
        "chancetstorms":    "t-storms",
        "clear":            "clear",    # "sunny" doesnt work for nighttime
        "cloudy":           "cloudy",
        "flurries":         "snow",
        "fog":              "rain",
        "hazy":             "clear",
        "mostlycloudy":     "cloudy",
        "mostlysunny":      "clear",
        "partlycloudy":     "cloudy",
        "partlysunny":      "clear",
        "sleet":            "snow",
        "rain":             "rain",
        "sleet":            "snow",
        "snow":             "snow",
        "sunny":            "clear",
        "tstorms":          "t-storms",
        "tstorms":          "t-storms",
        "unknown":          "clear",
        "cloudy":           "cloudy",
        "partlycloudy":     "cloudy"
    }
    return iconMap[icon]


#
#      http://api.wunderground.com/api/3d32d71a6c117bb4/geolookup/q/80304.json
#        {
#            "response": {
#                "version":"0.1",
#                "termsofService":"http://www.wunderground.com/weather/api/d/terms.html",
#                "features": {
#                    "geolookup": 1
#                }
#            },	
#            "location": {
#                "type":"CITY",
#                "country":"US",
#                "country_iso3166":"US",
#                "country_name":"USA",
#                "state":"CO",
#                "city":"Boulder",
#                "tz_short":"MDT",
#                "tz_long":"America/Denver",
#                "lat":"40.03531647",
#                "lon":"-105.28376770",
#                "zip":"80304",
#                "magic":"1",
#                "wmo":"99999",
#                "l":"/q/zmw:80304.1.99999",
#                "requesturl":"US/CO/Boulder.html",
#                "wuiurl":"http://www.wunderground.com/US/CO/Boulder.html",
#                "nearby_weather_stations": {
#                    ...
#                }
#            }
#        }
#
# @return the tz_short for the given zipcode
#
def fetchTimeZone(zipcode):

    r = requests.get('http://api.wunderground.com/api/3d32d71a6c117bb4/geolookup/q/{0}.json'.format(zipcode))
    if (r.status_code == 200):
        retMe = r.json()["location"]["tz_long"]
    else:
        r.raise_for_status()

    logTrace("fetchTimeZone: zipcode", zipcode, "timezone", retMe)
    return retMe


#
#
#  	    	    "FCTTIME": {
# 	    	        "hour": "18",
#                   "hour_padded": "18",
#                   "min": "00",
#                   "min_unpadded": "0",
#                   "sec": "0",
#                   "year": "2016",
#                   "mon": "4",
#                   "mon_padded": "04",
#                   "mon_abbrev": "Apr",
#                   "mday": "21",
#                   "mday_padded": "21",
#                   "yday": "111",
#                   "isdst": "1",
#                   "epoch": "1461283200",
#                   "pretty": "6:00 PM MDT on April 21, 2016",
#                   "civil": "6:00 PM",
#                   "month_name": "April",
#                   "month_name_abbrev": "Apr",
#                   "weekday_name": "Thursday",
#                   "weekday_name_night": "Thursday Night",
#                   "weekday_name_abbrev": "Thu",
#                   "weekday_name_unlang": "Thursday",
#                   "weekday_name_night_unlang": "Thursday Night",
#                   "ampm": "PM",
#                   "tz": "",
#                   "age": "",
#                   "UTCDATE": ""
# 	    	    },
#
# @return FCTTIME formatted as string
#
def formatFCTTIME( fcttime ):
    # TODO: timezone?
    return "{0}/{1}/{2}-{3}:{4}:{5}".format( fcttime["year"],
                                         fcttime["mon_padded"],
                                         fcttime["mday_padded"],
                                         fcttime["hour_padded"],
                                         fcttime["min"],
                                         fcttime["tz"])


#
# @return true if there's a tstorm in the given hourly_forecast
#
def isTstorm( hourly_forecast ):
    return "tstorm" in hourly_forecast["icon"]


#
# @return true if there's a tstorm in the given set of hourly_forecasts
#
def isTstormInForecast( hourly_forecasts ):
    retMe = False
    for hourly_forecast in hourly_forecasts:
        if isTstorm( hourly_forecast ):
            retMe = True
            break
    logTrace("isTstormInForecast: ", retMe)
    return retMe

            

#
# Trace weather data
#
def logTraceWeatherData( zipcode, weatherData ):

    #
    # Scan 36-hour forecast for thunderstorms
    # https://www.wunderground.com/weather/api/d/docs?d=resources/phrase-glossary
    #
    for hourly_forecast in weatherData["hourly_forecast"]:
        logTrace( zipcode, 
                 formatFCTTIME( hourly_forecast["FCTTIME"] ), 
                 # hourly_forecast["FCTTIME"]["pretty"], 
                 "fctcode:", hourly_forecast["fctcode"], 
                 "icon:", hourly_forecast["icon"], 
                 "condition:", hourly_forecast["condition"], 
                 "Chance of precip (pop):", hourly_forecast["pop"] )

    #
    # Check alerts.
    # https://www.wunderground.com/weather/api/d/docs?d=resources/phrase-glossary
    #
    for alert in weatherData["alerts"]:
        logTrace( zipcode, alert["type"], alert["date"], alert["expires"] )



#
# @return a tstorm warning message for the given zipcode and hourly forecast
#
# TODO: should i send a new message if the pop changes?
# TODO: what if the forecast goes from tstorm to no tstorm? send update?
#
def buildTstormWarningMessage( zipcode, hourly_forecast ):
    retMe = {}
    retMe["_id"] = "tstorm-" + zipcode + "-" + formatFCTTIME( hourly_forecast["FCTTIME"] )
    retMe["zipcode"] = zipcode
    retMe["subject"] = "STORM ALERT!"
    retMe["msg"] = "{2}: {0}% chance of thunderstorms at {1}".format( hourly_forecast["pop"],
                                                                      hourly_forecast["FCTTIME"]["civil"].replace(":00 ",""),
                                                                      zipcode)
    logTrace("buildTstormWarningMessage: retMe:", json.dumps(retMe))
    return retMe

#
# Upsert msg to db
#
def upsertMessage( db, msg ):
    logTrace("upsertMessage: ", json.dumps(msg))
    db["/ari/messages"].update_one( { "_id": msg["_id"] }, 
                                    { "$set": msg }, 
                                    upsert=True )

#
# Upsert msg to db
#
def upsertMessages( db, msgs ):
    for msg in msgs:
        upsertMessage( db, msg )


#
# @return tstorm warning messages for the given hourly_forecasts
#
def buildTstormWarningMessages( zipcode, hourly_forecasts ):
    retMe = []
    for hourly_forecast in hourly_forecasts:
        if isTstorm( hourly_forecast ):
            retMe.append( buildTstormWarningMessage( zipcode, hourly_forecast ) )
    return retMe


#
# Download data for the given --zipcode and write to --outputfile
#
def downloadWeatherData( args ):

    args = verifyArgs( args , required_args = [ '--zipcode', '--outputfile' ] )

    weatherData = fetchWeatherData( args["--zipcode"] )
    writeJson( weatherData, args["--outputfile"] )


#
# Send the notification msg to the given user
#
def sendMessageToUser( msg, user ):

    sendNotificationViaPostmark( "team@surfapi.com",
                                 decryptCreds( user["notificationEmail"] ),
                                 msg["subject"],
                                 msg["msg"] )

#
# Send the notification msg to the given set of users
#
def sendMessageToUsers( msg, users ):
    for user in users: 
        sendMessageToUser(msg, user)


#
# @return all msgs marked hasBeenSent=False
#
def getUnsentMessages(db):
    retMe = list( db["/ari/messages"].find( { "$or": [ { "hasBeenSent": { "$exists": False } }, { "hasBeenSent" : False } ] } ) )
    logTrace("getUnsentMessages: retMe:", json.dumps(retMe))
    return retMe


#
# @return all users in the given zipcode
#
def getUsersInZipcode(db, zipcode):
    retMe = list( db["/ari/users"].find( { "zipcode": zipcode } ) )
    logTrace("getUsersInZipcode: zipcode:", zipcode, "retMe:", json.dumps(retMe))
    return retMe


#
# Send all unsent msgs in the queue
# Update msg records to reflect they have been sent
#
def sendNotifications( args ):

    args['--mongouri'] = decryptCreds( os.environ["ARI_MONGO_URI"] )

    # -rx- gmailcreds = decryptCreds( os.environ["ARI_CREDS"] )
    # -rx- args['--gmailuser'] = gmailcreds.split(":",1)[0]
    # -rx- args['--gmailpass'] = gmailcreds.split(":",1)[1]

    args = verifyArgs( args , required_args = [ '--mongouri' ] )

    db = getMongoDb( args["--mongouri"] )

    unsentMsgs = getUnsentMessages(db)

    for msg in unsentMsgs:
        users = getUsersInZipcode( db, msg["zipcode"] )
        sendMessageToUsers(msg, users)
        msg["hasBeenSent"] = True
        upsertMessage(db, msg)


#
# @return true if it's 7am
#
def isTimeForMorningForecast( fcttime ):
    return fcttime["hour_padded"] == "07"


#
# @return true if it's 7pm
#
def isTimeForEveningForecast( fcttime ):
    return fcttime["hour_padded"] == "19"


#
# @return an array of arrays, hourly_forecasts bucketed according to ari_iconCoarseLabel
#
def consolidateForecasts( hourly_forecasts ):
    # consolidate consecutive coarseLabels
    retMe = []
    prev_i = 0
    prev_coarseLabel = hourly_forecasts[0]["ari_iconCoarseLabel"]
    for i in range(len(hourly_forecasts)):
        curr_coarseLabel = hourly_forecasts[i]["ari_iconCoarseLabel"] 
        if ( curr_coarseLabel != prev_coarseLabel ):
            retMe.append( hourly_forecasts[ prev_i:i ] )
            prev_i = i
            prev_coarseLabel = curr_coarseLabel

    retMe.append( hourly_forecasts[ prev_i: ] )

    logTrace("consolidateForecasts: retMe:", retMe)
    return retMe


#
# @return a message fragment for the given consolidatedBucket of hourly_forecasts (with same ari_iconCoarseLabel)
#
def buildMessageFragment(consolidatedBucket):
    if (len(consolidatedBucket) == 1):
        hourly_forecast = consolidatedBucket[0]
        retMe = "{0}: {1}{2}".format( hourly_forecast["FCTTIME"]["civil"].replace(":00 ",""),
                                      hourly_forecast["pop"] + "% " if hourly_forecast["pop"] != "0" else "",
                                      hourly_forecast["ari_iconCoarseLabel"] )
    else:
        first_hourly_forecast = consolidatedBucket[0]
        last_hourly_forecast = consolidatedBucket[-1]
        retMe = "{0} thru {1}: {2}{3}".format( first_hourly_forecast["FCTTIME"]["civil"].replace(":00 ",""),
                                               last_hourly_forecast["FCTTIME"]["civil"].replace(":00 ",""),
                                               first_hourly_forecast["pop"] + "% " if first_hourly_forecast["pop"] != "0" else "",
                                               first_hourly_forecast["ari_iconCoarseLabel"] )

    logTrace("buildMessageFragment: retMe:", retMe)
    return retMe



#
# @return a morning forecast msg
#
def buildMorningForecastMsg( zipcode, hourly_forecasts):

    consolidatedBuckets = consolidateForecasts( hourly_forecasts[0:12] )
    msgFragments = map( buildMessageFragment, consolidatedBuckets )

    retMe = {}
    retMe["_id"] = "morning-" + zipcode + "-" + formatFCTTIME( hourly_forecasts[0]["FCTTIME"] )
    retMe["zipcode"] = zipcode
    retMe["subject"] = "Today's Forecast"
    retMe["msg"] = "{0}: {1}".format( zipcode, "; ".join(msgFragments) )

    logTrace("buildMorningForecastMsg: retMe:", json.dumps(retMe))
    return retMe
        

#
# @return a morning forecast msg
#
def buildEveningForecastMsgs( zipcode, hourly_forecasts):

    retMe = []

    # build overnight msg
    consolidatedBuckets = consolidateForecasts( hourly_forecasts[0:12] )
    msgFragments = map( buildMessageFragment, consolidatedBuckets )

    overnightMsg = {}
    overnightMsg["_id"] = "overnight-" + zipcode + "-" + formatFCTTIME( hourly_forecasts[0]["FCTTIME"] )
    overnightMsg["zipcode"] = zipcode
    overnightMsg["subject"] = "Overnight Forecast"
    overnightMsg["msg"] = "{0}: {1}".format( zipcode, "; ".join(msgFragments) )
    retMe.append( overnightMsg )


    # build next day msg
    consolidatedBuckets = consolidateForecasts( hourly_forecasts[12:24] )
    msgFragments = map( buildMessageFragment, consolidatedBuckets )

    tomorrowMsg = {}
    tomorrowMsg["_id"] = "tomorrow-" + zipcode + "-" + formatFCTTIME( hourly_forecasts[0]["FCTTIME"] )
    tomorrowMsg["zipcode"] = zipcode
    tomorrowMsg["subject"] = "Tomorrow's Forecast"
    tomorrowMsg["msg"] = "{0}: {1}".format( zipcode, "; ".join(msgFragments) )
    retMe.append( tomorrowMsg )

    logTrace("buildEveningForecastMsgs: retMe:", retMe)
    return retMe
        


#
# @return a morning forecast msg
#
def buildEveningForecastMsg( zipcode, weatherData ):
    return {}


#
# Add ari-app specific fields
#
# @return pre-processed weatherData
#
def preProcessWeatherData( weatherData ):

    # map icons to coarseLabels
    for hourly_forecast in weatherData["hourly_forecast"]:
        hourly_forecast["ari_iconCoarseLabel"] = mapIconToCoarseLabel( hourly_forecast["icon"] )

    return weatherData


#
# Process the weather data for the given zipcode.
#
def processWeatherData(db, zipcode, weatherData):

    weatherData = preProcessWeatherData( weatherData )

    logTraceWeatherData( zipcode, weatherData )

    # Check for nearby tstorms
    if isTstormInForecast( weatherData["hourly_forecast"][0:3] ):
        msgs = buildTstormWarningMessages( zipcode, weatherData["hourly_forecast"][0:3] )
        upsertMessages( db, msgs )

    if isTimeForMorningForecast( weatherData["hourly_forecast"][0]["FCTTIME"] ):
        msg = buildMorningForecastMsg( zipcode, weatherData["hourly_forecast"] )
        upsertMessage( db, msg )

    if isTimeForEveningForecast( weatherData["hourly_forecast"][0]["FCTTIME"] ):
        msgs = buildEveningForecastMsgs( zipcode, weatherData["hourly_forecast"] )
        upsertMessages( db, msgs )



#
#  Fetch weather data from wunderground for each zipcode in db and process it.
#
def fetchAndProcessWeatherData(args): 

    args['--mongouri'] = decryptCreds( os.environ["ARI_MONGO_URI"] )
    args = verifyArgs( args , required_args = [ '--mongouri' ] )

    # fetch the list of zipcodes from the users collection
    db = getMongoDb( args["--mongouri"] )
    zipcodes = db["/ari/users"].distinct( "zipcode" )

    for zipcode in zipcodes:
        weatherData = fetchWeatherData(zipcode)
        processWeatherData(db, zipcode, weatherData)

#
# Load weather data from file and process it.
#
def loadAndProcessWeatherData(args): 

    args['--mongouri'] = decryptCreds( os.environ["ARI_MONGO_URI"] )
    args = verifyArgs( args , required_args = [ '--mongouri', '--zipcode', '--inputfile' ] )

    db = getMongoDb( args["--mongouri"] )

    zipcode = args["--zipcode"]
    weatherData = readJson( args["--inputfile"] )

    processWeatherData(db, zipcode, weatherData)


#
# @return a user dict
#
def buildUser(args):
    retMe = {}
    retMe["_id"] = args["--user"]
    retMe["zipcode"] = args["--zipcode"] 
    retMe["notificationEmail"] = encryptCreds( args["--notificationEmail"] )
    # retMe["zipcodeTimeZone"] = fetchTimeZone( retMe["zipcode"] )
    return retMe



#
# Add a user to the db.
#
def addUser(args):

    args['--mongouri'] = decryptCreds( os.environ["ARI_MONGO_URI"] )
    args = verifyArgs( args , required_args = [ '--mongouri', '--user', '--zipcode', '--notificationEmail' ] )

    db = getMongoDb( args["--mongouri"] )

    newUser = buildUser(args)

    logTrace("addUser: adding", json.dumps(newUser))

    db["/ari/users"].update_one( { "_id": newUser["_id"] }, 
                                 { "$set": newUser }, 
                                 upsert=True )


#
# Fetch the list of distinct zipcodes from the users collection.
#
def getDistinctZipcodes(args):

    args['--mongouri'] = decryptCreds( os.environ["ARI_MONGO_URI"] )
    args = verifyArgs( args , required_args = [ '--mongouri' ] )

    db = getMongoDb( args["--mongouri"] )
    zipcodes = db["/ari/users"].distinct( "zipcode" )
    logTrace("getDistinctZipcodes:", zipcodes)


#
#
#
def playWithDates(args):

    d = date.today()
    logTrace("playWithDates: date.today():", d, d.strftime("%a %m/%d/%Y %H:%M:%S %z %Z"))

    n = datetime.now()
    logTrace("playWithDates: datetime.now():", n, n.strftime("%a %m/%d/%Y %H:%M:%S z=%z Z=%Z"))

    n = datetime.utcnow()
    logTrace("playWithDates: datetime.utcnow():", n, n.strftime("%a %m/%d/%Y %H:%M:%S z=%z Z=%Z"))

    n = datetime.now().isoformat(' ')
    logTrace("playWithDates: datetime.now().isoformat():", n)

    n = datetime.now(tz=pytz.utc)
    logTrace("playWithDates: datetime.now(tz=pytz.utc):", n, n.strftime("%a %m/%d/%Y %H:%M:%S z=%z Z=%Z"))

    tz = pytz.timezone("America/Denver")
    n = datetime.now(tz=tz)
    logTrace("playWithDates: datetime.now(tz=pytz.timezone(America/Denver)):", n, n.strftime("%a %m/%d/%Y %H:%M:%S z=%z Z=%Z"))

    n = datetime.now(tz=pytz.timezone("America/New_York"))
    logTrace("playWithDates: datetime.now(tz=pytz.timezone([merica/New_York)):", n, n.strftime("%a %m/%d/%Y %H:%M:%S z=%z Z=%Z"))


#
# ---- encryption ----------------------------------------------

#
# @return the string s, padded on the right to the nearest multiple of bs.
#         the pad char is the ascii char for the pad length.
#
def pad(s, bs):
    retMe = s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
    # print("pad: retMe: #" + retMe + "#")
    return retMe


#
# @param s a string or byte[] previously returned by pad. 
#          assumes the pad char is equal to the length of the pad
#
# @return s with the pad on the right removed.
#
def unpad(s):
    retMe = s[:-ord(s[len(s)-1:])]
    # print("unpad: retMe:", retMe)
    return retMe


#
# @param key - key size can be 16, 24, or 32 bytes (128, 192, 256 bits)
#              You must use the same key when encrypting and decrypting.
# @param msg - the msg to encrypt
#
# @return base64-encoded ciphertext
#
def encrypt(key, msg):
    msg = pad(msg, AES.block_size)

    #
    # iv is like a salt.  it's used for randomizing the encryption
    # such that the same input msg isn't encoded to the same cipher text
    # (so long as you use a different iv).  The iv is then prepended to
    # the ciphertext.  Before decrypting, you must remove the iv and only
    # decrypt the ciphertext.
    #
    # Note: AES.block_size is always 16 bytes (128 bits)
    #
    iv = Random.new().read(AES.block_size)

    cipher = AES.new(key, AES.MODE_CBC, iv)

    #
    # Note: the iv is prepended to the encrypted message
    # encryptedMsg is a base64-encoded byte[] 
    # 
    return base64.b64encode(iv + cipher.encrypt(msg))


#
# @param key - key size can be 16, 24, or 32 bytes (128, 192, 256 bits)
#              You must use the same key when encrypting and decrypting.
# @param encryptedMsg - the msg to decrypt (base64-encoded), previously returned 
#                       by encrypt.  First 16 bytes is the iv (salt)
#
def decrypt(key, encryptedMsg):
    enc = base64.b64decode(encryptedMsg)
    iv = enc[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')


#
# @return AES-encrypted creds
#
def encryptCreds( creds ):
    key = os.environ['ARI_AES_KEY'].encode('utf-8')
    return encrypt(key, creds).decode('utf-8')


#
# @return AES-derypted creds
#
def decryptCreds( encCreds ):
    key = os.environ['ARI_AES_KEY'].encode('utf-8')
    return decrypt(key, encCreds )






#
# main entry point ---------------------------------------------------------------------------
# 
args = verifyArgs( parseArgs() , required_args = [ '--action' ] )
logTrace("main: verified args=", args)


if args["--action"] == "fetchAndProcessWeatherData":
    fetchAndProcessWeatherData(args)

elif args["--action"] == "downloadWeatherData":
    downloadWeatherData(args)

elif args["--action"] == "loadAndProcessWeatherData":
    loadAndProcessWeatherData(args)

elif args["--action"] == "addUser":
    addUser(args)

elif args["--action"] == "getDistinctZipcodes":
    getDistinctZipcodes(args)

elif args["--action"] == "playWithDates":
    playWithDates(args)

elif args["--action"] == "sendEmail":
    sendEmail(args)

elif args["--action"] == "sendNotifications":
    sendNotifications(args)

elif args["--action"] == "encryptCreds":
    args = verifyArgs( args , required_args = [ '--msg' ] )
    logInfo("encryptCreds:", encryptCreds(args["--msg"]) )

elif args["--action"] == "fetchAndProcessWeatherData+sendNotifications":
    fetchAndProcessWeatherData(args)
    sendNotifications(args)



else:
    logError( "main: Unrecognized action: " + args["--action" ] )


