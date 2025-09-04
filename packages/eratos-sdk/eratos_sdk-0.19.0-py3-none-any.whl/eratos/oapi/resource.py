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
import gzip
from json import dumps as jdump, loads as jload
from yaml import load as yload, dump as ydump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from deepmerge import Merger

from .errors import ResourceError
from .util import move_prefix_to_new_format

from shapely import wkt
import numpy as np

_logger = logging.getLogger(__name__)

merge_strat = Merger(
    [
        (list, ['override']),
        (dict, ['merge'])
    ],
    ['override'],
    ['override']
)

class Resource(object):
    def __init__(self, adapter, id=None, yaml=None, json=None, content=None):
        self.adapter = adapter
        self.content = {}
        self.links = []
        self.backlinks = []
        if id is not None:
            self.content = {
                '@id': id
            }
            self.fetch()
        elif json is not None:
            self.content_set(jload(json))
        elif yaml is not None:
            self.content_set(yload(yaml, Loader=Loader))
        elif content is not None:
            self.content_set(content)
        else:
            self.content = {}

    def is_valid(self):
        if self.content is None:
            return False
        if '@id' not in self.content:
            return False
        if '@type' not in self.content:
            return False
        if '@owner' not in self.content:
            return False
        if '@policy' not in self.content:
            return False
        return True

    def id(self):
        return self.content['@id']

    def schema_id(self):
        return self.content['@type']

    def policy(self):
        if '@policy' in self.content:
            return self.adapter.Policy(id=self.content['@policy'])
        else:
            return None

    def __repr__(self):
        return '%s: %s (%s)' % (self.content['@id'], self.content['name'], self.content['@type'])

    def owner_id(self):
        return self.content['@owner']

    def set_api_content(self, content):
        self.content = {}
        for key in set(content.keys()).difference(set(['@links', '@backlinks'])):
            self.content[key] = content[key]
        if '@links' in content:
            self.links = content['@links']
        else:
            self.links = []
        if '@backlinks' in content:
            self.backlinks = content['@backlinks']
        else:
            self.backlinks = []

    def fetch(self):
        if '@id' not in self.content:
            raise ResourceError('@id must be specified before fetching')
        self.set_api_content(self.adapter.request('GET', self.content['@id']))
        return self
    
    def save(self):
        if '@id' not in self.content:
            # We are creating the resource.
            if '@type' not in self.content:
                raise ResourceError('@type must be specified before creating')
            self.set_api_content(self.adapter.request('POST', '/resources', data=jdump(self.content).encode('utf-8')))
        else:
            if not self.is_valid():
                raise ResourceError('resource not in a state to update')
            self.set_api_content(self.adapter.request('PUT', self.content['@id'], data=jdump(self.content).encode('utf-8')))
        return self

    def remove(self):
        if not self.is_valid():
            raise ResourceError('resource not in a state to remove')
        self.adapter.request('DELETE', self.content['@id'])
        self.set_api_content({})
        return self

    def data(self):
        return self.adapter.Data(self, id=(self.content['@data'] if '@data' in self.content else None))

    def content_set(self, content):
        new_content = move_prefix_to_new_format(content)
        for cp in ['@id', '@owner', '@policy']:
            if cp in self.content:
                new_content[cp] = self.content[cp]
        self.content = new_content
        return self

    def yaml_set(self, yaml):
        return self.content_set(yload(yaml, Loader=Loader))

    def json_set(self, yaml):
        return self.content_set(jload(yaml))

    def content_merge(self, content):
        prefix_vals = {}
        for cp in ['@id', '@owner', '@policy']:
            if cp in self.content:
                prefix_vals[cp] = self.content[cp]
        for k in content.keys():
            self.content[k] = content[k]
        for cp in ['@id', '@owner', '@policy']:
            if cp in prefix_vals:
                self.content[cp] = prefix_vals[cp]
        return self

    def yaml_merge(self, yaml):
        return self.content_merge(yload(yaml, Loader=Loader))

    def json_merge(self, json):
        return self.content_merge(jload(json))

    def json(self, **kwargs):
        return jdump(self.content, **kwargs)
    
    def yaml(self, **kwargs):
        return ydump(self.content, Dumper=Dumper, **kwargs)

    def get_geo(self, detail='max', asVec=False):
        if detail not in ['point', 'box', 'max']:
            raise ValueError('detail should be one of point/box/max')
        wkt_data = self.adapter.request('GET', self.content['@id']+'/geo?type=wkt&detail=%s' % detail).decode('utf-8')
        wkt_elem = wkt.loads(wkt_data.split(';')[-1])
        if asVec:
            if detail == 'point':
                return np.asarray(wkt_elem)
            elif detail == 'box':
                return np.asarray(list(zip(*wkt_elem.exterior.coords.xy)))
        else:
            return wkt_elem

    def set_geo(self, wkt):
        hdr = {
            'Content-Type': 'application/vnd.eratos.geo+wkt',
            'Content-Encoding': 'gzip'
        }
        return self.adapter.request('POST', self.content['@id']+'/geo', headers=hdr, data=gzip.compress(wkt.encode('ascii')))

    # def get_geo(self, ):

