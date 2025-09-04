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
from json import dumps as jdump, loads as jload
from yaml import load as yload, dump as ydump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from deepmerge import Merger

from .errors import PolicyError
from .util import move_prefix_to_new_format

_logger = logging.getLogger(__name__)

merge_strat = Merger(
    [
        (list, ['append']),
        (dict, ['merge'])
    ],
    ['override'],
    ['override']
)

class Policy:
    def __init__(self, adapter, id=None, yaml=None, json=None, content=None):
        self.adapter = adapter
        self.content = {}
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

    def is_valid(self):
        if self.content is None:
            return False
        if '@id' not in self.content:
            return False
        if '@type' not in self.content:
            return False
        if '@owner' not in self.content:
            return False
        if '@for' not in self.content:
            return False
        return True

    def is_resource_policy(self):
      if '@type' not in self.content:
        return False
      if self.adapter.host+'/schemas/node_policy' == self.content['@type']:
        return True
      return False

    def is_node_policy(self):
      if '@type' not in self.content:
        return False
      if self.adapter.host+'/schemas/node_policy' == self.content['@type']:
        return True
      return False

    def id(self):
        return self.content['@id']

    def schema_id(self):
        return self.content['@type']

    def isfor_id(self):
        return self.content['@for']

    def owner_id(self):
        return self.content['@owner']

    def fetch(self):
        if '@id' not in self.content:
            raise PolicyError('@id must be specified before fetching')
        self.content = self.adapter.request('GET', self.content['@id'])
        return self
    
    def save(self):
        if '@id' not in self.content:
            # We are creating the resource.
            if '@type' not in self.content:
                raise PolicyError('you may not create a policy directly')
        else:
            if not self.is_valid():
                raise PolicyError('resource not in a state to update')
            self.content = self.adapter.request('PUT', self.content['@id'], data=jdump(self.content).encode('utf-8'))
        return self

    def content_set(self, content):
        new_content = move_prefix_to_new_format(content)
        for cp in ['@id', '@owner', '@for', '@type']:
            if cp in self.content:
                new_content[cp] = self.content[cp]
        self.content = new_content
        return self

    def content_merge(self, content):
        new_content = merge_strat.merge(self.content, content)
        for cp in ['@id', '@owner', '@for', '@type']:
            if cp in self.content:
                new_content[cp] = self.content[cp]
        self.content = new_content
        return self

    def yaml_set(self, yaml):
        return self.content_set(yload(yaml, Loader=Loader))

    def yaml_merge(self, yaml):
        return self.content_merge(yload(yaml, Loader=Loader))

    def json(self, **kwargs):
        return jdump(self.content, **kwargs)
    
    def yaml(self, **kwargs):
        return ydump(self.content, Dumper=Dumper, **kwargs)

    def add_rule(self, actor, effect, actions):
        if '@id' not in self.content:
            raise PolicyError('@id must be specified before adding a rule')
        # Check similar rule already exists and edit the actions.
        for i in range(len(self.content['rules'])):
            if self.content['rules'][i]['actor'] == actor and self.content['rules'][i]['effect'] == effect:
                self.content['rules'][i]['actions'] = actions
                return self
        # Otherwise add a new rule.
        self.content['rules'] += [{
          'actor': actor,
          'effect': effect,
          'actions': actions,
        }]
        return self

    def invite_user(self, email, actions):
        if '@id' not in self.content:
            raise PolicyError('@id must be specified before inviting a user')
        # Check to see if user has already been invited, if so replace the actions.
        if '@invites' in self.content:
            for inv in self.content['@invites']:
                if inv['email'] == email:
                    self.adapter.request('PUT', inv.id, data=jdump({'Actions': actions}).encode('utf-8'))
                    return self.fetch()
        # Check to see if the user already has policy permissions.
        if '@links' in self.content:
            for k in self.content['@links'].keys():
                if self.content['@links'][k]['email'] == email:
                    return self.add_rule(k, 'Allow', actions).save()
        # Invite user
        req_body = {
            'TargetID': self.content['@id'],
            'Email': email,
            'Actions': actions
        }
        self.adapter.request('POST', self.adapter.host+'/shares', data=jdump(req_body).encode('utf-8'))
        return self.fetch()
