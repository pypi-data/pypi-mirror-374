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
import pprint
import mimetypes
import base64
import hashlib
from json import dumps as jdump

from .gsdata import GSData
from .errors import PolicyError
from .util import calc_best_chunk_size, dataset_chunks, hash_dataset_chunks, get_meta_items, extract_pn_and_did, calc_filemap_from_chunk, Merkle

_logger = logging.getLogger(__name__)

class Data:
    def __init__(self, adapter, resource, id=None, content=None):
        self.adapter = adapter
        self.content = {}
        self.resource = resource
        self.version = None
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
        if 'resource' not in self.content:
            return False
        return True

    def id(self):
        return self.content['id']

    def fetch(self):
        if 'id' not in self.content:
            raise PolicyError('id must be specified before fetching')
        self.content = self.adapter.request('GET', self.content['id'])
        if 'master' in self.content and 'versions' in self.content and self.content['master'] in self.content['versions']:
            self.version = self.content['versions'][self.content['master']]
        else:
            self.version = None
        return self

    def versions(self):
        if 'versions' in self.content:
            return self.content['versions']
        else:
            return []

    def is_synced(self):
        return self.content['info']['isSync'] if 'isSync' in self.content['info'] else False

    def content_available(self, allow_partial=False):
        if 'master' not in self.content or 'versions' not in self.content:
            return None
        if self.content['master'] not in self.content['versions']:
            return None
        for k in self.content['versions'][self.content['master']]['nodes'].keys():
            if self.content['versions'][self.content['master']]['nodes'][k]['status'] == 'Valid':
                return k
            if allow_partial and self.content['versions'][self.content['master']]['nodes'][k]['status'] == 'Partial':
                return k
        return None

    def targs_files(self, files):
        if type(files) is list:
            for i in range(len(files)):
                if type(files[i]) is dict:
                    if 'path' not in files[i]:
                        raise AttributeError('expected path prop in files list')
                    if 'mime' not in files[i]:
                        files[i]['mime'] = mimetypes.guess_type(files[i]['path'])[0]
                elif type(files[i]) is str:
                    files[i] = { 'path': files[i], 'mime': mimetypes.guess_type(files[i])[0] }
                else:
                    raise AttributeError('items in files must be either a dict or a string')
            return files
        elif type(files) is dict:
            if 'path' not in files:
                raise AttributeError('expected path prop in files')
            if 'mime' not in files:
                files['mime'] = mimetypes.guess_type(files['path'])[0]
            return [files]
        elif type(files) is str:
            return [{ 'path': files, 'mime': mimetypes.guess_type(files)[0] }]
        else:
            raise AttributeError('files must be either a list, dict, or a string')

    def create_file_dataset(self, chunk_size):
        if not self.is_valid():
            ds_create_body = {
                'resource': self.resource.id(),
                'type': 'Objects',
                'meta': {
                    'update': 'None',
                    'hash': {
                        'type': 'Bytes',
                        'size': chunk_size,
                        'algorithm': 'SHA256'
                    }
                }
            }
            _logger.debug('push_files: creating dataset: %s' % pprint.pformat(ds_create_body, width=1024*1024))
            self.content = self.adapter.request('POST', '/datasets', data=jdump(ds_create_body).encode('utf-8'))
            _logger.debug('push_files: creating dataset: %s' % pprint.pformat(self.content, width=1024*1024))
        else:
            _logger.debug('push_files: using created dataset: %s' % pprint.pformat(self.content, width=1024*1024))

    def push_files(self, files, store, geom=None, verbose=False):
        '''
        Push files to a given store (Creating a new dataset if required).
        '''
        # Translate files to the expected form.
        files = self.targs_files(files)
        # Validate the file list.
        for fn in files:
            if not os.path.exists(fn['path']):
                raise AttributeError('file %s cannot be found' % fn['path'])
            if os.path.isdir(fn['path']):
                raise AttributeError('file %s is a directory' % fn['path'])
        # Get the data node represented by store.
        dn = self.adapter.NodeList(incEratosNodes=True).find(store)
        if dn is None:
            raise AttributeError('store either does not point to a valid data node or you do not have access to it')
        # If the dataset doesn't exist, create it.
        self.create_file_dataset(calc_best_chunk_size(files))
        # Check we can push files to it.
        if self.content['type'] != 'Objects':
            raise AttributeError('cannot push files to a non object dataset')
        # Give the node access to the resource/dataset.
        ds_version_node = {
            'isSync': False
        }
        _logger.debug('push_files: attaching node to dataset: %s' % pprint.pformat(ds_version_node, width=1024*1024))
        self.content = self.adapter.request('POST', self.id(), params={'node':dn.id()}, data=jdump(ds_version_node).encode('utf-8'))
        _logger.debug('push_files: attached node to dataset: %s' % pprint.pformat(self.version, width=1024*1024))
        # Hash the file list.
        _logger.debug('push_files: calculating hashes using chunk size: %d' % self.content['meta']['hash']['size'])
        hashes = hash_dataset_chunks(files, self.content['meta']['hash']['size'])
        merkle = Merkle(hashes)
        _logger.debug('push_files: calculated hashes: %s' % pprint.pformat([base64.b64encode(h).decode('ascii') for h in hashes], width=1024*1024))
        _logger.debug('push_files: calculated merkel root: %s' % merkle.root_b64())
        # Create a new version of the dataset.
        if not (self.version is not None and self.version['manifest']['merkelRootHash'] == merkle.root_b64()):
            meta_files = get_meta_items(files)
            ds_version_body = {
                'comment': 'Initial manifest',
                'manifest': {
                    'items': meta_files,
                    'merkelRootHash': merkle.root_b64()
                },
                'fetchInterfaces': {
                    'File:v1': {}
                }
            }
            if geom is not None:
                ds_version_body['fetchInterfaces']['Geom:v1'] = geom
            _logger.debug('push_files: creating new dataset version: %s' % pprint.pformat(ds_version_body, width=1024*1024))
            self.version = self.adapter.request('POST', self.content['id']+'/versions', data=jdump(ds_version_body).encode('utf-8'))
            _logger.debug('push_files: created new dataset version: %s' % pprint.pformat(self.version, width=1024*1024))
        else:
            _logger.debug('push_files: no need to create new version: %s' % pprint.pformat(self.version, width=1024*1024))
        # Get the primary node and data id.
        pn, did = extract_pn_and_did(self.content['id'])
        # Push the dataset to the node.
        dn_create_dataset = {
            'fetchType': 'Served',
            'version': self.version['version']
        }
        _logger.debug('push_files: pushing dataset to node (%s, %s): %s' % (pn, did, pprint.pformat(dn_create_dataset, width=1024*1024)))
        dn_dataset = dn.request('POST', '/datasets/%s/%s' % (pn, did), data=jdump(dn_create_dataset).encode('utf-8'))
        _logger.debug('push_files: pushed dataset to node (%s, %s): %s' % (pn, did, pprint.pformat(dn_dataset, width=1024*1024)))
        # Push the hashes.
        _logger.debug('push_files: pushing hashes to node (%s, %s)' % (pn, did))
        dn.request('POST', '/datasets/%s/%s/hashes' % (pn, did), headers={'Content-Type': 'application/vnd.eratos.sha256hashlist'}, data=b''.join(hashes))
        # Push the data.
        chunk_idx = 0
        for chunk in dataset_chunks(files, self.content['meta']['hash']['size']):
            if verbose:
                print('Pushing chunk %d/%d' % (chunk_idx+1, len(hashes)))
            _logger.debug('push_files: pushing chunks node (%s, %s): %d' % (pn, did, chunk_idx))
            dn.request('POST', '/datasets/%s/%s/chunks' % (pn, did), params={'idx': chunk_idx}, headers={'Content-Type': 'application/vnd.eratos.chunk'}, data=chunk)
            chunk_idx += 1
        if chunk_idx != self.version['manifest']['chunkCount']:
            raise AttributeError('incorrect number of chunks pushed')

    def pull_files(self, dest, version=None):
        # Get the version to pull the data from.
        if 'master' not in self.content or 'versions' not in self.content:
            raise AttributeError('no version available with valid dataset')
        if version is None:
            version = self.content['master']
        if version not in self.content['versions']:
            raise AttributeError('given version not in the dataset')
        # Fetch the version.
        _logger.debug('pull_files: fetching dataset version: %s' % self.content['versions'][version]['version'])
        ds_version = self.adapter.request('GET', self.version['version'])
        _logger.debug('pull_files: fetched dataset version: %s' % pprint.pformat(ds_version, width=1024*1024))
        # Fine the nodes that the version is on.
        nodes_with_data = []
        for k in ds_version['nodes']:
            if ds_version['nodes'][k]['status'] == 'Valid':
                nodes_with_data += [self.adapter.Node(id=k)]
        if len(nodes_with_data) == 0:
            raise AttributeError('no node with the data for the given dataset version')
        # Fetch the hash list from one node.
        pn, did = extract_pn_and_did(self.content['id'])
        _logger.debug('pull_files: pulling hashes for (%s, %s) from node %s' % (pn, did, nodes_with_data[0].id()))
        hash_data = nodes_with_data[0].request('GET', '/datasets/%s/%s/hashes' % (pn, did), headers={'Accept': 'application/vnd.eratos.sha256hashlist'})
        hashes = []
        num_hashes = len(hash_data) // 32
        if num_hashes != ds_version['manifest']['chunkCount']:
            raise AttributeError('the number of hashes in the hash list %d is not what was expected %d' % (num_hashes, ds_version['manifest']['chunkCount']))
        for i in range(0,num_hashes):
            hashes += [hash_data[32*i:32*(i+1)]]
        merkle = Merkle(hashes)
        _logger.debug('pull_files: calculated hashes: %s' % pprint.pformat([base64.b64encode(h).decode('ascii') for h in hashes], width=1024*1024))
        _logger.debug('pull_files: calculated merkel root: %s' % merkle.root_b64())
        if merkle.root_b64() != ds_version['manifest']['merkelRootHash']:
            raise AttributeError('merkel root hash of hash list does not equal expected value')
        # Create the stubs of the files in the output directory.
        for it in ds_version['manifest']['items']:
            itpath = os.path.join(dest, it['path'])
            os.makedirs(os.path.dirname(itpath), exist_ok=True)
            _logger.debug('pull_files: precreating file: %s' % itpath)
            open(itpath, 'w+b').close()
        # Fetch the chunks from nodes in a round robin manner and construct the files.
        for chunk_idx in range(ds_version['manifest']['chunkCount']):
            _logger.debug('pull_files: pulling chunk %d for (%s, %s) from node %s' % (chunk_idx, pn, did, nodes_with_data[0].id()))
            chunk = nodes_with_data[0].request('GET', '/datasets/%s/%s/chunks' % (pn, did), params={'idx': chunk_idx}, headers={'Accept': 'application/vnd.eratos.chunk'})
            if len(chunk) != ds_version['manifest']['chunkSize']:
                raise AttributeError('the size of the returned %d chunk %d is not what was expected %d' % (chunk_idx, len(chunk), ds_version['manifest']['chunkSize']))
            chunk_hash = hashlib.sha256(chunk).digest()
            _logger.debug('pull_files: pulled chunk %d hash %s' % (chunk_idx, base64.b64encode(chunk_hash).decode('ascii')))
            if chunk_hash != hashes[chunk_idx]:
                raise AttributeError('the hash of the returned %d chunk %s is not what was expected %s' % (chunk_idx, base64.b64encode(chunk_hash).decode('ascii'), base64.b64encode(hashes[chunk_idx]).decode('ascii')))
            icls = calc_filemap_from_chunk(ds_version['manifest'], chunk_idx)
            for icl in icls:
                file_start = icl['file_start']
                file_end = icl['file_start'] + icl['count']
                chunk_start = icl['chunk_start']
                chunk_end = icl['chunk_start'] + icl['count']
                _logger.debug('pull_files: mapping chunk %d[%d:%d] -> %s[%d:%d]' % (chunk_idx, chunk_start, chunk_end, icl['item']['path'], file_start, file_end))
                itpath = os.path.join(dest, icl['item']['path'])
                with open(itpath, 'r+b') as f:
                    f.seek(file_start, os.SEEK_SET)
                    f.write(chunk[chunk_start:chunk_end])

    def sync_files(self, files, store, store_root_path, geom=None, chunk_size=1048576):
        '''
        Sync files on a given store (Creating a new dataset if required).
        '''
        # Translate files to the expected form.
        files = self.targs_files(files)
        # Get the data node represented by store.
        dn = self.adapter.NodeList(incEratosNodes=True).find(store)
        if dn is None:
            raise AttributeError('store either does not point to a valid data node or you do not have access to it')
        # If the dataset doesn't exist, create it.
        self.create_file_dataset(chunk_size)
        # Check we can push files to it.
        if self.content['type'] != 'Objects':
            raise AttributeError('cannot push files to a non object dataset')
        # Give the node access to the resource/dataset.
        ds_version_node = {
            'isSync': True
        }
        _logger.debug('sync_files: attaching node to dataset: %s' % pprint.pformat(ds_version_node, width=1024*1024))
        self.content = self.adapter.request('POST', self.id(), params={'node':dn.id()}, data=jdump(ds_version_node).encode('utf-8'))
        _logger.debug('sync_files: attached node to dataset: %s' % pprint.pformat(self.version, width=1024*1024))
        # Sync the files on the node.
        pn, did = extract_pn_and_did(self.content['id'])
        dn_create_dataset = {
            'fetchType': 'Synced',
            'items': files,
            'syncPath': store_root_path,
            'fetchInterfaces': {
                'File:v1': {}
            }
        }
        if geom is not None:
            dn_create_dataset['fetchInterfaces']['Geom:v1'] = geom
        _logger.debug('sync_files: pushing dataset to node (%s, %s): %s' % (pn, did, pprint.pformat(dn_create_dataset, width=1024*1024)))
        dn_dataset = dn.request('POST', '/datasets/%s/%s' % (pn, did), data=jdump(dn_create_dataset).encode('utf-8'))
        _logger.debug('sync_files: pushed dataset to node (%s, %s): %s' % (pn, did, pprint.pformat(dn_dataset, width=1024*1024)))

    # def poll_sync(self, plog=False):
    #     # Loop until there is either an error, or the file has synced.
    #     while True:
    #         self.fetch()
    #         if not self.is_synced():
    #             return True
    #         if 'syncError' in self.content['info'] and self.content['info']['syncError'] is not None:
    #             return False
    #         if 'contentMerkleRootHash' in self.content['info'] and self.content['info']['contentMerkleRootHash'] is not None:
    #             return True
    #         if plog:
    #             loc = self.location(self.content['info']['syncNode'])
    #             if 'chunkCount' not in self.content['info'] or loc is None:
    #                 print("sync: initialising")
    #             else:
    #                 print("sync: %s/%s" % (loc['info']['validatedChunkCount'], self.content['info']['chunkCount']))
    #         time.sleep(1)

    # def pull_file_2(self, dest):
    #     # Find a node we have permission to pull from.
    #     dn_list = self.adapter.NodeList()
    #     dn = None
    #     for loc in self.locations():
    #       if loc['info']['validatedChunkCount'] != self.content['info']['chunkCount']:
    #         continue
    #       dn = dn_list.find(loc['node'])
    #       if dn is not None:
    #         break
    #     if dn is None:
    #         raise AttributeError('you do not have access to a data node with the given content')
    #     # Pull the full file.
    #     with open(dest, "w+b") as wf:
    #         file_content = dn.request('GET', '/api/file', params={'id':self.id()})
    #         wf.write(file_content)

    # @contextlib.contextmanager
    # def data(self, text=False):
    #     fd, path = tempfile.mkstemp('etf')
    #     self.pull_file(path)
    #     with open(path, 'r' if text else 'rb') as f:
    #         yield f
    #     os.close(fd)

    # def remove(self):
    #   return self

    def gapi(self):
        if self.version is not None and 'Geom:v1' in self.version['fetchInterfaces']:
            return GSData(adapter=self.adapter, resource=self.resource, data=self)
        return None
