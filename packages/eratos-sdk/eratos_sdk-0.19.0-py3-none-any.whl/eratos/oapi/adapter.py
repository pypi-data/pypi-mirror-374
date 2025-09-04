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

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from json import dumps as jdump, loads as jload

from .creds import AccessTokenCreds
from .resource import Resource
from .search import SearchAdapter
from .policy import Policy
from .collection import Collection
from .node import Node
from .data import Data
from .nodetask import NodeTask
from .nodelist import NodeList
from .errors import CommError
from .util import decode_request_content_response
from . import __primarynode__

from .block import Block

_logger = logging.getLogger(__name__)
_node_name_validator = re.compile('^[a-zA-Z0-9-]+$')

def decode_jwt_claims(token):
    b64claims = token.split('.')[1]
    b64claims += '=' * (4 - (len(b64claims) % 4))
    return jload(base64.urlsafe_b64decode(b64claims))

class Adapter:
    def __init__(self, creds: AccessTokenCreds, host=__primarynode__, ignore_certs=False):
        self.creds = creds
        self.host = host
        self.ignore_certs = ignore_certs
        self.dn_token = None
        if os.name == 'nt':
            self.config_dir = os.path.join(os.environ['USERPROFILE'], 'eratos')
        else:
            self.config_dir = os.path.join(os.environ['HOME'], '.eratos')
        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)
        self._httpAdp = HTTPAdapter(max_retries=Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        ))
        self._httpSession = requests.Session()
        self._httpSession.mount("https://", self._httpAdp)
        self._httpSession.mount("http://", self._httpAdp)
        self._httpSession.trust_env = False

    def request(self, method: str, path: str, headers={}, **kwargs):
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        if 'Accept' not in headers:
            headers['Accept'] = 'application/json'
        url = path if 'http:' in path or 'https:' in path else self.host+path
        req = self._httpSession.request(method, url, headers=headers, auth=self.creds, verify=not self.ignore_certs, **kwargs)
        _logger.debug('pn request: %s %s (%d)' % (method, url, req.status_code))
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

    def session(self):
        return self._httpSession

    def get_data_node_token(self):
        if self.dn_token is None or self.dn_token['claims']['exp'] < (time.time() + 60):
            tres = self.request('GET', '/token/node')
            self.dn_token = {
                "raw": tres['token'],
                "claims": decode_jwt_claims(tres['token'])
            }
            _logger.debug('adapter: new dn_token: %s' % self.dn_token['raw'])
        return self.dn_token['raw']

    def get_data_node_ca_path(self):
        hostbase64 = base64.urlsafe_b64encode(self.host.encode('ascii')).decode('ascii')
        cert_file = os.path.join(self.config_dir, 'noderoot.%s.crt' % hostbase64)
        if not os.path.exists(cert_file):
            cert_res = self._httpSession.request('GET', self.host+'/certs/dnroot.crt', verify=not self.ignore_certs)
            if cert_res.status_code >= 200 and cert_res.status_code < 400:
                _logger.debug('get_data_node_ca_path: cert data:\n%s' % cert_res.text)
                with open(cert_file, 'w+t') as f:
                    f.write(cert_res.text)
            else:
                if 'application/json' in cert_res.headers.get('Content-Type'):
                    raise CommError(cert_res.status_code, cert_res.json())
                else:
                    raise CommError(cert_res.status_code, { 'code': 'unknown', 'message': cert_res.text })
        _logger.debug('get_data_node_ca_path: cert file %s' % cert_file)
        return cert_file

    def user_policy(self):
        data = self.request('GET', '/me')
        return self.Policy(id=data['ResourcePolicy'])

    def search_adapter(self):
        return SearchAdapter(self)

    def search_resources(self, props={}, limit=None):
        adp = SearchAdapter(self, props=props, limit=limit)
        return list([res for res in adp.search()])

    # Deprecated fn.
    def search(self, query, typ=None, ext_source=None, tags=None, rel=None, loc=None, start=None, fns={}):
        query = {
            "q": query
        }
        if typ is not None:
            query["type"] = typ
        if ext_source is not None:
            query["extSource"] = ext_source
        if tags is not None:
            query["tags"] = ",".join(tags)
        if loc is not None:
            query["loc"] = loc
        if rel is not None:
            query["rel"] = rel
        if start is not None:
            query["start"] = start
        for k in fns.keys():
            query[k] = fns[k]
        return self.request('GET', '/search?' + urllib.parse.urlencode(query))

    def search_tags(self, query, tags=None):
        query = {
            "Query": query
        }
        if tags is not None:
            query["Tags"] = ",".join(tags)
        data = self.request('GET', '/tags?' + urllib.parse.urlencode(query))
        return data

    def create_data_node(self, friendlyId="", description=""):
        if type(friendlyId) is not str:
            raise TypeError('friendlyId should be of type str')
        if type(description) is not str:
            raise TypeError('description should be of type str')
        if _node_name_validator.match(friendlyId) is None:
            raise ValueError('friendlyId should match ^[a-zA-Z0-9-]+$')
        nodeCreateData = {
            'friendlyId': friendlyId,
            'description': description,
        }
        data = self.request('POST', '/nodes', data=jdump(nodeCreateData).encode('utf-8'))
        return self.Node(content=data)

    def Resource(self, *args, **kwargs):
        return Resource(self, *args, **kwargs)

    def Policy(self, *args, **kwargs):
        return Policy(self, *args, **kwargs)

    def Collection(self, *args, **kwargs):
        return Collection(self, *args, **kwargs)

    def Node(self, *args, **kwargs):
        return Node(self, *args, **kwargs)

    def NodeTask(self, *args, **kwargs):
        return NodeTask(self, *args, **kwargs)
        
    def NodeList(self, *args, **kwargs):
        return NodeList(self, *args, **kwargs)

    def Data(self, *args, **kwargs):
        return Data(self, *args, **kwargs)
