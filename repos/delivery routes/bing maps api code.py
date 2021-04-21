import urllib.request
import json

# Your Bing Maps Key 
bingMapsKey = "Au5hDbyQjjSaQY7L2mARJHMG1_922wzhfXmSaytIdku_AvBI3pmyY98tTp-imkSf"

# input information

#pointA (Leslie's House)
leslielat = 25.86288760266286 
leslielon= -80.24720464588125


#pointB
destination = "16141 Blatt Blvd Weston FL 33326"



# The general form is

# http://dev.virtualearth.net/REST/V1/Routes/Driving?wp.0=STARTLAT,STARTLONG&wp.1=1427%20Alderbrook%20Ln%20San%20Jose%20CA%2095129&key=YOUR_BING_MAPS_KEY

encodedDest = urllib.parse.quote(destination, safe='')

routeUrl = "http://dev.virtualearth.net/REST/V1/Routes/Driving?wp.0=" + str(leslielat) + "," + str(leslielon) + "&wp.1=" + encodedDest + "&key=" + bingMapsKey

request = urllib.request.Request(routeUrl)
response = urllib.request.urlopen(request)

r = response.read().decode(encoding="utf-8")
result = json.loads(r)

print(result)

# itineraryItems = result["resourceSets"][0]["resources"][0]["travelDistance"]

# for item in itineraryItems:
#     print(item["instruction"]["text"])