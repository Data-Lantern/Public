#!/usr/bin/python
#
# Data Lantern Inc confidential
# ______________________________
#
#  [2014] - [2018] Data Lantern Inc
#  All Rights Reserved.
#
# NOTICE:  All information contained herein is, and remains
# the property of Data Lantern Inc and its suppliers, if any.
# The intellectual and technical concepts contained herein
# are proprietary to Data Lantern Inc and its suppliers and
# may be covered by U.S. and Foreign Patents, patents in
# process, and are protected by trade secret or copyright
# law. Dissemination of this inforamtion or reproduction of
# this material is strictly forbidden unless prior written
# permission is obtained from Data Lantern Inc.
#
# Sample python code for sending data to the Data Lantern server.
#

import argparse
import json
import lanternapi
import datetime
import time

# to suppress IPv6 warning "WARNING: No route found for IPv6 destination :: (no default route?)"
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

# Example:
# ./sampleWriter.py  -n 10.0.0.10 -t someTokenIdReceivedFromDataLanternServer -d 1

def processPayload(payload):
    """Process devices's data and create data format required by DL server"""
    standard = {}
    values = []
    for line in payload.splitlines():
        if "HTTP/1.0 200 OK" in line:
            pass
        elif "Content-Type" in line:
            pass
        elif "Ver:" in line:
            k,v = line.split()
            standard['Ver'] = v
        elif "Brd:" in line:
            k,v = line.split()
            standard['Brd'] = v
        elif "IP:" in line:
            k,v = line.split()
            standard['IP'] = v
        elif "Port:" in line:
            k,v = line.split()
            standard['Port'] = v
        elif "MAC:" in line:
            k,v = line.split()
            standard['MAC'] = v
        elif "Date:" in line:
            k,v = line.split()
            standard['Date'] = v
        elif "Time:" in line:
            k,v = line.split()
            standard['Time'] = v
        elif "Type:" in line:
             k,v = line.split()
             standard['Type'] = v
        elif "Constants" in line:
            k,v = line.split()
            vArray = v.split(',')
            standard['Constants'] = vArray
        elif "Settings" in line:
            k,v = line.split()
            vArray = v.split(',')
            standard['Settings'] = vArray
        elif "Temperatures" in line:
            v = line.split(',')
            standard['Units'] = v
        elif line.strip():
            values.append(line.split(','))
        else:
            pass

    standard['Values'] = values
    return standard

def main():

    parser = argparse.ArgumentParser(description='Read pcap with heliodyne data and sent to DL server.')
    parser.add_argument('-n','--hostname', help='Hostname|IP of data lantern server',
                    required=True)
    parser.add_argument('-d','--deviceId', help='Device ID', required=True)
    parser.add_argument('-t', '--token',
                        help='API token',
                        required=True)
    parser.add_argument('-f', '--filename',
                        help='pcap file',
                        required=True)
    args = parser.parse_args()

    # create initial control data and store in variable
    control = { 'standard' : { } }

    # set up lanternapi object
    la = lanternapi.lanternapi()
    la.setHostname(args.hostname)
    la.setApiToken(args.token)

    packets = rdpcap(args.filename)
    sessions = packets.sessions()
    dataArray = []

    for session in sessions:
        heliodynePayload = ''
        for packet in sessions[session]:
            if (packet.haslayer(TCP) and
                packet[TCP].dport == 9999 and
                packet.haslayer(Raw)):
                heliodynePayload += str(packet[Raw].load)

        if (heliodynePayload != ''):
            standard = processPayload(heliodynePayload)
            data = { 'standard' : standard }
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dataObj = { 'data' : data, 'control' : control, 'creation_time' : now }
            dataArray.append(dataObj)

    # package up data using heliodyne data and stored control data and creation_time
    jsonData = json.dumps(dataArray, separators=(',',':'))

    # send to DL server
    code, body = la.sendData(args.deviceId, jsonData)
    print('sendData status: %d' % code)
    print('sendData response body: %r' % body)
    print('\n')

    # if response is OK, store returned control data
    if (code == 200):
        respObj = json.loads(body)
        if (respObj['status'] == 'success'):
            dataPart = respObj['data']
            if (dataPart['control'] != None):
                control = json.loads(dataPart['control'])

    # consider logging response

if __name__ == "__main__":
	main()

#
# Example of TCP payload data going from Heliodyne to the cloud server,
# each line ends in CR/LF
#
#HTTP/1.0 200 OK
#Content-Type: text/html
#
#Ver: 420
#Brd: RCM4000
#IP: 10.0.0.52
#Port: 9999
#MAC: 00:90:c2:d0:77:c3
#Date: 05/02/2017
#Time: 18:22:00
#Type: energy4
#
#Constants:  0.33570,0.01639,5.54075,0.31931,36.56813
#Settings:  0,18,5,50,0,82,130,1,160,1,120,160,3,0,1,0,0.000,0,0,1,0,2,40,17,8,120
#Temperatures -degF,Flow-GPM,Pressure-PSIg,Energy-BTU/min,Electricty-kW,Radiation-W/m2,All_DATA_10MIN_AVGs
#20170205_182000,58.32,66.62,-999.90,73.09,57.06,67.55,-999.90,0.00,0.00,0.00,0.00,0.00,0.00
#20170205_181000,58.85,66.68,-999.90,73.12,57.07,67.54,-999.90,0.00,0.00,0.00,0.00,0.00,0.00
#20170205_180000,59.45,66.71,-999.90,73.14,57.07,67.54,-999.90,0.00,0.00,0.00,0.00,0.00,0.00
#20170205_175000,60.23,66.77,-999.90,73.19,57.08,67.54,-999.90,0.00,0.00,0.00,0.00,0.00,0.00
#20170205_174000,61.30,66.82,-999.90,73.22,57.16,67.53,-999.90,0.00,0.00,0.00,0.00,0.00,0.00
#20170205_173000,62.44,66.88,-999.90,73.30,57.17,67.54,-999.90,0.00,0.00,0.00,0.00,0.00,0.00
#20170205_172000,63.72,66.97,-999.90,73.37,57.17,67.53,-999.90,0.00,0.00,0.00,0.00,0.00,0.00
