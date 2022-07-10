#!/usr/bin/env python3
import boto3
import psutil
import os
#######################################################################################################################################################################
################################################################ Tested with Python3.6,3.7& 3.8 #######################################################################
###### You can check below psutil library from python shell
####>>> import psutil
####>>> from pprint import pprint as pp
####>>> p = psutil.Process()
####>>> p.cpu_percent(interval=5)
####>>> pp([(p.pid, p.info) for p in psutil.process_iter(['name', 'status']) if p.info['status'] == psutil.STATUS_RUNNING])
####[(650, {'name': 'python3', 'status': 'running'})]
####>>> pp([(p.pid, p.info['name'], sum(p.info['cpu_times'])) for p in sorted(psutil.process_iter(['name', 'cpu_times']), key=lambda p: sum(p.info['cpu_times'][:2]))][-3:])
####[(1, 'init', 0.31), (650, 'python3', 0.75), (11, 'bash', 52.43000000000001)]
####>>>
#######################################################################################################################################################################

_METADATAURL = 'http://169.254.169.254/latest/meta-data'

cw = boto3.client('cloudwatch')
currMetrics = []
def appendMetrics(CurrentMetrics, Dimensions, Name, Unit, Value):
    metric = { 'MetricName' : Name
    , 'Dimensions' : Dimensions
    , 'Unit' : Unit
    , 'Value' : Value
    }
    CurrentMetrics.append(metric)

def memUsedByApache():
    return round(sum([p.info['memory_info'].rss for p in psutil.process_iter(attrs=['name','memory_info']) if 'httpd' in p.info['name']]) / (1024*1024), 1)

def memUsedByMysql():
    return round(sum([p.info['memory_info'].rss for p in psutil.process_iter(attrs=['name','memory_info']) if 'mysqld' in p.info['name']]) / (1024*1024), 1)

def usedMemoryPercentage():
    return psutil.virtual_memory().percent

def usedDiskSpace():
    return psutil.disk_usage('/').percent

if __name__ == '__main__':
    instance_id = requests.get( _METADATAURL + '/instance-id').text
    instance_type = requests.get( _METADATAURL + '/instance-type').text
    dimensions = [{'Name' : 'InstanceId', 'Value': instance_id}, {'Name' : 'InstanceType', 'Value': instance_type}]
    appendMetrics(currMetrics, dimensions, Name='ApacheMemory', Value=memUsedByApache(), Unit='Megabytes')
    appendMetrics(currMetrics, dimensions, Name='MysqlMemory', Value=memUsedByMysql(), Unit='Megabytes')
    appendMetrics(currMetrics, dimensions, Name='MemoryInUse', Value=usedMemoryPercentage(), Unit='Percent')
    appendMetrics(currMetrics, dimensions, Name='DiskspaceUsed', Value=usedDiskSpace(), Unit='Percent')
