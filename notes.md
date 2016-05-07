

smtplib.SMTPAuthenticationError: (534, b'5.7.14 <
https://accounts.google.com/signin/continue?sarp=1&scc=1&plt=AKgnsbvd
\n5.7.14 3F353-iUfA_DgvkU0wGEqYc_YSS_mrEqnZyTl1xkdr8VSsZcxeM-NKkHbS8iQ6wzse_SnD\n5.7.14 27eHnNiiWuY9vSDfbGQOkV-K2j7jvXhmhy-yby2Yp_ZAtmZx4r
BExEqiEEf4yYYo9yVuOl\n5.7.14 8IuVh3ql6TbS2SzaVj6EOMtRmNqWK89ekd3eFQJUj7Jl296kOvCDqBNHkd4TFHp6uIhEV0\n5.7.14 y9aFFbFlQkCsTgubfsIn
7SlTI2aV4> Please log in via your web browser and\n5.7.14 then try again.\n5.7.14  Learn more at\n5.7.14  https://support.google
.com/mail/answer/78754 l66sm7355431qhc.42 - gsmtp')

# Ari''s T-Storm Alerts App for Dog Owners


./wuclient.py --action addUser \
              --user "robertgalderman@gmail.com" \
              --notificationEmail "8454897099@tmomail.net" \
              --zipcode 80304

./wuclient.py --action fetchAndProcessWeatherData 

./wuclient.py --action sendNotifications


./wuclient.py --action downloadWeatherData \
              --zipcode "80304" \
              --outputfile data/80304.json

./wuclient.py --action loadAndProcessWeatherData \
              --zipcode "80304" \
              --inputfile data/80304.json

./wuclient.py --action sendEmail \
              --toaddr "8454897099@tmomail.net" \
              --subject "STORM ALERT!" \
              --msg "STORM ALERT: 71% chance of thunderstorms at 6:00 PM"



---------------------------------------------------------------------------------------------
## Heroku commands:

heroku login
heroku create
heroku config:set ARI_MONGO_URI=...
heroku config:set ARI_CREDS=...
heroku config:set ARI_AES_KEY=...

heroku run run

heroku addons:create scheduler:standard

# go to scheduler on web dashboard
heroku addons:open scheduler
Add Job -> run -> Hourly -> Next: :30 Dyno: Free


heroku addons:create postmark:10k
heroku config:get POSTMARK_API_TOKEN -s  >> .env
heroku config:get POSTMARK_SMTP_SERVER -s  >> .env
heroku config:get POSTMARK_INBOUND_ADDRESS -s  >> .env


---------------------------------------------------------------------------------------------
## TODO

TODO: python app 
      runs periodically (once every 5 mins? 30mins?  )
        - note: 1 API call per zipcode.
      fetch data
      check for tstorm alerts
      check for tstorms in 36-hour forecast
      if (tstorm): send push notification
      done.


TODO: mongodb - user registry.  email, password, location, push notification info
      python batch app reads user locations from db
      gets weather info and sends push notifications

TODO: sms messages: http://tinywords.com/about-old/mobile/
      you can send an email to the phone's email address (see table in link above) and it
      will show up as an SMS message!  This is what we want!  don't even need an app!  
      8454897099@tmomail.net

TODO: iphone app
TODO: android app
    
TODO: % chance of precip/t-storm ? "pop" field


TODO: geolookup to get zipcode timezone
      http://api.wunderground.com/api/3d32d71a6c117bb4/geolookup/q/80304.json
        {
            "response": {
                "version":"0.1",
                "termsofService":"http://www.wunderground.com/weather/api/d/terms.html",
                "features": {
                    "geolookup": 1
                }
            },	
            "location": {
                "type":"CITY",
                "country":"US",
                "country_iso3166":"US",
                "country_name":"USA",
                "state":"CO",
                "city":"Boulder",
                "tz_short":"MDT",
                "tz_long":"America/Denver",
                "lat":"40.03531647",
                "lon":"-105.28376770",
                "zip":"80304",
                "magic":"1",
                "wmo":"99999",
                "l":"/q/zmw:80304.1.99999",
                "requesturl":"US/CO/Boulder.html",
                "wuiurl":"http://www.wunderground.com/US/CO/Boulder.html",
                "nearby_weather_stations": {
                    ...
                }
            }
        }

    {
      "response": {
      "version":"0.1",
      "termsofService":"http://www.wunderground.com/weather/api/d/terms.html",
      "features": {
      "geolookup": 1
      }
    	}
    		,	"location": {
    		"type":"CITY",
    		"country":"US",
    		"country_iso3166":"US",
    		"country_name":"USA",
    		"state":"NY",
    		"city":"Pleasant Valley",
    		"tz_short":"EDT",
    		"tz_long":"America/New_York",
    		"lat":"41.74496078",
    		"lon":"-73.81787872",
    		"zip":"12569",
    		"magic":"1",
    		"wmo":"99999",
    		"l":"/q/zmw:12569.1.99999",
    		"requesturl":"US/NY/Pleasant_Valley.html",
    		"wuiurl":"http://www.wunderground.com/US/NY/Pleasant_Valley.html",


TODO: current conditions
      http://api.wunderground.com/api/3d32d71a6c117bb4/conditions/q/80304.json


---------------------------------------------------------------------------------------------
## Notifications


Need to keep track of notifications, so that i don't send repeated notifications for the 
same weather event.

Notifications should be sent at ideal times, e.g:

* a notification in the evening for weather events overnight or the next day
* a notification in the morning for weather events that day
* a notification for unexpected weather alerts at any time during the day

* keep track of notifications in db.
* associate with the weather event (so i know i've already sent a notification for this event)
* notification record:
    * message
    * timestamp
    * weatherEvent(s) (some subset of hourly_forecast or alert data)
        * could be several consecutive hourly_forecast records


so.. thunderstorm detected in 36 hour forecast
first time this thunderstorm has been detected
thunderstorm identified by timestamp
queue up notifications
    - notification to be sent 1 hour before
    - notification to be sent morning of (7am)
    - notification to be sent evening before (9pm)
before sending notification, double check that the forecast hasn't changed.

TODO: what to do if tstorm forecast spans consecutive hours?
      condense notifications (mark all notification records as "sent", but send only 1 notification)
TODO: what to do if multiple tstorm forecast on intermittent hours?
      condense morning of/evening before notifications
      send all 1-hour-before notifications

now.. thunderstorm detected in 36 hour forecast
not the first time this thunderstorm has been detected
thunderstorm identified by timestamp
lookup queued notifications for this thunderstorm


how about...
3 types of notifications
morningof: 7am: forecast from 7am to 7pm
evening: 7pm: forecast from 7pm to 7am
+eveningbefore: 7pm: forecast from 7am to 7pm next day
hourbefore: notification of t-storms 1 hour before
so... the weatherunderground api helps because... it's telling me the local time.
the hourly forecasts begin with the next hour.
so if the next hour is, 7am, then that's when we send the daily report
if it's 7pm, we send the nightly and next-day report
if there's a tstorm within the first 2 hours in the forecast, we send a notification.
and we log everytime we send a notification
so that we don't duplicate


I need to know the current time in the user's timezone.


done: at what time within the current hour does the wunderground hourly api start to return the next hour of data (as the first record)?
      immediately: by 04 mins after, it was already showing next hour.
TODO: what time are we checking?  on the half-hour?  once an hour i think is reasonable.

condense weather forecast:
80304 1:00 PM MDT on May 06, 2016 fctcode: 3 icon: mostlycloudy condition: Mostly Cloudy Chance of precip (pop): 15
80304 2:00 PM MDT on May 06, 2016 fctcode: 2 icon: partlycloudy condition: Partly Cloudy Chance of precip (pop): 15
80304 3:00 PM MDT on May 06, 2016 fctcode: 2 icon: partlycloudy condition: Partly Cloudy Chance of precip (pop): 24
80304 4:00 PM MDT on May 06, 2016 fctcode: 15 icon: tstorms condition: Thunderstorm Chance of precip (pop): 76
80304 5:00 PM MDT on May 06, 2016 fctcode: 4 icon: cloudy condition: Overcast Chance of precip (pop): 15
80304 6:00 PM MDT on May 06, 2016 fctcode: 14 icon: chancetstorms condition: Chance of a Thunderstorm Chance of precip (pop): 30
80304 7:00 PM MDT on May 06, 2016 fctcode: 2 icon: partlycloudy condition: Partly Cloudy Chance of precip (pop): 15
80304 8:00 PM MDT on May 06, 2016 fctcode: 2 icon: partlycloudy condition: Partly Cloudy Chance of precip (pop): 15
80304 9:00 PM MDT on May 06, 2016 fctcode: 2 icon: partlycloudy condition: Partly Cloudy Chance of precip (pop): 15
80304 10:00 PM MDT on May 06, 2016 fctcode: 2 icon: partlycloudy condition: Partly Cloudy Chance of precip (pop): 15
80304 11:00 PM MDT on May 06, 2016 fctcode: 2 icon: partlycloudy condition: Partly Cloudy Chance of precip (pop): 15
80304 12:00 AM MDT on May 07, 2016 fctcode: 1 icon: clear condition: Clear Chance of precip (pop): 0
80304 1:00 AM MDT on May 07, 2016 fctcode: 1 icon: clear condition: Clear Chance of precip (pop): 0

isTstormWithinNextThreeHours?
    haveQueuedMessage?
    queueMessage




---------------------------------------------------------------------------------------------
## API


WeatherUnderground API:   
https://www.wunderground.com/weather/api/d/pricing.html

FREE: 500 calls/day (1 call/2.88 mins); 10 calls/min

API KEY: 3d32d71a6c117bb4

TODO: need to gen new key and answer "Yes" to "Will it be used for commercial purposes?"


    GET http://api.wunderground.com/api/{key}/{features}/{settings}/q/{query}.{format}

Note: more than 1 {feature} can be specified, e.g: /alerts/hourly/

    GET http://api.wunderground.com/api/3d32d71a6c117bb4/alerts/hourly/q/80304.json

    curl http://api.wunderground.com/api/3d32d71a6c117bb4/alerts/hourly/q/80304.json
    {
        "response": {
            "version":"0.1",
            "termsofService":"http://www.wunderground.com/weather/api/d/terms.html",
            "features": {
                "alerts": 1 ,
                "hourly": 1
            }
	    },
	    "hourly_forecast": [
	    	{
	    	    "FCTTIME": {
	    	        "hour": "18","hour_padded": "18","min": "00","min_unpadded": "0","sec": "0","year": "2016","mon": "4","mon_padded": "04","mon_abbrev": "Apr","mday": "21","mday_padded": "21","yday": "111","isdst": "1","epoch": "1461283200","pretty": "6:00 PM MDT on April 21, 2016","civil": "6:00 PM","month_name": "April","month_name_abbrev": "Apr","weekday_name": "Thursday","weekday_name_night": "Thursday Night","weekday_name_abbrev": "Thu","weekday_name_unlang": "Thursday","weekday_name_night_unlang": "Thursday Night","ampm": "PM","tz": "","age": "","UTCDATE": ""
	    	    },
	    	    "temp": {"english": "62", "metric": "17"},
	    	    "dewpoint": {"english": "37", "metric": "3"},
	    	    "condition": "Clear",                                       <----------------- https://www.wunderground.com/weather/api/d/docs?d=resources/phrase-glossary
	    	    "icon": "clear",
	    	    "icon_url":"http://icons.wxug.com/i/c/k/clear.gif",
	    	    "fctcode": "1",                                             <----------------- https://www.wunderground.com/weather/api/d/docs?d=resources/phrase-glossary
	    	    "sky": "13",
	    	    "wspd": {"english": "6", "metric": "10"},
	    	    "wdir": {"dir": "S", "degrees": "186"},
	    	    "wx": "Sunny",
	    	    "uvi": "1",
	    	    "humidity": "39",
	    	    "windchill": {"english": "-9999", "metric": "-9999"},
	    	    "heatindex": {"english": "-9999", "metric": "-9999"},
	    	    "feelslike": {"english": "62", "metric": "17"},
	    	    "qpf": {"english": "0.0", "metric": "0"},
	    	    "snow": {"english": "0.0", "metric": "0"},
	    	    "pop": "0",
	    	    "mslp": {"english": "30.04", "metric": "1017"}
	    	},
            {
                ...
            }
	    ],
        "query_zone": "039",
	    "alerts": [ ]
    }



---------------------------------------------------------------------------------------------
## Vision


MVP: app warnings and alerts when t-storms in the forecast or imminent

ADD: general reminders (e.g. for giving medications)
            - VET could input medication schedule into App (easy for owner)

ADD: potty training app (schedule and reminders)

ADD: Comm channel between dog owner and vet
        - immunization schedules and reminders
        - medication schedules and reminders


---------------------------------------------------------------------------------------------
## Prior Art:

* http://weatherpuppy.com/
    * just a pic of a puppy that corresponds to the weather

* http://www.nws.noaa.gov/com/weatherreadynation/wea.html
    * general emergency alerts issued by gov

* http://www.accuweather.com/en/outdoor-articles/outdoor-living/free-smartphone-apps-can-be-li/13927022
    * several apps for weather alerts

* https://itunes.apple.com/us/app/noaa-weather-alert-free/id529051002?mt=8    
    * noaa weather alerts

* http://mashable.com/2013/03/14/apps-for-dogs/#QWCW64jZcEq3
    * list of "must-have apps" for dogowners.  nothing weather-alert-related.



