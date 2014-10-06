#
#      Licensed to the Apache Software Foundation (ASF) under one
#      or more contributor license agreements.  See the NOTICE file
#      distributed with this work for additional information
#      regarding copyright ownership.  The ASF licenses this file
#      to you under the Apache License, Version 2.0 (the
#      "License"); you may not use this file except in compliance
#      with the License.  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#      Unless required by applicable law or agreed to in writing,
#      software distributed under the License is distributed on an
#      "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#      KIND, either express or implied.  See the License for the
#      specific language governing permissions and limitations
#      under the License.
#
"""
Module that takes care of network communications for cmislib. It does
not know anything about CMIS or do anything special with regard to the
response it receives.
"""

"""
temporary for development
"""
import human_curl as hurl
import pycurl
"""
end of temporary
"""

from urllib import urlencode
import logging
import httplib2
import importlib
import re
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

class RESTService(object):

    """
    Generic service for interacting with an HTTP end point.
    """

    pass


class DefaultRESTService(RESTService):

    """
    Generic service for interacting with an HTTP end point. Sets headers
    such as the USER_AGENT and builds the basic auth handler.
    """

    def __init__(self, **kwargs):
        self.user_agent = 'cmislib/%s +http://chemistry.apache.org/'
        self.logger = logging.getLogger('cmislib.net.DefaultRESTService')

    def get(self,
            url,
            username=None,
            password=None,
            **kwargs):

        """ Makes a get request to the URL specified."""

        headers = {}
        if kwargs:
            if 'headers' in kwargs:
                headers = kwargs['headers']
                del kwargs['headers']
                self.logger.debug('Headers passed in:' + headers)
            if url.find('?') >= 0:
                url = url + '&' + urlencode(kwargs)
            else:
                url = url + '?' + urlencode(kwargs)

        self.logger.debug('About to do a GET on:' + url)

        h = httplib2.Http()
        h.add_credentials(username, password)
        headers['User-Agent'] = self.user_agent

        return h.request(url, method='GET', headers=headers)

    def delete(self, url, username=None, password=None, **kwargs):

        """ Makes a delete request to the URL specified. """

        headers = {}
        if kwargs:
            if 'headers' in kwargs:
                headers = kwargs['headers']
                del kwargs['headers']
                self.logger.debug('Headers passed in:' + headers)
            if url.find('?') >= 0:
                url = url + '&' + urlencode(kwargs)
            else:
                url = url + '?' + urlencode(kwargs)

        self.logger.debug('About to do a DELETE on:' + url)

        h = httplib2.Http()
        h.add_credentials(username, password)
        headers['User-Agent'] = self.user_agent

        return h.request(url, method='DELETE', headers=headers)

    def put(self,
            url,
            payload,
            contentType,
            username=None,
            password=None,
            **kwargs):

        """
        Makes a PUT request to the URL specified and includes the payload
        that gets passed in. The content type header gets set to the
        specified content type.
        """

        headers = {}
        if kwargs:
            if 'headers' in kwargs:
                headers = kwargs['headers']
                del kwargs['headers']
                self.logger.debug('Headers passed in:' + headers)
            if url.find('?') >= 0:
                url = url + '&' + urlencode(kwargs)
            else:
                url = url + '?' + urlencode(kwargs)

        self.logger.debug('About to do a PUT on:' + url)

        h = httplib2.Http()
        h.add_credentials(username, password)
        headers['User-Agent'] = self.user_agent
        if contentType is not None:
            headers['Content-Type'] = contentType
        return h.request(url, body=payload, method='PUT', headers=headers)

    def post(self,
             url,
             payload,
             contentType,
             username=None,
             password=None,
             **kwargs):

        """
        Makes a POST request to the URL specified and posts the payload
        that gets passed in. The content type header gets set to the
        specified content type.
        """

        headers = {}
        if kwargs:
            if 'headers' in kwargs:
                headers = kwargs['headers']
                del kwargs['headers']
                self.logger.debug('Headers passed in:' + headers)
            if url.find('?') >= 0:
                url = url + '&' + urlencode(kwargs)
            else:
                url = url + '?' + urlencode(kwargs)

        self.logger.debug('About to do a POST on:' + url)

        h = httplib2.Http()
        h.add_credentials(username, password)
        headers['User-Agent'] = self.user_agent
        if contentType is not None:
            headers['Content-Type'] = contentType
        return h.request(url, body=payload, method='POST', headers=headers)


