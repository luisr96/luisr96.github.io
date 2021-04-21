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
df = pd.read_csv(f"OrderLog_geocodio_8779ba5d6a16d021219cbd7cd4c5efbb242eb660.csv")

# make a dataframe with all rows, and only the following columns:
df_deliveries = df.loc[:,['ID', 'Client','Latitude','Longitude']]

# remove the pandas index column and set it to the ID
df_deliveries.set_index('ID', inplace=True)

df_minimums = pd.DataFrame(columns=['ID', 'Client','Latitude','Longitude'])




limit = len(df_deliveries.index)


print(df_minimums)


distancecolumn = []
timecolumn = []



# coordinates of start location
homelat = 25.86288760266286 
homelon= -80.24720464588125
startlat = homelat
startlon = homelon



while len(df_minimums.index) != limit:

	# create the distance/duration data
	for i in df_deliveries.index: # for as many rows as there are

		distance, duration = goTo(startlat, startlon, df_deliveries.at[i, 'Latitude'], df_deliveries.at[i, 'Longitude'])

		distancecolumn.append(distance)
		timecolumn.append(duration)


	# add the data as columns to df
	df_deliveries['Distance_from_Last'] = distancecolumn
	df_deliveries['Time_from_Last'] = timecolumn
	print(df_deliveries)


	# dataframe of closest point
	df_closest = df_deliveries[df_deliveries.Time_from_Last==df_deliveries.Time_from_Last.min()]
	print(df_closest)

	# latitude of closest point
	closestlat = df_closest['Latitude'].values[0]
	print(closestlat)

	# longitude of closest point
	closestlon = df_closest['Longitude'].values[0]
	print(closestlon)


	#., "go" there and save the data
	distance, duration = goTo(startlat, startlon, closestlat, closestlon)
	print(distance)
	print(duration)


	##add closest point to df of minimums
	df_minimums = df_minimums.append(df_closest)

	# delete min row
	df_deliveries = df_deliveries.loc[df_deliveries['Time_from_Last']!=df_deliveries['Time_from_Last'].min()]

	print(df_deliveries)



	startlat = closestlat
	startlon = closestlon

	distancecolumn = []
	timecolumn = []


	print(df_minimums)




# set the index as the 'ID' for minimum dataframe
df_minimums['ID'] = df_minimums.index
df_minimums.set_index('ID', inplace=True)


print(masterdistance)
print(mastertime)
print(masterrouting)

print(df_minimums)

df_minimums.to_csv('route.csv')