from endpointer import cluster as ep_cluster

def get_cluster_data(telemetry_data):

    cluster_data = telemetry_data[ep_cluster.CLUSTER_DATA]

    return cluster_data

def get_cluster_datetime(telemetry_data):

    cluster_data = get_cluster_data(telemetry_data)

    date_time = cluster_data[ep_cluster.CLUSTER_DATETIME]

    return date_time

