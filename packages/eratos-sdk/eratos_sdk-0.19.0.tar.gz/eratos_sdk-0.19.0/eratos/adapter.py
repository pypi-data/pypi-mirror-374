#
# Copyright (C) Eratos Group Pty Ltd and its affiliates.
#
# This file was created as part of:
#
#   Eratos Python SDK
#
# It is proprietary software, you may not:
#
#   a) redistribute it and/or modify without permission from Eratos Group Pty Ltd.
#   b) reuse the code in part or in full without permission from Eratos Group Pty Ltd.
#
# If permission has been granted for reuse and/or redistribution it is subject
# to the following conditions:
#
#   a) The above copyright notice and this permission notice shall be included
#      in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import os
import logging
import time
import base64
import urllib
import re
import time

import requests
from requests.adapters import HTTPAdapter
from requests_toolbelt.adapters.socket_options import TCPKeepAliveAdapter
from requests.packages.urllib3.util.retry import Retry

from json import dumps as jdump, loads as jload

from .ern import Ern
from .creds import BaseCreds, TrackerExchange
from .resource import Resource
from .search import SearchAdapter
from .policy import Policy
from .data import Data
from .dataversion import DataVersion
from .errors import CommError
from .util import decode_request_content_response
from .oapi.creds import AccessTokenCreds as OAPIAccessTokenCreds
from .oapi.adapter import Adapter as OAPIAdapter

_logger = logging.getLogger(__name__)
_node_name_validator = re.compile('^[a-zA-Z0-9-]+$')

def decode_jwt_claims(token):
    """
    A small decoder utility function.

    Parameters
    ----------
    token : str
        A string defining the token for authentication.
    """
    b64claims = token.split('.')[1]
    b64claims += '=' * (4 - (len(b64claims) % 4))
    return jload(base64.urlsafe_b64decode(b64claims))

