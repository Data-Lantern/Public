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
#

import argparse
import json
import lanternapi
import datetime
import time

# Example:
# ./sampleRegisterUser.py  -n 10.0.0.10 -u username -p password -d 1


def main():

    parser = argparse.ArgumentParser(description='Register a new user.')
    parser.add_argument('-n','--hostname', help='Hostname|IP of data lantern server',
                    required=True)
    parser.add_argument('-f','--firstname', help='First Name', required=True)
    parser.add_argument('-l','--lastname', help='Last Name', required=True)
    parser.add_argument('-u', '--username',
                        help='Username',
                        required=True)
    parser.add_argument('-e', '--email', help='Email for the account', required=True)
    parser.add_argument('-p', '--password',
                        help='password for the account',
                        required=True)
    parser.add_argument('-c','--inviteCode', help='Invitation Code', required=True)
    args = parser.parse_args()

    # create initial control data and store in variable
    control = { 'standard' : { } }

    # set up lanternapi object
    la = lanternapi.lanternapi()
    la.setHostname(args.hostname)

    # login to DL server
    code, body = la.registerUser(args.inviteCode, args.firstname, args.lastname,
                                args.username, args.email, args.password)
    print('register status: %d' % code)
    print('register response body: %r' % body)
    print('\n')

if __name__ == "__main__":
	main()
