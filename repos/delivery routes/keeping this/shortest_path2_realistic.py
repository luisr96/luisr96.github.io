import urllib.request
import requests
import json
import pandas as pd
import random
import csv

# Your Bing Maps Key 
bingMapsKey="Au5hDbyQjjSaQY7L2mARJHMG1_922wzhfXmSaytIdku_AvBI3pmyY98tTp-imkSf"

def goTo(startlat, startlon,endlat, endlon):
	'''Uses Bing Maps API to go from
	startlat,startlon to endlat,endlon
	Traffic info is not used'''
	
	payload = {
    "origins": [{"latitude": startlat, "longitude": startlon}],
    "destinations": [{"latitude": endlat, "longitude": endlon}],
    "travelMode": "driving",
	}

	keydict = {"key": bingMapsKey}

	r = requests.post('https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix', data = json.dumps(payload), params = keydict)

	data = (r.json())

	distance = data['resourceSets'][0]['resources'][0]['results'][0]['travelDistance'] / 1.60934 #convert from km to miles

	duration = data['resourceSets'][0]['resources'][0]['results'][0]['travelDuration']

	print(f"\nFrom: {startlat},{startlon }\nTo: {endlat},{endlon}\nDistance: {distance:.2f} miles\nDuration: {duration:.2f} minutes")

	return distance, duration


# import file
df_deliveries = pd.read_csv(f"OrderLog_geocodio_8779ba5d6a16d021219cbd7cd4c5efbb242eb660.csv")

# make a dataframe with all rows, and only the following columns:
df_deliveries = df_deliveries.loc[:,['ID', 'Client','Latitude','Longitude']]

# remove the pandas index column and set it to the ID
df_deliveries.set_index('ID', inplace=True)


df_route = pd.DataFrame(columns=['ID', 'Client','Latitude','Longitude'])


# coordinates of start location
homelat = 25.86288760266286 
homelon= -80.24720464588125



df_home = pd.read_csv('home.csv')
df_home.set_index('ID', inplace=True)



limit = len(df_deliveries.index)

distancecolumn = []
timecolumn = []




startlat = homelat
startlon = homelon

space = 6
space_counter = 0


while len(df_deliveries.index) != 0:

	if space_counter != space:

		# create the distance/duration data
		for i in df_deliveries.index: # for as many rows as there are

			distance, duration = goTo(startlat, startlon, df_deliveries.at[i, 'Latitude'], df_deliveries.at[i, 'Longitude'])

			distancecolumn.append(distance)
			timecolumn.append(duration)


		# put directions for startlat/lon and all lat/lons in df_deliveries in a column
		df_deliveries['Distance_from_Last'] = distancecolumn
		df_deliveries['Time_from_Last'] = timecolumn
		print(df_deliveries)


		# create dataframe of closest address
		df_closest = df_deliveries[df_deliveries.Time_from_Last==df_deliveries.Time_from_Last.min()]
		print("\nClosest point: \n")
		print(df_closest)


		# its latitude
		closestlat = df_closest['Latitude'].values[0]
		# its longitude
		closestlon = df_closest['Longitude'].values[0]


		# "Go" there and save the data
		distance, duration = goTo(startlat, startlon, closestlat, closestlon)

		# add closest address to route df (was initially empty)
		df_route = df_route.append(df_closest)


		print("\nRoute so far: \n")
		print(df_route)

		# delete min row so we don't go to the same place twice
		df_deliveries = df_deliveries.loc[df_deliveries['Time_from_Last']!=df_deliveries['Time_from_Last'].min()]

		# new start is the last traveled location
		startlat = closestlat
		startlon = closestlon

		# reset these to make new columns
		distancecolumn = []
		timecolumn = []

		space_counter += 1

		continue

	else:

		distance, duration = goTo(startlat, startlon, homelat, homelon)


		df_home.loc[0,'Distance_from_Last'] = distance
		df_home.loc[0,'Time_from_Last'] = duration


		startlat = homelat
		startlon = homelon


		df_route = df_route.append(df_home)

		space_counter = 0

		continue

	space_counter += 1


# set the index as the 'ID' for minimum dataframe
df_route['ID'] = df_route.index
df_route.set_index('ID', inplace=True)


print("\nRoute: \n")
print(df_route)

df_route.to_csv('route_realistic.csv')