class Adapter:
    """
    A class used to interact with Eratos' adapter functionality.

    Attributes
    ----------
    creds : BaseCreds
        Required Eratos Token key ID and secret, wrapped in an BaseCreds object. (Default value is None)
    ignore_certs : bool
        Optional argument to ignore or accept certificates. (Default value is False)
    """
    def __init__(self, creds: BaseCreds=None, ignore_certs=False):
        self._ignore_certs = ignore_certs
        self._httpAdp = HTTPAdapter(max_retries=Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        ))
        self._httpSession = requests.Session()
        self._tcp = TCPKeepAliveAdapter(idle = 120, interval = 10)
        self._httpSession.mount("https://", self._httpAdp)
        self._httpSession.mount("http://", self._httpAdp)
        self._httpSession.mount("https://", self._tcp)
        self._httpSession.trust_env = False
        self._tracker_exchange = TrackerExchange(self._httpSession, creds, self._ignore_certs)
        self._dn_token = None
        self._disable_oapi = False

    def master_pn(self):
        """
        Retrieves the master primary node.

        master_pn() fetches the Eratos Resource Name (ERN) of the master primary node for the given adapter.
        
        Returns
        -------
        Ern
            The unique Eratos Resource Name (ERN) of the master primary node.
        """
        return self._tracker_exchange.master_pn()

    def request(self, target_ern: Ern, method: str, path: str, headers={}, retRequest=False, retOnlyRequest=False, **kwargs):
        """
        Send a request to a specific ERN.

        request() sends a request to a specific Eratos Resource Name (ERN) to perform a given action.

        Parameters
        ----------
        target_ern : Ern
            A string defining the target Eratos Resource Name (ERN) to send the request to.
        method : str
            A string to define the method of the request. (ex. 'GET')
        path : str
            A string to define the path of the request.
        headers : dict
            Includes any headers to add to the request. (Default value is an empty dictionary)
        retRequest : bool
            True or False to return the request as well as the response. (Default is False)
        kwargs : args
            Optional keyword arguments to add to the request object.
            Arguments can include any of the following:
            | params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=None, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None

        Raises
        ------
        ValueError
            If the response cannot be decoded.
        CommError
            If the request fails.

        Returns
        -------
        dict | str
            The decoded response content.
        """
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        if 'Accept' not in headers:
            headers['Accept'] = 'application/json'
        url = path if path[:5] == 'http:' or path[:6] == 'https:' in path else self._tracker_exchange.fetch_target_host(target_ern)+path
        auth = self._tracker_exchange.get_auth_token(target_ern)
        req = self._httpSession.request(method, url, headers=headers, auth=auth, verify=not self._ignore_certs, **kwargs)
        _logger.debug('request to %s: %s %s (%d)' % (target_ern, method, url, req.status_code))
        if req.status_code >= 200 and req.status_code < 400:
            try:
                if retOnlyRequest:
                    return req
                elif retRequest:
                    return decode_request_content_response(req), req
                else:
                    return decode_request_content_response(req)
            except ValueError:
                return None
        else:
            if 'application/json' in req.headers.get('Content-Type'):
                raise CommError(req.status_code, req.json())
            else:
                raise CommError(req.status_code, { 'code': 'unknown', 'message': req.text })
 
    def dnrequest(self, dnurl: str, method: str, path: str, headers={}, **kwargs):
        """
        Send a datanode request.

        dnrequest() sends a request to the adapter's datanode to perform a given action.

        Parameters
        ----------
        dnurl : str
            The url for the datanode. It is set to a default if an empty string is provided. 
        method : str
            A string to define the type of the request. (ex. 'GET')
        path : str
            A string to define the path of the request.
        headers : dict
            Includes any headers to add to the request. (Default value is an empty dictionary)
        kwargs : args
            Optional keyword arguments to add to the request object.
            Arguments can include any of the following:
            | params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=None, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None

        Raises
        ------
        ValueError
            If the response cannot be decoded.
        CommError
            If the request fails.

        Returns
        -------
        dict | str
            The decoded response content.
        """
        if dnurl == '':
            dnurl = 'https://xwjtd2dq7lk6ywxifyav463c.nds.e-gn.io'
        self._refresh_dn_token()
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        if 'Accept' not in headers:
            headers['Accept'] = 'application/json'
        headers['X-API-Token'] = self._dn_token['token']
        url = path if 'http:' in path or 'https:' in path else dnurl+path
        req = self._httpSession.request(method, url, headers=headers, verify=not self._ignore_certs, **kwargs)
        _logger.debug('dn request: %s %s (%d)' % (method, url, req.status_code))
        if req.status_code >= 200 and req.status_code < 400:
            try:
                return decode_request_content_response(req)
            except ValueError:
                return None
        else:
            if 'application/json' in req.headers.get('Content-Type'):
                raise CommError(req.status_code, req.json())
            else:
                raise CommError(req.status_code, { 'code': 'unknown', 'message': req.text })

    def dnbasicrequest(self, method: str, ep: str, headers={}, **kwargs):
        """
        Send a datanode basic HTTP request.

        dnbasicrequest() sends a basic HTTP request to the adapter's datanode to perform a given action.

        Parameters
        ----------
        method : str
            A string to define the type of the request. (ex. 'GET')
        ep : str
            A string to define the parameters of the request.
        headers : dict
            Includes any headers to add to the request. (Default value is an empty dictionary)
        kwargs : args
            Optional keyword arguments to add to the request object.
            Arguments can include any of the following:
            | params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=None, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None

        Raises
        ------
        CommError
            If the request fails.

        Returns
        -------
        Response
            The response content.
        """
        self._refresh_dn_token()
        headers['X-API-Token'] = self._dn_token['token']
        req = self._httpSession.request(method, ep, headers=headers, verify=not self._ignore_certs, **kwargs)
        _logger.debug('dn request: %s %s (%d)' % (method, ep, req.status_code))
        if req.status_code >= 200 and req.status_code < 400:
            return req
        else:
            if 'application/json' in req.headers.get('Content-Type'):
                raise CommError(req.status_code, req.json())
            else:
                raise CommError(req.status_code, { 'code': 'unknown', 'message': req.text })

    def dnstreamrequest(self, method: str, ep: str, headers={}, **kwargs):
        """
        Send a datanode stream request.

        dnstreamrequest() sends a stream request to the adapter's datanode to perform a given action.

        Parameters
        ----------
        method : str
            A string to define the type of the request. (ex. 'GET')
        ep : str
            A string to define the parameters of the request.
        headers : dict
            Includes any headers to add to the request. (Default value is an empty dictionary)
        kwargs : args
            Optional keyword arguments to add to the request object.
            Arguments can include any of the following:
            | params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=None, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None

        Returns
        -------
        stream
            The streamed response content.
        """
        self._refresh_dn_token()
        headers['X-API-Token'] = self._dn_token['token']
        return self._httpSession.request(method, ep, headers=headers, verify=not self._ignore_certs, stream=True, **kwargs)

    def _refresh_dn_token(self):
        now = int(time.time())
        if self._dn_token is None or self._dn_token['exp'] < now:
            tok, req = self.request(Ern(type='tracker'), 'GET', '/auth/dntoken', retRequest=True)
            b64c = tok.split('.', 2)[0]
            jsonc = base64.urlsafe_b64decode(b64c + '=' * (4 - len(b64c) % 4))
            akk, aks = req.headers['x-old-api'].split('.')
            self._dn_token = {
                'token': tok,
                'exp':  jload(jsonc)['exp'] - 30,
                'oapk': akk,
                'oaps': aks
            }

    def disable_oapi(self):
        self._disable_oapi = True

    def _check_dn_token(self):
        if self._disable_oapi:
            return False
        try:
            self.request(Ern(type='tracker'), 'GET', '/auth/dntoken', retRequest=True)
            return True
        except CommError as e:
            if e.code == 1003:
                return False
            else:
                raise e
    
    def create_data_node(self, friendlyId="", description=""):
        if type(friendlyId) is not str:
            raise TypeError('friendlyId should be of type str')
        if type(description) is not str:
            raise TypeError('description should be of type str')
        if _node_name_validator.match(friendlyId) is None:
            raise ValueError('friendlyId should match ^[a-zA-Z0-9-]+$')
        self._refresh_dn_token()
        eadp = OAPIAdapter(OAPIAccessTokenCreds(self._dn_token['oapk'], self._dn_token['oaps']), host="https://e-pn.io")
        return self._fix_node(eadp.create_data_node(friendlyId=friendlyId, description=description))

    def Node(self, *args, **kwargs):
        if len(args) > 0:
            args = list(args)
            args[0] = f'https://e-pn.io/nodes/{args[0].split(":")[-1]}'
            args = tuple(args)
        if 'id' in kwargs and 'ern:' in kwargs['id']:
            kwargs['id'] = f'https://e-pn.io/nodes/{kwargs["id"].split(":")[-1]}'
        self._refresh_dn_token()
        eadp = OAPIAdapter(OAPIAccessTokenCreds(self._dn_token['oapk'], self._dn_token['oaps']), host="https://e-pn.io")
        return eadp.Node(*args, **kwargs)
    
    def _fix_node(self, node):
        node.content['id'] = 'ern::node:'+node.content['id'][-24:]
        node.content['owner'] = 'ern::user:'+node.content['owner'][-24:]
        node.content['policy'] = 'ern:e-pn.io:policy:'+node.content['policy'][-24:]
        return node



    def session(self):
        """
        Retrieves the current HTTP session object.

        Returns
        -------
        Session
            HTTP Session object.
        """
        return self._httpSession

    def search_adapter(self, return_limit=-1, **kwargs):
        """
        Searches the current adapter according to a given query.

        search_adapter() returns a SearchAdapter object according to a set of given parameters. Must run with an initialized adapter with valid credentials.

        Parameters
        ----------
        return_limit : int
            A set return limit on the search. (Default value is -1)
        kwargs : args
            Optional keyword arguments to search against.
            Arguments can include any of:
            | *query* = A string to query (ex. '*')
            | *limit* = An integer depicting the number of resources to limit the return (ex. 20)
            | *start* = An integer depicting the start index (ex. 0)
            | *exclude* = A list of ERNs to exclude.
            | *type* = A list of types to search for.
            | *excludeType* = A list of types to exclude from the search.
            | *owner* = A list of owner ERN's to search against.
            | *collections* = A list of collection ERN's to search against.
            | *facets* = A list of facets to search against.
            | *geom* = A geospatial geometry to search within.

        Returns
        -------
        SearchAdapter
            An Eratos SearchAdapter object to interact with.
        """
        return SearchAdapter(self, return_limit=return_limit, **kwargs)

    def search_resources(self, return_limit=-1, **kwargs):
        """
        Searches resources according to a specific query.

        search_resources() returns a list of matching ERNs (can be empty) according to specific query parameters. Must run with an initialized adapter with valid credentials.

        Parameters
        ----------
        return_limit : int
            A set return limit on the search. (Default value is -1)
        kwargs : args
            Optional keyword arguments to search against.
            Arguments can include any of:
            | *query* = A string to query (ex. '*')
            | *limit* = An integer depicting the number of resources to limit the return (ex. 20)
            | *start* = An integer depicting the start index (ex. 0)
            | *exclude* = A list of ERNs to exclude.
            | *type* = A list of types to search for.
            | *excludeType* = A list of types to exclude from the search.
            | *owner* = A list of owner ERN's to search against.
            | *collections* = A list of collection ERN's to search against.
            | *facets* = A list of facets to search against.
            | *geom* = A geospatial geometry to search within.

        Returns
        -------
        list[str]
            An empty list or a list of unique Eratos Resource Name (ERN) strings.
        """
        adp = self.search_adapter(return_limit=return_limit, **kwargs)
        return list([res for res in adp.search()])

    def Resource(self, *args, **kwargs):
        """
        Interacts with an Eratos Resource.

        Resource() returns a Resource that corresponds to the provided arguments. If the ern argument is set, it will fetch the corresponding Resource, else it will create a resource based on yaml, json or dictionary content.

        Parameters
        ----------
        args : args
            Optional non-keyworded arguments.
        kwargs : args
            Optional keyword arguments.
            Arguments can include any of:
            | *ern* = String or Eratos Resource Name (ERN) of an existing object in Eratos to retrieve. (Default value is None)
            | *yaml* = Yaml object to create an Eratos Resource object. (Default value is None)
            | *json* = JSON object to create an Eratos Resource object. (Default value is None)
            | *content* = Dictionary object to create an Eratos Resource object. (Default value is None)

        Returns
        -------
        Resource
            An Eratos resource object.
        """
        return Resource(self, *args, **kwargs)

    def Policy(self, *args, **kwargs):
        """
        Interacts with a Policy.

        Policy() returns a Policy object with the ability to interact with the policy for a given Resource or Node.

        Parameters
        ----------
        args : args
            Optional non-keyworded arguments.
        kwargs : args
            Optional keyword arguments.
            Arguments can include any of:
            | *ern* = String or Eratos Resource Name (ERN) of an existing Policy object in Eratos to retrieve. (Default value is None)
            | *yaml* = Yaml object to set policy content. (Default value is None)
            | *json* = JSON object to set policy content. (Default value is None)
            | *content* = Dictionary object to set policy content. (Default value is None)

        Returns
        -------
        Policy
            An Eratos Policy object to interact with.
        """
        return Policy(self, *args, **kwargs)

    def Data(self, *args, **kwargs):
        """
        Interacts with the underlying data in a Resource.

        Data() returns a Data object with the ability to interact with the data that a Resource contains.

        Parameters
        ----------
        args : args
            Optional non-keyworded arguments.
        kwargs : args
            Optional keyword arguments.
            Arguments can include any of:
            | *ern* = String or Eratos Resource Name (ERN) of an existing Eratos dataset. (Default value is None)
            | *content* = Dictionary object to set data content. (Default value is None)

        Returns
        -------
        Data
            An Eratos Data object to interact with.
        """
        return Data(self, *args, **kwargs)

    def DataVersion(self, *args, **kwargs):
        return DataVersion(self, *args, **kwargs)

