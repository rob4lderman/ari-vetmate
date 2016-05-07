#!/usr/bin/python3
#
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

#        datestr = datestr + " {}".format( date.today().year )
#        tmpdate = datetime.strptime(datestr, "%b %d %Y")
#        return tmpdate.strftime("%m/%d/%y")
# https://docs.python.org/3.3/library/datetime.html#strftime-strptime-behavior
from datetime import date, datetime, timedelta, timezone
import pytz


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
# TODO
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
def sendNotificationViaEmail( fromAddr, fromPass, toAddr, subject, msg):

    logTrace("sendNotificationViaEmail: fromAddr:", fromAddr,
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
# Send an email.
#
def sendEmail(args):

    args['--gmailuser'] = os.environ["gmailuser"]
    args['--gmailpass'] = os.environ["gmailpass"]

    args = verifyArgs( args , required_args = [ '--toaddr', '--subject', '--msg', '--gmailuser', '--gmailpass' ] )

    sendNotificationViaEmail( args['--gmailuser'],
                              args['--gmailpass'],
                              args['--toaddr'],
                              args['--subject'],
                              args['--msg'] )



# -rx- #
# -rx- # TODO
# -rx- # Send notification!
# -rx- # Note: need to enable "less secure apps" in gmail: https://www.google.com/settings/security/lesssecureapps
# -rx- #
# -rx- def sendEmailSummary( args ):
# -rx- 
# -rx-     message = Message(From=args["--gmailuser"],
# -rx-                       To=args["--to"])
# -rx- 
# -rx-     message.Subject = "ThinMint Daily Account Summary"
# -rx- 
# -rx-     emailLinesText = readLines( args["--inputfile"] )
# -rx-     emailLinesHtml = readLines( args["--inputfile"] + ".html" )
# -rx- 
# -rx-     message.Html = "".join( emailLinesHtml )
# -rx-     message.Body = "\n".join( emailLinesText )
# -rx- 
# -rx-     sender = Mailer('smtp.gmail.com', 
# -rx-                      port=587,
# -rx-                      use_tls=True, 
# -rx-                      usr=args["--gmailuser"],
# -rx-                      pwd=args["--gmailpass"] )
# -rx-     sender.send(message)


#
# @return a ref to the mongo db by the given name.
#
def getMongoDb( mongoUri ):
    dbname = mongoUri.split("/")[-1]
    mongoClient = MongoClient( mongoUri )
    print("getMongoDb: connected to {}, database {}".format( mongoUri, dbname ) )
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
# condition - icon
# Chance of Flurries	    chanceflurries	
# Chance of Rain	        chancerain	
# Chance Rain	            chancerain	
# Chance of Freezing Rain	chancesleet	
# Chance of Sleet	        chancesleet	
# Chance of Snow	        chancesnow	
# Chance of Thunderstorms	chancetstorms	
# Chance of a Thunderstorm	chancetstorms	
# Clear	                    clear	
# Cloudy	                cloudy	
# Flurries	                flurries	
# Fog	                    fog	
# Haze	                    hazy	
# Mostly Cloudy	            mostlycloudy	
# Mostly Sunny	            mostlysunny	
# Partly Cloudy	            partlycloudy	
# Partly Sunny	            partlysunny	
# Freezing Rain	            sleet	
# Rain	                    rain	
# Sleet	                    sleet	
# Snow	                    snow	
# Sunny	                    sunny	
# Thunderstorms	            tstorms	
# Thunderstorm	            tstorms	
# Unknown	                unknown	
# Overcast	                cloudy	
# Scattered Clouds	        partlycloudy	

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
# TODO: need to update tz from time to time in order to adjust from daylight time to standard time, e.g.
#       or maybe not... if using tz_long...
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
    retMe["msg"] = "{0}% chance of thunderstorms at {1}".format( hourly_forecast["pop"],
                                                                              hourly_forecast["FCTTIME"]["civil"] )
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
    sendNotificationViaEmail( os.environ["gmailuser"],
                              os.environ["gmailpass"],
                              user["notificationEmail"],
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

    args['--gmailuser'] = os.environ["gmailuser"]
    args['--gmailpass'] = os.environ["gmailpass"]
    args['--mongouri'] = os.environ["mongouri"]

    args = verifyArgs( args , required_args = [ '--mongouri', '--gmailuser', '--gmailpass' ] )

    db = getMongoDb( args["--mongouri"] )

    unsentMsgs = getUnsentMessages(db)

    for msg in unsentMsgs:
        users = getUsersInZipcode( db, msg["zipcode"] )
        sendMessageToUsers(msg, users)
        msg["hasBeenSent"] = True
        upsertMessage(db, msg)


#
# Process the weather data for the given zipcode.
#
def processWeatherData(db, zipcode, weatherData):

    logTraceWeatherData( zipcode, weatherData )

    # TODO
    if isTstormInForecast( weatherData["hourly_forecast"][0:3] ):
        msgs = buildTstormWarningMessages( zipcode, weatherData["hourly_forecast"][0:3] )
        upsertMessages( db, msgs )

    # if isTimeForMorningForecast( weatherData["hourly_forecast"][0]["FCTTIME"] ):
    #     queueMorningForecastMessage( zipcode, weatherData )
    # elif isTimeForEveningForecast( weatherData["hourly_forecast"][0]["FCTTIME"] ):
    #     queueEveningForecastMessage( zipcode, weatherData )



#
#  Fetch weather data from wunderground for each zipcode in db and process it.
#
def fetchAndProcessWeatherData(args): 

    args['--mongouri'] = os.environ["mongouri"]
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

    args['--mongouri'] = os.environ["mongouri"]
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
    retMe["notificationEmail"] = args["--notificationEmail"]
    retMe["zipcodeTimeZone"] = fetchTimeZone( retMe["zipcode"] )
    return retMe



#
# Add a user to the db.
#
def addUser(args):

    args['--mongouri'] = os.environ["mongouri"]
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

    args['--mongouri'] = os.environ["mongouri"]
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


else:
    logError( "main: Unrecognized action: " + args["--action" ] )


