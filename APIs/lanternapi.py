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
# module that uses pycurl to access the Data Lantern server

import pycurl
import re
from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

class lanternapi(object):
    """Access the Data Lantern server API with pycurl."""

    def __init__(self):
        self.urlBase = "/api/v1"
        self.hostName = "lantern.com"
        self.headers = {}

        self.curlSetup()


    def setHostname(self, name):
        """Set the Data Lantern server hostname."""
        self.hostName = name


    def setApiToken(self, token):
        """Set the device owner's API token."""
        self.apiToken = token


    def headerFunction(self, header_line):
        """Process and store request headers."""
        # HTTP standard specifies that headers are encoded in iso-8859-1.
        header_line = header_line.decode('iso-8859-1')

        # Header lines include the first status line (HTTP/1.x ...).
        # We are going to ignore all lines that don't have a colon in them.
        # This will screw up headers that are split on multiple lines...
        if ':' not in header_line:
            return

        # Break the header line into header name and value.
        name, value = header_line.split(':', 1)

        # Remove whitespace that may be present.
        # Header lines include the trailing newline, and there may be whitespace
        # around the colon.
        name = name.strip()
        value = value.strip()

        # Header names are case insensitive.
        # Lowercase name here.
        name = name.lower()

        # Now we can actually record the header name and value.
        self.headers[name] = value


    def responseEncoding(self):
        """Figure out and return response encoding."""
        encoding = None
        if 'content-type' in self.headers:
            content_type = self.headers['content-type'].lower()
            match = re.search('charset=(\S+)', content_type)
            if match:
                encoding = match.group(1)
                print('Decoding using %s' % encoding)
        if encoding is None:
            # Default encoding for HTML is iso-8859-1.
            # Other content types may have different default encoding,
            # or in case of binary data, may have no encoding at all.
            encoding = 'iso-8859-1'

        return encoding


    def curlSetup(self):
        """Set up object before first curl."""
        self.c = pycurl.Curl()

        # just keep cookies in memory, these are retained after a call to reset()
        self.c.setopt(pycurl.COOKIEFILE, "")


    def curlReset(self):
        """Reset object before next curl."""
        self.c.reset()

        self.buffer = BytesIO()
        self.c.setopt(self.c.WRITEDATA, self.buffer)
        self.c.setopt(self.c.HEADERFUNCTION, self.headerFunction)

        headers = [ "Accept: application/json" ]
        self.c.setopt(pycurl.HTTPHEADER, headers)