class CachedPoolAdapter:
    def __init__(self, adapter: Adapter, cacheTime=3600.0):
        self._adapter = adapter
        self._cacheTime = cacheTime
        self._cache = {
            'resources': {},
            'policies': {},
            'data': {},
        }

    def master_pn(self):
        return self._adapter.master_pn()

    def request(self, target_ern: Ern, method: str, path: str, headers={}, retRequest=False, retOnlyRequest=False, **kwargs):
        return self._adapter.request(target_ern, method, path, headers=headers, retRequest=retRequest, retOnlyRequest=retOnlyRequest, **kwargs)
    def dnrequest(self, dnurl: str, method: str, path: str, headers={}, **kwargs):
        return self._adapter.dnrequest(dnurl, method, path, headers=headers, **kwargs)

    def dnbasicrequest(self, method: str, ep: str, headers={}, **kwargs):
        return self._adapter.dnbasicrequest(method, ep, headers=headers, **kwargs)

    def dnstreamrequest(self, method: str, ep: str, headers={}, **kwargs):
        return self._adapter.dnstreamrequest(method, ep, headers=headers, **kwargs)

    def session(self):
        return self._adapter.session()

    def search_adapter(self, return_limit=-1, **kwargs):
        return self._adapter.search_adapter(return_limit=return_limit, **kwargs)

    def search_resources(self, return_limit=-1, **kwargs):
        return self._adapter.search_resources(return_limit=return_limit, **kwargs)

    def _check_cache_item(self, tp, ern, gen):
        if ern in self._cache[tp] and time.monotonic() < self._cache[tp][ern]['fetchTime']+self._cacheTime:
            return self._cache[tp][ern]['item']
        res = gen()
        self._cache[tp][ern] = {
            'fetchTime': time.monotonic(),
            'item': res
        }
        return res

    def Resource(self, *args, **kwargs):
        if 'ern' in kwargs:
            return self._check_cache_item('resources', str(kwargs['ern']), lambda: Resource(self, *args, **kwargs))
        else:
            return Resource(self, *args, **kwargs)

    def Policy(self, *args, **kwargs):
        if 'ern' in kwargs:
            return self._check_cache_item('policies', str(kwargs['ern']), lambda: Policy(self, *args, **kwargs))
        else:
            return Policy(self, *args, **kwargs)

    def Data(self, *args, **kwargs):
        if 'ern' in kwargs:
            return self._check_cache_item('data', str(kwargs['ern']), lambda: Data(self, *args, **kwargs))
        else:
            return Data(self, *args, **kwargs)

    def DataVersion(self, *args, **kwargs):
        if 'ern' in kwargs:
            return self._check_cache_item('dataversion', str(kwargs['ern']), lambda: DataVersion(self, *args, **kwargs))
        else:
            return DataVersion(self, *args, **kwargs)
