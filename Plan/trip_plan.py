import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import os
from sklearn.cluster import KMeans
from Data.Read_data import *
from Sort.sort import *
from Plot.plot_to_rtf import *
from geopy.distance import vincenty

class trip_plan:
	"""
	This class trip_planner will create the travel route for users automatically based on 
	three input filters they input: travel time, budget, schedule.
	We use K-means algorithm to calculate the optimal travel route and revise the K-means algorithm to return 
	k nearest neighboorhoods that each clusters have the same number of elements.
	"""
	def __init__(self, time, bugdet, degree):
		#constructor
		self.time = time
		self.bugdet = bugdet
		self.degree = degree

	def trip_planer(self, time, bugdet, degree):
		"""
		This function first read data 'trip_plan.csv'. Then, we use Kmeans algorithm to calculate the optimal center points 
		of each day, and use revised_kmeans algorithm to make every clusters have the same number of elements. Finally, we 
		call the function 'write_trip_plan_to_rtf' in the module 'plot_to_rtf' of Plot directory.

		Parameters:
			time: int
			budget: string
			degree: int
		"""
		try:
			path = os.getcwd()
			travel_data = pd.read_csv(path + '/Data/trip_plan.csv', encoding = 'latin1') 
		except IOError:
			print("Error: can\'t find file or read data")

		#calculate the total_num_attractions based on 
		if (degree == 1):
			total_num_attractions = time * 2
		elif (degree == 2):
			total_num_attractions = time * 4

		#transform input parameter budget to a reasonable list
		if (bugdet == 1):
			bugdet_list = [1,2]
		elif (bugdet == 2):
			bugdet_list = [3,4]
		elif (bugdet == 3):
			bugdet_list = [5]

		recommended_attraction = travel_data.iloc[:total_num_attractions, :]
		recommended_attraction = recommended_attraction.replace(to_replace= '-999', value='N.A.')

		cordinate_data = []

		for i in range(recommended_attraction.shape[0]):
			temp = []
			temp.append(recommended_attraction['lat'].iloc[i])
			temp.append(recommended_attraction['lng'].iloc[i])
			cordinate_data.append(temp)

		kmeans = KMeans(n_clusters = time, random_state = 0).fit(cordinate_data)
		
		a = pd.Series(kmeans.labels_)
		index_list = {}
		for i in range(time):
			index_list[i] = (a[a == i].index.tolist())
		order_list = sorted(index_list, key=lambda k: len(index_list[k]), reverse = True)

		center_points = kmeans.cluster_centers_

		index_list, center_points = self.revised_kmeans(index_list, order_list, cordinate_data, center_points, time, degree)

		center_points = np.asarray(center_points)
		
		recommendation_order = np.random.permutation(time)
		recommended_center = center_points[recommendation_order, :]

		write_trip_plan_to_rtf(index_list, recommendation_order, recommended_center, recommended_attraction, bugdet_list)

	def distance(self, lat1,lng1,lat2,lng2):
		"""
		This method calculate the distance of two cordinates in miles.
		Parameters:
			lat1: float (latitute)
			lng1: float (longitude)
			lat2: float (latitude)
			lng2: float (longitude)

		Return:
			d: float
		"""
		add1 = (lat1,lng1)
		add2 = (lat2,lng2)
		d = vincenty(add1, add2).miles
		return d

	def generate_combined_dataset(self, d1,d2):
    '''
    This is to generate a combined and sorted dataset of museums and attractions for trip planning

    Parameters:
    	d1: dataframe
    	d2: dataframe

    	Return:
    		combined_df
    '''

	    combined_df = pd.concat([d1,d2],ignore_index=True)
	    combined_df = combined_df.drop_duplicates(subset=['name'],keep='first')
	    combined_df = sort_trip(combined_df).reset_index(drop=True)
	    return combined_df

	def revised_kmeans(self, index_list, order_list, cordinate_data, center_points, time, degree):
		"""
		This method revises the Kmeans method to return k nearest neighboorhoods that each clusters have the same number of elements.
		
		Parameters:
			index_list: list of list of int
			order_list: list of int
			cordinate_data: Dataframe
			center_points: list of list float
			time: int
			degree: string

		Return:
			index_list: list of list of int 
			center_points: list of list of point
		"""
		for k, i in enumerate(order_list):
			if (degree == 1):
				n = len(index_list[i]) - 2
			elif (degree == 2):
				n = len(index_list[i]) - 4
			for x in range(n):
	            #find max distance
				d = 0
				max_index = 0
				for index in range(len(index_list[i])):
					if (d < self.distance(cordinate_data[index][0], cordinate_data[index][1],center_points[i][0], center_points[i][1])):
						d = self.distance(cordinate_data[index][0], cordinate_data[index][1],center_points[i][0], center_points[i][1])
						max_index = index
	            #calculate minimal distance to a cluster j, j != i
				d = 10000
				min_index = 0
				for index in order_list[k+1:]:
					if (d > self.distance(cordinate_data[max_index][0], cordinate_data[max_index][1],center_points[index][0], center_points[index][1])):
						d = self.distance(cordinate_data[max_index][0], cordinate_data[max_index][1],center_points[index][0], center_points[index][1])
						min_index = index
				#add
				index_list[min_index].append(index_list[i][max_index])
				#delete
				del index_list[i][max_index]
	        #recalculate centroids    
			center_points = []
			for j in range(time):
				cordinate_subdata = [cordinate_data[h] for h in index_list[j]]
				kmeans = KMeans(n_clusters=1, random_state=0).fit(cordinate_subdata)
				center_points.append([kmeans.cluster_centers_[0][0], kmeans.cluster_centers_[0][1]])
		return index_list, center_points	














