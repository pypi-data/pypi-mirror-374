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

from json import dumps as jdump

class Collection(object):
    def __init__(self, adapter, id=None, name=None, tp=None):
        self.adapter = adapter
        if id is not None:
            self.resource = self.adapter.Resource(id)
        elif name is not None:
            if tp is None:
              raise Exception('tp must be specified with name')
            elif tp not in ['resource', 'user']:
              raise Exception('tp must be one of resource or user')
            content={
              '@type': 'https://schemas.eratos.ai/json/collection.resource' if tp == 'resource' else 'https://schemas.eratos.ai/json/collection.user',
              'name': name
            }
            self.resource = self.adapter.Resource(content=content)
            self.resource.save()
        else:
            raise Exception('id or name must be specified')

    def is_valid(self):
        return self.resource.is_valid()

    def id(self):
        return self.resource.id()

    def collection_type(self):
        if not self.is_valid():
            raise Exception('collection is not valid')
        if self.resource.content['@type'] == 'https://schemas.eratos.ai/json/collection.resource':
          return 'resource'
        else:
          return 'user'

    def item_count(self):
        if not self.is_valid():
            raise Exception('collection is not valid')
        return self.resource.content['itemCount']

    def add_items(self, ids):
        if not self.is_valid():
            raise Exception('collection is not valid')
        req_content = {
          'action': 'Add',
          'items': ids
        }
        res = self.adapter.request('POST', self.resource.content['@id']+'/items', data=jdump(req_content).encode('utf-8'))
        self.resource.content['itemCount'] = res['totalItems']
        return res['deltaItems']
        
    def rem_items(self, ids):
        if not self.is_valid():
            raise Exception('collection is not valid')
        req_content = {
          'action': 'Remove',
          'items': ids
        }
        res = self.adapter.request('POST', self.resource.content['@id']+'/items', data=jdump(req_content).encode('utf-8'))
        self.resource.content['itemCount'] = res['totalItems']
        return res['deltaItems']

    def items(self, just_ids=False):
      next_url = self.resource.content['@id'] + '/items?count=20&incLinkedData=true'
      while True:
        if next_url is None:
          break
        res = self.adapter.request('GET', next_url)
        if 'next' in res:
          next_url = res['next']
        else:
          next_url = None
        for iid in res['items']:
          if iid in res['@links']:
            yield self.adapter.Resource(content=res['@links'][iid])
          else:
            yield self.adapter.Resource(id=iid)