class CURLRESTService(RESTService):

    """
    Generic human_curlL-based service for interacting with an HTTP end
    point. Sets headers such as the USER_AGENT and builds the
    basic auth handler.
    """

    def __init__(self, **kwargs):
        import human_curl as hurl
        import pycurl
        self.user_agent = 'cmislib/%s +http://chemistry.apache.org/'
        self.curlOpts = kwargs
        self.logger = logging.getLogger('cmislib.net.CURLRESTService')


    def get(self,
            url,
            username=None,
            password=None,
            **kwargs):

        """ Makes a get request to the URL specified."""

        # merge the curl options with the ones that got passed in
        if len(self.curlOpts) > 0:
            kwargs.update(self.curlOpts)

        headers = {}
        options = {}
        if kwargs:
            if 'headers' in kwargs:
                headers = kwargs['headers']
                del kwargs['headers']
                self.logger.debug('Headers passed in:' + headers)
            if 'curlOpts' in kwargs:
                options = kwargs['curlOpts']
                del kwargs['curlOpts']
                self.logger.debug('CurlOpts passed in:' + str(options))
            if url.find('?') >= 0:
                url = url + '&' + urlencode(kwargs)
            else:
                url = url + '?' + urlencode(kwargs)

        self.logger.debug('About to do a GET on:' + url)

        auth = None
        if username is not None:
            auth = (username, password)

        hurlResponse = hurl.get(url, allow_redirects=True, auth=auth, options=options, user_agent=self.user_agent)
        content = hurlResponse.content
        response = self._buildHttplib2Response(hurlResponse)
        return response, content

    def delete(self, url, username=None, password=None, **kwargs):

        """ Makes a delete request to the URL specified. """

        # merge the curl options with the ones that got passed in
        if len(self.curlOpts) > 0:
            kwargs.update(self.curlOpts)

        headers = {}
        if kwargs:
            if 'headers' in kwargs:
                headers = kwargs['headers']
                del kwargs['headers']
                self.logger.debug('Headers passed in:' + headers)
            if url.find('?') >= 0:
                url = url + '&' + urlencode(kwargs)
            else:
                url = url + '?' + urlencode(kwargs)

        self.logger.debug('About to do a DELETE on:' + url)

        h = httplib2.Http()
        h.add_credentials(username, password)
        headers['User-Agent'] = self.user_agent

        return h.request(url, method='DELETE', headers=headers)

    def put(self,
            url,
            payload,
            contentType,
            username=None,
            password=None,
            **kwargs):

        """
        Makes a PUT request to the URL specified and includes the payload
        that gets passed in. The content type header gets set to the
        specified content type.
        """

        # merge the curl options with the ones that got passed in
        if len(self.curlOpts) > 0:
            kwargs.update(self.curlOpts)

        headers = {}
        if kwargs:
            if 'headers' in kwargs:
                headers = kwargs['headers']
                del kwargs['headers']
                self.logger.debug('Headers passed in:' + headers)
            if url.find('?') >= 0:
                url = url + '&' + urlencode(kwargs)
            else:
                url = url + '?' + urlencode(kwargs)

        self.logger.debug('About to do a PUT on:' + url)

        h = httplib2.Http()
        h.add_credentials(username, password)
        headers['User-Agent'] = self.user_agent
        if contentType is not None:
            headers['Content-Type'] = contentType
        return h.request(url, body=payload, method='PUT', headers=headers)

    def post(self,
             url,
             payload,
             contentType,
             username=None,
             password=None,
             **kwargs):

        """
        Makes a POST request to the URL specified and posts the payload
        that gets passed in. The content type header gets set to the
        specified content type.
        """

        # merge the curl options with the ones that got passed in
        if len(self.curlOpts) > 0:
            kwargs.update(self.curlOpts)

        headers = {}
        if kwargs:
            if 'headers' in kwargs:
                headers = kwargs['headers']
                del kwargs['headers']
                self.logger.debug('Headers passed in:' + headers)
            if url.find('?') >= 0:
                url = url + '&' + urlencode(kwargs)
            else:
                url = url + '?' + urlencode(kwargs)

        self.logger.debug('About to do a POST on:' + url)

        c = pycurl.Curl()
        if username is not None:
            c.setopt(c.USERNAME, username)
            c.setopt(c.PASSWORD, password)
        c.setopt(c.USERAGENT, self.user_agent)
        if contentType is not None:
            headers['Content-Type'] = contentType
        c.setopt(c.HTTPHEADER, headers)
        responseHandler = _ResponseHandler()
        c.setopt(c.WRITEFUNCTION, responseHandler.contentHandler)
        c.setopt(c.HEADERFUNCTION, responseHandler.headerHandler)

        c.perform()

        content = responseHandler.getContent()

        # TODO build httplib2.Response including populating the 'previous' list from hurlResponse w/history
        response = httplib2.Response(responseHandler.getHeaders())
        response.status = c.getinfo(pycurl.HTTP_CODE)
        response.previous

        c.close()

        return response, content

    def _buildHttplib2Response(self, hurlResponse):
        response = httplib2.Response(hurlResponse.headers)
        response.update({'status': str(hurlResponse.status_code)})
        response.status = hurlResponse.status_code
        # TODO recursively populate the 'previous' list from hurlResponse history
        response.previous = hurlResponse.history
        return response


class _ResponseHandler:

    def __init__(self):
        self._content = BytesIO()
        self._headers = {}

    def getContent(self):
        return self._content.getvalue()

    def contentHandler(self):
        self._content.write()

    def getHeaders(self):
        return self._headers

    def headerHandler(self, headerLine):
        # HTTP standard specifies that headers are encoded in iso-8859-1.
        # On Python 2, decoding step can be skipped.
        # On Python 3, decoding step is required.
        header_line = headerLine.decode('iso-8859-1')

        # Header lines include the first status line (HTTP/1.x ...).
        # We are going to ignore all lines that don't have a colon in them.
        # This will botch headers that are split on multiple lines...
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
        self._headers[name] = value