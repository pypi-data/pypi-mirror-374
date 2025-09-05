import os

CLUSTER_DATA = 'cluster-data'
CLUSTER_DATETIME = 'cluster-datetime'
NODE_DATA = 'node-data'
NODE_IP = 'node-ip'

def set_cluster_data(telemetry_data, cluster_data):

    telemetry_data[CLUSTER_DATA] = cluster_data

def set_node_data(telemetry_data, node_data):

    telemetry_data[NODE_DATA] = node_data

def get_cluster_data(telemetry_data):

    return telemetry_data[CLUSTER_DATA]

def get_node_data(telemetry_data):

    return telemetry_data[NODE_DATA]

def get_cluster_datetime(telemetry_data):

    cluster_data = get_cluster_data(telemetry_data)
    
    return cluster_data[CLUSTER_DATETIME]

def get_node_ip(telemetry_data):

    cluster_data = get_cluster_data(telemetry_data)
    
    return cluster_data[NODE_IP]
