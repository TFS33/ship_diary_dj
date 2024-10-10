from __future__ import print_function
import time
import weatherapi
from weatherapi.rest import ApiException
from pprint import pprint
import requests
from diary.helpers.credentials.weather_api import WEATHER_API_KEY


# # Configure API key authorization: ApiKeyAuth
# configuration = weatherapi.Configuration()
# configuration.api_key['key'] = WEATHER_API_KEY
# # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# # configuration.api_key_prefix['key'] = 'Bearer'
#
# # create an instance of the API class
# api_instance = weatherapi.APIsApi(weatherapi.ApiClient(configuration))
# q = "188.69.184.99"  # str | Pass US Zipcode, UK Postcode, Canada Postalcode, IP address, Latitude/Longitude (decimal degree) or city name. Visit [request parameter section](https://www.weatherapi.com/docs/#intro-request) to learn more.
# dt = '2023-10-20' # date | Date on or after 1st Jan, 2015 in yyyy-MM-dd format
#
# try:
#     # Astronomy API arba kiti
#     api_response = api_instance.ip_lookup(q)
#     pprint(api_response)
# except ApiException as e:
#     print(f"Exception when calling APIsApi->astronomy: %s\n" % e)


"""
All URIs are relative to https://api.weatherapi.com/v1

Class	Method	HTTP request	Description
APIsApi	astronomy	GET /astronomy.json	Astronomy API
APIsApi	forecast_weather	GET /forecast.json	Forecast API
APIsApi	future_weather	GET /future.json	Future API
APIsApi	history_weather	GET /history.json	History API
APIsApi	ip_lookup	GET /ip.json	IP Lookup API
APIsApi	marine_weather	GET /marine.json	Marine Weather API
APIsApi	realtime_weather	GET /current.json	Realtime API
APIsApi	search_autocomplete_weather	GET /search.json	Search/Autocomplete API
APIsApi	time_zone	GET /timezone.json	Time Zone API
"""

from datetime import datetime

print(datetime.now())
