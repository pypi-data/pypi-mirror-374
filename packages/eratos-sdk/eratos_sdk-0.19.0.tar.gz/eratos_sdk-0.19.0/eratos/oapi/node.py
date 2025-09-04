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

import logging
import pprint

from .errors import PolicyError, CommError
from .util import decode_request_content_response

_logger = logging.getLogger(__name__)

class Node:
    def __init__(self, adapter, id=None, content=None):
        self.adapter = adapter
        self.host = None
        self.content = {}
        if id is not None:
            self.content = {
                'id': id
            }
            self.fetch()
        elif content is not None:
            self.content = content

    def is_valid(self):
        if self.content is None:
            return False
        if 'id' not in self.content:
            return False
        return True

    def fetch(self):
        if 'id' not in self.content:
            raise PolicyError('id must be specified before fetching')
        self.content = self.adapter.request('GET', self.content['id'])
        return self

    def remove(self):
        self.adapter.request('DELETE', self.content['id'])

    def id(self):
        return self.content['id']

    def policy(self):
        if 'policy' in self.content:
            return self.adapter.Policy(id=self.content['policy'])
        else:
            return None

    def owner(self):
        return self.content['owner']

    def friendly_id(self):
        return self.content['friendlyId']

    def desc(self):
        return self.content['description']

    def is_active(self):
        return self.content['isActive']

    def activation_token(self):
        if 'activationToken' in self.content:
            return self.content['activationToken']
        return None

    def config(self):
        return self.content['config']

    def endpoint(self):
      _logger.debug('push_files: datanode content: %s' % (pprint.pformat(self.content, width=1024*1024)))
      return self.content['controlAPIEndpoint']

    def last_ping(self):
      return self.content['lastPing']

    def last_iptrace(self):
      return self.content['lastIPTrace']

    def request(self, method: str, path: str, headers={}, **kwargs):
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        if 'Accept' not in headers:
            headers['Accept'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.adapter.get_data_node_token()
        url = self.endpoint() + path
        req = self.adapter.session().request(method, url, headers=headers, verify=not self.adapter.ignore_certs, **kwargs)
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