# TODO We don't have a valid certificate for SSL yet, can delete these when ready
        self.c.setopt(pycurl.SSL_VERIFYPEER, 0)
        self.c.setopt(pycurl.SSL_VERIFYHOST, 0)


    def registerUser(self, inviteCode, firstname, lastname, username, email, password):
        """Register a new user."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/register'
        self.c.setopt(pycurl.URL, url)

        postData = {'code': inviteCode,
                    'firstname': firstname,
                    'lastname': lastname,
                    'username': username,
                    'email': email,
                    'password': password,
                    'password_confirmation': password}
        # Form data must be provided already urlencoded.
        postFields = urlencode(postData)
        # Sets request method to POST,
        # Content-Type header to application/x-www-form-urlencoded
        # and data to send in request body.
        self.c.setopt(pycurl.POSTFIELDS, postFields)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def login(self, email, password):
        """Send login API request and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/login'
        self.c.setopt(pycurl.URL, url)

        postData = {'email': email,
                    'password': password}
        # Form data must be provided already urlencoded.
        postFields = urlencode(postData)
        # Sets request method to POST,
        # Content-Type header to application/x-www-form-urlencoded
        # and data to send in request body.
        self.c.setopt(pycurl.POSTFIELDS, postFields)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]


    def logout(self):
        """Send logout API request and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/logout'
        self.c.setopt(pycurl.URL, url)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def getApiToken(self):
        """Send get token request and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/gettoken'
        self.c.setopt(pycurl.URL, url)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def getMyDevices(self, page):
        """Send get access API request and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/devices'
        if page > 0:
            url = self.set_query_parameter(url, 'page', page)
        self.c.setopt(pycurl.URL, url)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def getMyDevice(self, deviceId):
        """Send get device API request and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/device/' + str(deviceId)
        self.c.setopt(pycurl.URL, url)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def getUserAccessList(self, deviceId):
        """Send get access request and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/access/' + str(deviceId)
        self.c.setopt(pycurl.URL, url)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def getOtherDevices(self, page):
        """Send get access API request and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/access'
        if page > 0:
            url = self.set_query_parameter(url, 'page', page)
        self.c.setopt(pycurl.URL, url)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def addUserAccessToDeviceData(self, deviceId, email):
        """Send request to give a user access to my device's data and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/access/' + str(deviceId) + '/data'
        self.c.setopt(pycurl.URL, url)

        postData = {'datauseremail': email}
        # Form data must be provided already urlencoded.
        postFields = urlencode(postData)
        # Sets request method to POST,
        # Content-Type header to application/x-www-form-urlencoded
        # and data to send in request body.
        self.c.setopt(pycurl.POSTFIELDS, postFields)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def addUserAccessToDeviceControl(self, deviceId, email):
        """Send request to give a user access to my device's control and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/access/' + str(deviceId) + '/control'
        self.c.setopt(pycurl.URL, url)

        postData = {'controluseremail': email}
        # Form data must be provided already urlencoded.
        postFields = urlencode(postData)
        # Sets request method to POST,
        # Content-Type header to application/x-www-form-urlencoded
        # and data to send in request body.
        self.c.setopt(pycurl.POSTFIELDS, postFields)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def removeUserAccessToDeviceData(self, deviceId, email):
        """Send request to remove a user's access to my device's data and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/access/' + str(deviceId) + '/data'
        self.c.setopt(pycurl.URL, url)
        self.c.setopt(pycurl.CUSTOMREQUEST, 'delete')

        postData = {'datauseremail': email}
        # Form data must be provided already urlencoded.
        postFields = urlencode(postData)
        # Sets request method to POST,
        # Content-Type header to application/x-www-form-urlencoded
        # and data to send in request body.
        self.c.setopt(pycurl.POSTFIELDS, postFields)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def removeUserAccessToDeviceControl(self, deviceId, email):
        """Send request to remove a user's access to my device's control and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/access/' + str(deviceId) + '/control'
        self.c.setopt(pycurl.URL, url)
        self.c.setopt(pycurl.CUSTOMREQUEST, 'delete')

        postData = {'controluseremail': email}
        # Form data must be provided already urlencoded.
        postFields = urlencode(postData)
        # Sets request method to POST,
        # Content-Type header to application/x-www-form-urlencoded
        # and data to send in request body.
        self.c.setopt(pycurl.POSTFIELDS, postFields)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def sendData(self, deviceId, data):
        """Send data API request and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/data'
        self.c.setopt(pycurl.URL, url)

        postData = {'device_id': deviceId,
                    'data': data,
                    'api_token': self.apiToken}
        # Form data must be provided already urlencoded.
        postFields = urlencode(postData)
        # Sets request method to POST,
        # Content-Type header to application/x-www-form-urlencoded
        # and data to send in request body.
        self.c.setopt(pycurl.POSTFIELDS, postFields)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]


    def getData(self, deviceId, page, limit):
        """Send control data API request and return http response code and body."""
        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/data/' + str(deviceId)
        if page > 0:
            url = self.set_query_parameter(url, 'page', page)
        if limit > 0:
            url = self.set_query_parameter(url, 'limit', limit)
        self.c.setopt(pycurl.URL, url)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def getLatestControl(self, deviceId):
        """Send latest control API request and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/control/' + str(deviceId) + '/latest'
        self.c.setopt(pycurl.URL, url)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def sendControl(self, deviceId, controlData):
        """Send control data request and return http response code and body."""

        self.curlReset()

        url = "https://" + self.hostName + self.urlBase + '/control/' + str(deviceId)
        self.c.setopt(pycurl.URL, url)

        postData = {'device_id': deviceId,
                    'control': controlData}
        # Form data must be provided already urlencoded.
        postFields = urlencode(postData)
        # Sets request method to POST,
        # Content-Type header to application/x-www-form-urlencoded
        # and data to send in request body.
        self.c.setopt(pycurl.POSTFIELDS, postFields)

        self.c.perform()

        code = self.c.getinfo(pycurl.RESPONSE_CODE)
        encoding = self.responseEncoding()
        body = self.buffer.getvalue()

        return [code, body.decode(encoding)]

    def set_query_parameter(self, url, param_name, param_value):
        """Given a URL, set or replace a query parameter and return the
        modified URL.

        >>> set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
        'http://example.com?foo=stuff&biz=baz'

        """
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query_params = parse_qs(query_string)

        query_params[param_name] = [param_value]
        new_query_string = urlencode(query_params, doseq=True)

        return urlunsplit((scheme, netloc, path, new_query_string, fragment))
