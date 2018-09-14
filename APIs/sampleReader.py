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
# Sample python code for getting data from the Data Lantern server.

import argparse
import json
import lanternapi
import datetime
import time

# Example:
# ./sampleReader.py  -n 10.0.0.10 -u username -p password -d 1


def main():

    parser = argparse.ArgumentParser(description='Get data from DL server for a device.')
    parser.add_argument('-n','--hostname', help='Hostname|IP of data lantern server',
                    required=True)
    parser.add_argument('-d','--deviceId', help='Device ID', required=True)
    parser.add_argument('-u', '--username',
                        help='email or login id for DL server login',
                        required=True)
    parser.add_argument('-p', '--password',
                        help='password for DL server login',
                        required=True)
    args = parser.parse_args()

    # create initial control data and store in variable
    control = { 'standard' : { } }

    # set up lanternapi object
    la = lanternapi.lanternapi()
    la.setHostname(args.hostname)

    # login to DL server
    code, body = la.login(args.username, args.password)
    print('login status: %d' % code)
    print('login response body: %r' % body)
    print('\n')

    # get list of devices
    code,body = la.getMyDevices(0)
    print('getMyDevices status: %d' % code)
    print('getMyDevices response body: %r' % body)
    print('\n')

    # get list of users that access my device
    code,body = la.getUserAccessList(1)
    print('getUserAccessList status: %d' % code)
    print('getUserAccessList response body: %r' % body)
    print('\n')

    # get list of devices I don't own that I can access
    code,body = la.getOtherDevices(0)
    print('getOtherDevices status: %d' % code)
    print('getOtherDevices response body: %r' % body)
    print('\n')

    # get device data
    code, body = la.getData(1, 0, 25)
    print('getData status: %d' % code)
    print('getData response body: %r' % body)
    print('\n')

    # logout
    code, body = la.logout()
    print('logout status: %d' % code)
    print('logout response body: %r' % body)
    print('\n')

if __name__ == "__main__":
	main()
