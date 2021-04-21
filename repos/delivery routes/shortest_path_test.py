import urllib.request
import requests
import json
import pandas as pd
import random

# import file
# file should have 4 columns: Client, Latitude, Longitude, Cluster
df = pd.read_csv('customerdata_clustered_car.csv')

# Your Bing Maps Key 
bingMapsKey="Au5hDbyQjjSaQY7L2mARJHMG1_922wzhfXmSaytIdku_AvBI3pmyY98tTp-imkSf"

# coordinates of start location
homelat = 25.86288760266286 
homelon= -80.24720464588125

iterlat = homelat
iterlon= -homelon

def distanceXtoY(startlat, startlon,endlat, endlon):
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

def clusterinfo(i):
	'''Print the distance/time info for cluster i'''
	print(f"\nCluster {i}")
	print(f"Number of waypoints in Cluster {i}: {rows[i]}\n")
	print(clusters[i])
	print(f"\nDistances: {distancebycluster[i]}")
	print(f"Times: {timebycluster[i]}")

def summary():
	'''Returns a summary for each cluster, which includes
	distance and time for each cluster'''
	summeddistance = 0
	summedtime = 0
	print(f"\nTotal number of waypoints: {len(df.index)}")

	for i in range(df['cluster_label'].min(), df['cluster_label'].max()+1):
		print(f"\nDistance to complete cluster {i}: {sum(distancebycluster[i]):.2f} miles")
		print(f"Time to complete cluster {i}: {sum(timebycluster[i]):.2f} minutes ({(sum(timebycluster[i])/60):.2f} hours)")

		summeddistance += sum(distancebycluster[i])
		summedtime += sum(timebycluster[i])

	print(f"\nTotal distance: {summeddistance:.2f} miles")
	print(f"Total time:     {summedtime:.2f} minutes ({summedtime/60:.2f} hours)")

def optimizeCluster(i):
	df_iter = df.drop(df[df.cluster_label != i].index)


def main():
	# initializations
	i = 0
	x = 0
	times = []
	distances = [] 
	clusters = {}
	distancebycluster = {}
	timebycluster = {}
	iterlistdistances = []
	iterlisttimes = []
	routing = {}
	rows = []
	df_iter_storer = {}

	# for all cluster labels in the data
	for i in range(df['cluster_label'].min(), df['cluster_label'].max()+1):

		# create a new df that deletes all rows not of that cluster label
		df_iter = df.drop(df[df.cluster_label != i].index)

		# store df_iters
		df_iter_storer[i] = df_iter

		# randomly shuffle the rows
		df_iter = df_iter.sample(frac=1).reset_index(drop=True)

		# save IDs for routing
		routinglist = df_iter['ID'].tolist()

		# put ID list in dictionary
		routing[i] = routinglist

		# put 0 at the beginning of routing list, to represent friend's house
		routinglist.insert(0, 0)




		print("\n--------------------------------------------------------------")
		print(f"\nAnalyzing Cluster {i}\n")
		print(df_iter)

		# reset row counter
		rowcounter = 0

		# for each row of a column
		for x in range(0, len(df_iter.index)):

			rowcounter += 1

			# save the current cluster onto dict
			clusters[i] = df_iter

			# save the latitude
			iterlat = clusters[i].iloc[x][2]

			# save the longitude
			iterlon = clusters[i].iloc[x][3]

			# pass through on first row iteration so that iterlatafter !=  iterlat
			# and iterlonafter != iterlon. Difference in lon,lat points lets it 
			# find distances and time
			if x == 0:
				pass
			else:
				distance, duration = distanceXtoY(startlat=iterlat, startlon=iterlon, endlat=iterlatafter, endlon=iterlonafter)

				iterlistdistances.append(distance)
				iterlisttimes.append(duration)

			iterlatafter = iterlat
			iterlonafter = iterlon

			# increment to next row
			x += 1

		# When the cluster finishes,
		# calculate distance from friend's house to first location
		distance, duration = distanceXtoY(startlat=homelat, startlon=homelon, endlat=clusters[i].iloc[-1][2], endlon=clusters[i].iloc[-1][3])

		iterlistdistances.append(distance)
		iterlisttimes.append(duration)

		# and from last last location, to friend's house
		distance, duration = distanceXtoY(startlat=clusters[i].iloc[0][2], startlon=clusters[i].iloc[0][3], endlat=homelat, endlon=homelon)

		iterlistdistances.append(distance)
		iterlisttimes.append(duration)

		# add the cluster's distance/duration info to a dictionary
		distancebycluster[i] = iterlistdistances
		timebycluster[i] = iterlisttimes

		# reset lists to make it free for the next cluster
		iterlistdistances = []
		iterlisttimes = []
		rows.append(rowcounter)

		# increment to next cluster
		i += 1

	return [df_iter_storer, routing, distancebycluster, timebycluster]

maindata = main()
print(maindata[0][0])

optimizeCluster(maindata[0][0])









