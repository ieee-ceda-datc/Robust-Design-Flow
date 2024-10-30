import os
import sys
import json
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


"""
Get the candidate solutions from the csv file
weight_params: [congestion_weight, wirelength_weight, density_weight]
"""

def getCandidateSolutions(file_name : str, 
                          top_n : int, 
                          num_clusters : int, 
                          random_seed : int,    
                          weight_params : list):
    ### read the csv file
    df = pd.read_csv(file_name)
    congestion_list = df['Congestion'].tolist()
    congestion_list = [float(i) for i in congestion_list]

    wirelength_list = df['Wirelength'].tolist()
    wirelength_list = [float(i) for i in wirelength_list]

    density_list = df['Density'].tolist()
    density_list = [float(i) for i in density_list]

    ### Normalize the data (mean = 0.0, std dev = 1.0)
    scaler = StandardScaler()
    congestion_normalized = scaler.fit_transform(np.array(congestion_list).reshape(-1, 1))
    wirelength_normalized = scaler.fit_transform(np.array(wirelength_list).reshape(-1, 1))
    density_normalized = scaler.fit_transform(np.array(density_list).reshape(-1, 1))
    congestion_norm_list = [i[0] for i in congestion_normalized]
    wirelength_norm_list = [i[0] for i in wirelength_normalized]
    density_norm_list = [i[0] for i in density_normalized]
    
    ### Identify the Pareto optimal points
    points = np.array(list(zip(congestion_norm_list, wirelength_norm_list, density_norm_list)))
    # Initialize an empty list to store the Pareto optimal points
    pareto_front = []
    for i, point in enumerate(points):
        dominated = False
        for j, other_point in enumerate(points):
            if i != j:
                if (other_point <= point).all() and (other_point < point).any():
                    dominated = True
                    break
        if not dominated:
            pareto_front.append(point)

    pareto_front = np.array(pareto_front)
    # Separate the Pareto front points into their respective lists
    pareto_congestion = pareto_front[:, 0]
    pareto_wirelength = pareto_front[:, 1]
    pareto_density = pareto_front[:, 2]
    ### get the pareto id
    pareto_id_list = []
    for i in range(len(pareto_front)):
        for j in range(len(points)):
            if (pareto_front[i] == points[j]).all():
                pareto_id_list.append(j)
                break


    results_pareto_id_list = []
    ### Calculate the score of each Pareto optimal point (pick top_n pareto points)
    pareto_front_score = [weight_params[0] * pareto_congestion[i] + weight_params[1] * pareto_wirelength[i] + weight_params[2] * pareto_density[i] for i in range(len(pareto_front))]
    # sort the pareto id list and report the sorted pareto id list
    ordered_list = [i for i in range(len(pareto_id_list))]
    ordered_list = sorted(ordered_list, key=lambda x: pareto_front_score[x], reverse=True)
    sorted_pareto_id_list = [pareto_id_list[i] for i in ordered_list]
    for i in range(top_n):
        results_pareto_id_list.append(sorted_pareto_id_list[i])

    ### Perform K-means clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=random_seed)
    kmeans.fit(pareto_front)
    # Get cluster labels
    labels = kmeans.labels_
    # Get the centroids of the clusters
    centroids = kmeans.cluster_centers_
    ### Identify the pareto point in each cluster
    cluster_pareto_id_list = []
    for i in range(num_clusters):
        min_wirelength = 1e30
        min_wirelength_id = -1
        for i in range(len(labels)):
            if labels[i] == i:
                if wirelength_list[i] < min_wirelength:
                    min_wirelength = wirelength_list[i]
                    min_wirelength_id = pareto_id_list[i]
        cluster_pareto_id_list.append(min_wirelength_id)

    for id in cluster_pareto_id_list:
        if id not in results_pareto_id_list:
            results_pareto_id_list.append(id)

    ### print the pareto point director
    for id in results_pareto_id_list:
        print("\n")
        print(df.iloc[id])

    # Store the Pareto optimal points in a new DataFrame
    pareto_df = df.iloc[pareto_id_list]
    # Save the DataFrame to a CSV file
    pareto_df.to_csv(file_name +'.pareto_optimal_points.csv', index=False)

    candidate_trials_dir = []
    for id in results_pareto_id_list:
        candidate_trials_dir.append(df.iloc[id]['trial_id'])

    print("\n")
    print("The candidate trials are: ")
    for dir in candidate_trials_dir:
        print(dir)
        print("\n")

    # save the candidate trials
    candidate_df = df.iloc[results_pareto_id_list]
    candidate_df.to_csv(file_name +'.candidate_trials.csv', index=False)
    
    return candidate_trials_dir


if __name__ == "__main__":
    file_name = "results_20240816_180620.csv"
    top_n = 3
    num_clusters = 3
    random_seed = 0
    weight_params = [1.0, 1.0, 1.0]
    getCandidateSolutions(file_name, top_n, num_clusters, random_seed, weight_params)
