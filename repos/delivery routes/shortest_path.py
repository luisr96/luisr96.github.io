import urllib.request
import requests
import json
import pandas as pd
import random
import csv

num = 14

# import file
# file should have 4 columns: Client, Latitude, Longitude, Cluster
df = pd.read_csv(f"deliverydata_cluster{num}.csv")

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

def byCluster(i):
	print("\n")
	print(f"Distance for Cluster {i}:")
	print(distancebycluster[i])
	print("\n")
	print(f"Time for Cluster {i}:")	
	print(timebycluster[i])
	print("\n")
	print(f"Routing for Cluster {i}:")
	print(routing[i])


programrunner = 0
runthismanytimes = 20

while programrunner <= runthismanytimes:

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

		# randomly shuffle the rows
		df_iter = df_iter.sample(frac=1).reset_index(drop=True)


		print(df_iter)

		# save IDs for routing
		routinglist = df_iter['ID'].tolist()
		# puts 0 at the end to represent going back home after finishing cluster
		routinglist.insert(len(routinglist),0)

		# put ID list in dictionary
		routing[i] = routinglist

		# put 0 at the beginning of routing list, to represent friend's house
		routinglist.insert(0, 0)

		# reverses the list. how the algo is set up right now, it calculates it in reverse order. so we have to reverse it.
		routinglist = routinglist.reverse()

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

	print("\n")
	# prints routes by ids. all routes begin with 0 bc they start from friend's house
	print("Routes by Client IDs:")
	print(routing)

	# byCluster(8)

	# print(df_iter_storer[5])

	# print("")
	# print(sum(distancebycluster[0]))
	# print(sum(timebycluster[1]))


	distancedict = distancebycluster
	timedict = timebycluster
	columnlabels = []
	i=0
	for i in range(df['cluster_label'].min(), df['cluster_label'].max()+1):
		distancedict[i] = sum(distancebycluster[i])
		timedict[i] = sum(timebycluster[i])

	distancedict['Total'] = sum(distancebycluster.values())
	timedict['Total'] = sum(timebycluster.values())

	with open(f"distancesbycluster_{df['cluster_label'].max()+1}.csv", 'w') as f:  # You will need 'wb' mode in Python 2.x
	    w = csv.DictWriter(f, distancedict.keys())
	    w.writeheader()
	    w.writerow(distancedict)
	    w.writerow(routing)

	with open(f"timesbycluster_{df['cluster_label'].max()+1}.csv", 'w') as f: 
	    w = csv.DictWriter(f, timedict.keys())
	    w.writeheader()
	    w.writerow(timedict)
	    w.writerow(routing)


	with open(f"competition.csv", 'a') as f: 
	    w = csv.DictWriter(f, timedict.keys())
	    w.writeheader()
	    w.writerow(timedict)
	    w.writerow(routing)


	print(f"{programrunner}/{runthismanytimes}")
	programrunner += 1





