
# Ari''s T-Storm Alerts App for Dog Owners

---------------------------------------------------------------------------------------------
## TODO

done: sms messages: http://tinywords.com/about-old/mobile/
      you can send an email to the phone's email address (see table in link above) and it
      will show up as an SMS message!  This is what we want!  don't even need an app!  

* Alltel: 300 characters: [10-digit phone number]@message.alltel.com 
* AT&T Wireless (now part of Cingular): 160 characters: [10-digit phone number]@mmode.com 
* Boost Mobile: 500 characters: [10-digit phone number]@myboostmobile.com 
* Cingular: 150 characters: [10-digit phone number]@mobile.mycingular.com OR [10-digit number]@cingularme.com 
* Metrocall: 80 to 200 characters, depending on subscription plan: [10-digit pager number]@page.metrocall.com 
* Nextel (now part of Sprint Nextel): 140 characters: [10-digit telephone number]@messaging.nextel.com 
* Sprint PCS (now Sprint Nextel): 160 characters: [10-digit phone number]@messaging.sprintpcs.com 
* T-Mobile: 140 characters: [10-digit phone number]@tmomail.net 
* Verizon: 160 characters: [10-digit phone number]@vtext.com 
* Virgin Mobile USA: 160 characters: [10-digit phone number]@vmobl.com 

TODO: iphone app
TODO: android app
    

TODO: current conditions
      http://api.wunderground.com/api/3d32d71a6c117bb4/conditions/q/80304.json



---------------------------------------------------------------------------------------------
## Example wuclient.py commands


    ./wuclient.py --action addUser \
                  --user "robertgalderman@gmail.com" \
                  --notificationEmail "xxxxxxxxxx@tmomail.net" \
                  --zipcode 80304
    
    ./wuclient.py --action fetchAndProcessWeatherData 
    
    ./wuclient.py --action sendNotifications
    
    ./wuclient.py --action fetchAndProcessWeatherData+sendNotifications
    
    ./wuclient.py --action downloadWeatherData \
                  --zipcode "80304" \
                  --outputfile data/80304.json
    
    ./wuclient.py --action loadAndProcessWeatherData \
                  --zipcode "80304" \
                  --inputfile data/80304.json
    
    ./wuclient.py --action sendEmail \
                  --toaddr "xxxxxxxxxx@tmomail.net" \
                  --subject "STORM ALERT!" \
                  --msg "STORM ALERT: 71% chance of thunderstorms at 6:00 PM"


---------------------------------------------------------------------------------------------
## Heroku commands

    heroku login
    heroku create
    heroku config:set ARI_MONGO_URI=...
    heroku config:set ARI_CREDS=...
    heroku config:set ARI_AES_KEY=...
    
    # run one-off dyno immediately
    heroku run go
    
    # cron scheduler
    heroku addons:create scheduler:standard
    heroku addons:open scheduler
    Add Job -> run -> Hourly -> Next: :30 Dyno: Free/Hobby
    
    # send email
    heroku addons:create postmark:10k
    
    heroku config:get POSTMARK_API_TOKEN -s  >> .env
    heroku config:get POSTMARK_SMTP_SERVER -s  >> .env
    heroku config:get POSTMARK_INBOUND_ADDRESS -s  >> .env



---------------------------------------------------------------------------------------------
## Notifications

Need to keep track of notifications, so that i don't send repeated notifications for the 
same weather event.

Notifications should be sent at ideal times, e.g:

* a notification in the evening for weather events overnight or the next day
* a notification in the morning for weather events that day
* a notification for unexpected weather alerts at any time during the day


---------------------------------------------------------------------------------------------
## Weather API


WeatherUnderground API:   
https://www.wunderground.com/weather/api/d/pricing.html

* FREE: 500 calls/day (1 call/2.88 mins); 10 calls/min   
* API KEY: 3d32d71a6c117bb4   

* TODO: need to gen new key and answer "Yes" to "Will it be used for commercial purposes?"
* TODO: need a domain and a sender signature from that domain (setup forwarding via namecheap)
* TODO: hide the API KEY in an env variable 


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



