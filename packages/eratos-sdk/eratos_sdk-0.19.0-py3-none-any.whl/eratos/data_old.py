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
import mimetypes
import logging
from posixpath import isabs
import pprint
import mimetypes
import base64
import hashlib
import copy
from json import dumps as jdump

from .ern import Ern
from .oapi.creds import AccessTokenCreds as OAPIAccessTokenCreds
from .oapi.adapter import Adapter as OAPIAdapter
from .oapi.util import extract_pn_and_did, calc_filemap_from_chunk, Merkle

from .gsdata_old import GSData
from .errors import PolicyError

_logger = logging.getLogger(__name__)

_node_id_map = {
    'au-1.e-gn.io': 'au-1.e-gn.io',
    'cfp-au-tas-1': 'cfp-au-tas-1',
    'cfp-au-qld-1': 'cfp-au-qld-1',
    'cfp-au-wa-1': 'cfp-au-wa-1'
}

class Data:
    """
    A class to interact with Eratos' Resource Data.
    """
    @staticmethod
    def is_data(v):
        """
        A utility function to determine that the object is of type Data.

        Returns
        -------
        bool
            True or False depending on the type of the object.
        """
        return isinstance(v, Data)
    
    def __init__(self, adapter, resource, id=None, content=None):
        self._adapter = adapter
        self._resource = resource
        self._content = {}
        self._version = None
        if id is not None:
            self._content = {
                'id': id
            }
            self.fetch()
        elif content is not None:
            self._content = content

    def is_valid(self):
        """
        A utility function to determine the validity of a Data resource's fields.

        Returns
        -------
        bool
            True or False depending on the validity of a field.
        """
        if self._content is None:
            return False
        if 'id' not in self._content:
            return False
        if 'resource' not in self._content:
            return False
        return True

    def id(self):
        """
        Retrieves the unique Eratos Resource Name (ERN) ID.

        Returns
        -------
        str
            The unique Eratos Resource Name (ERN) ID of the current Resource.
        """
        return self._content['id']

    def fetch(self):
        """
        Fetches the data object.

        Returns
        -------
        Resource
            The data object resource.
        """
        if 'id' not in self._content:
            raise PolicyError('id must be specified before fetching')
        self._content = self._adapter.dnrequest('', 'GET', '/datasets', params={'ds': self._content['id']})
        if 'master' in self._content and 'versions' in self._content and self._content['master'] in self._content['versions']:
            self._version = self._content['versions'][self._content['master']]
        else:
            self._version = None
        return self

    def versions(self):
        """
        Retrieves the data versions if exists.

        Returns
        -------
        list[str]
            The versions that exist for a data object.
        """
        if 'versions' in self._content:
            return self._content['versions']
        else:
            return []

    def content_available(self, allow_partial=False):
        """
        Retrieves the key of data with content available.

        Parameters
        ----------
        allow_partial : bool
            Allow content that has a status of 'Partial'. (Default value is False)

        Returns
        -------
        str | None
            The string key of data with content available if exists.
        """
        if 'master' not in self._content or 'versions' not in self._content:
            return None
        if self._content['master'] not in self._content['versions']:
            return None
        for k in self._content['versions'][self._content['master']]['nodes'].keys():
            if self._content['versions'][self._content['master']]['nodes'][k]['status'] == 'Valid':
                return k
            if allow_partial and self._content['versions'][self._content['master']]['nodes'][k]['status'] == 'Partial':
                return k
        return None

    def sync_file_list(self):
        """
        Fetches the file paths for synced files.
        """
        if 'master' not in self._content or 'versions' not in self._content:
            return None

        version = self._content['versions'][self._content['master']]
        manifest = version['manifest']

        isSync = False
        for nid in version['nodes'].keys():
            node = version['nodes'][nid]
            if 'storeSync' in node and node['storeSync']:
                isSync = True
        if not isSync:
            return None
        return ['/'+item['path'] for item in manifest['items']]

    def pull_files(self, dest, version=None):
        """
        Pulls the dataset files into a given storage location.

        Parameters
        ----------
        dest : str
            The destination path to store the pulled data files.
        version : str
            A specified version of the data to pull. (Default value is None)

        Raises
        ------
        AttributeError
            If invalid values exist.
        """
        # Get the version to pull the data from.
        if 'master' not in self._content or 'versions' not in self._content:
            raise AttributeError('no version available with valid dataset')
        if version is None:
            version = self._content['master']
        if version not in self._content['versions']:
            raise AttributeError('given version not in the dataset')
        # Fetch the version.
        _logger.debug('pull_files: fetching dataset version: %s' % self._content['versions'][version]['version'])
        ds_version = self._adapter.dnrequest('', 'GET', '/datasets', params={'ds': self._version['version']})
        _logger.debug('pull_files: fetched dataset version: %s' % pprint.pformat(ds_version, width=1024*1024))
        # Find the nodes that the version is on.
        nodes_with_data = []
        for k in ds_version['nodes']:
            if ds_version['nodes'][k]['status'] == 'Valid':
                ds_version['nodes'][k]['id'] = k
                nodes_with_data += [ds_version['nodes'][k]]
        if len(nodes_with_data) == 0:
            raise AttributeError('no node with the data for the given dataset version')
        # Fetch the hash list from one node.
        pn, did = extract_pn_and_did(self._content['id'])
        _logger.debug('pull_files: pulling hashes for (%s, %s) from node %s' % (pn, did, nodes_with_data[0]['id']))
        hash_data = self._adapter.dnrequest('', 'GET', '/datasets/%s/%s/hashes' % (pn, did), headers={'Accept': 'application/vnd.eratos.sha256hashlist'})
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
            _logger.debug('pull_files: pulling chunk %d for (%s, %s) from node %s' % (chunk_idx, pn, did, nodes_with_data[0]['id']))
            chunk = self._adapter.dnrequest('', 'GET', '/datasets/%s/%s/chunks' % (pn, did), params={'idx': chunk_idx}, headers={'Accept': 'application/vnd.eratos.chunk'})
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

    def pull_objects(self, dest, version=None):
        """
        Runs the pull_files() method to pull the dataset files into a given storage location.

        Parameters
        ----------
        dest : str
            The destination path to store the pulled data files.
        version : str
            A specified version of the data to pull. (Default value is None)
        """
        return self.pull_files(dest, version = version)

    def list_objects(self, version=None):
        """
        Gets the lists of objects for a Data resource.

        Parameters
        ----------
        version : str
            A specified version of the data to pull. (Default value is None)

        Raises
        ------
        AttributeError
            If invalid values exist.
        
        Returns
        -------
        arr
            A list of data items including their path, mime type and size.
        """
        # Get the version to pull the data from.
        if 'master' not in self._content or 'versions' not in self._content:
            raise AttributeError('no version available with valid dataset')
        if version is None:
            version = self._content['master']
        if version not in self._content['versions']:
            raise AttributeError('given version not in the dataset')
        # Get the list of objects.
        items = []
        for it in self._content['versions'][version]['manifest']['items']:
            items += [{
                'key': it['path'],
                'mime': it['mime'],
                'size': it['size']
            }]
        return items

    def fetch_object(self, key, dest=".", version=None):
        """
        Downloads data according to a specific key into a destination.

        Parameters
        ----------
        key : str
            The key of the data to fetch.
        dest : str
            The location to store the data. (Default is ".")
        version : str
            A specific version of the data to pull. (Default value is None)

        Raises
        ------
        AttributeError
            If invalid values exist.
        """
        # Get the version to pull the data from.
        if 'master' not in self._content or 'versions' not in self._content:
            raise AttributeError('no version available with valid dataset')
        if version is None:
            version = self._content['master']
        if version not in self._content['versions']:
            raise AttributeError('given version not in the dataset')
        # Check the key exists in the dataset.
        keys = list([it['path'] for it in self._content['versions'][version]['manifest']['items']])
        if key not in keys:
            raise ValueError(f'key {key} not in dataset')
        # Fetch the file.
        if len(self._content['versions'][version]['nodes']) == 0:
            raise AttributeError('no node contains a valid representation of the data')
        firstNodeID = next(iter(self._content['versions'][version]['nodes']))
        firstNode = self._content['versions'][version]['nodes'][firstNodeID]
        fileEP = firstNode['fetchInterfaces']['File:v1']
        resp = self._adapter.dnbasicrequest('GET', fileEP, params={'path': key})
        if os.path.exists(dest) and os.path.isdir(dest):
            dest = os.path.join(dest, key)
        with open(dest, 'w+b') as f:
            f.write(resp.content)

    def push_objects(self, node, files, connector='Objects:Files:v1', connectorProps=None, chunkSize=None):
        """
        Pushes data to a node.

        Parameters
        ----------
        node : str
            The node to push the data to.
        files : arr
            The data filepaths to push.
        connector : str
            A specific type of connector to use on the data. This is specific to the file type. (Default value is 'Objects:Files:v1')
        connectorProps : dict
            The properties for the connector. (Default value is None)
        chunkSize : int64
            The size to chunk the data by. (Default value is None)
        """
        # Validate parameters.
        node, files, connector, connectorProps, chunkSize = \
            self._check_pushsync_inputs(False, node, files, connector, connectorProps, chunkSize)
        # Push the files.
        pushFiles, nodeID, dProps = self._translate_objects(node, files, connector, connectorProps, chunkSize, False)
        self._adapter._refresh_dn_token()
        eadp = OAPIAdapter(OAPIAccessTokenCreds(self._adapter._dn_token['oapk'], self._adapter._dn_token['oaps']), host="https://e-pn.io")
        resKey = str(self._resource.ern())
        nres = eadp.Resource(content={
            '@type': "https://schemas.eratos.ai/json/dataset",
            'name': f'{resKey} data',
            'newERN': [resKey],
            'dataDate': self._resource.date()
        }).save()
        ndata = nres.data()
        ndata.push_files(
            pushFiles,
            nodeID,
            **dProps,
        )
        # Write the dataset to the resource.
        self._resource.fetch()
        self._resource.set_prop('pndn', ndata.id())
        self._resource.save()

    def sync_objects(self, node, files, connector="Objects:Files:v1", connectorProps=None, chunkSize=None):
        """
        Sync files on a given node (Creating a new dataset if required).

        Parameters
        ----------
        node : str
            The node to sync the data to.
        files : arr
            The data filepaths to sync.
        connector : str
            A specific type of connector to use on the data. This is specific to the file type. (Default value is 'Objects:Files:v1')
        connectorProps : dict
            The properties for the connector. (Default value is None)
        chunkSize : int64
            The size to chunk the data by. (Default value is None)
        """
        # Validate parameters.
        node, files, connector, connectorProps, chunkSize = \
            self._check_pushsync_inputs(True, node, files, connector, connectorProps, chunkSize)
        # Sync the files.
        syncFiles, nodeID, dProps = self._translate_objects(node, files, connector, connectorProps, chunkSize, True)
        self._adapter._refresh_dn_token()
        eadp = OAPIAdapter(OAPIAccessTokenCreds(self._adapter._dn_token['oapk'], self._adapter._dn_token['oaps']), host="https://e-pn.io")
        resKey = str(self._resource.ern())
        nres = eadp.Resource(content={
            '@type': "https://schemas.eratos.ai/json/dataset",
            'name': f'{resKey} data',
            'newERN': [resKey],
            'dataDate': self._resource.date()
        }).save()
        ndata = nres.data()
        ndata.sync_files(
            syncFiles,
            nodeID,
            '/',
            **dProps,
        )
        # Write the dataset to the resource.
        self._resource.fetch()
        self._resource.set_prop('pndn', ndata.id())
        self._resource.save()

    def _translate_objects(self, node, files, connector, connectorProps, chunkSize, isSync):
        if isSync:
            retFiles = list([files[k]['path'][1:] for k in files.keys()])
        else:
            retFiles = []
            for k in files.keys():
                retFiles += [files[k]]
        try:
            if node.id() in _node_id_map:
                nodeID = _node_id_map[node.id()]
            else:
                nodeID = 'au-1.e-gn.io'
        except KeyError:
            nodeID = node.id()
            # raise ValueError(f'node {node} does not exist')
        dProps = {}
        if connector.lower() == 'objects:gridded:v1':
            dProps['geom'] = {}
            dProps['geom']['dimensions'] = copy.deepcopy(connectorProps['dimensions'])
            dProps['geom']['spaces'] = copy.deepcopy(connectorProps['spaces'])
            for sn in dProps['geom']['spaces'].keys():
                dProps['geom']['spaces'][sn]['type'] = 'structured'
            if isSync:
                dProps['geom']['variables'] = {}
                for vn in connectorProps['variables'].keys():
                    dProps['geom']['variables'][vn] = {}
                    for k in connectorProps['variables'][vn]:
                        if k == 'slices':
                            dProps['geom']['variables'][vn][k] = {}
                            for sn in connectorProps['variables'][vn][k]:
                                dProps['geom']['variables'][vn][k][files[sn]['path'][1:]] = copy.deepcopy(connectorProps['variables'][vn][k][sn])
                        else:
                            dProps['geom']['variables'][vn][k] = copy.deepcopy(connectorProps['variables'][vn][k])
            else:
                dProps['geom']['variables'] = copy.deepcopy(connectorProps['variables'])
        if isSync and chunkSize is not None:
            dProps['chunk_size'] = chunkSize
        return retFiles, nodeID, dProps

    def _check_pushsync_inputs(self, isSync, node, objects, connector, connectorProps, chunkSize):
        if type(node) is str:
            node = Ern(ern=node)
        elif type(node) is not Ern:
            raise TypeError('node should be a ern')
        if type(objects) is not dict:
            raise TypeError('objects should be a map[string]->string')
        syncPaths = {}
        for k in objects.keys():
            if type(k) is not str:
                raise TypeError(f'objects key {k} should be strings')
            if type(objects[k]) is str:
                objects[k] = {
                    'path': objects[k],
                    'mime': mimetypes.guess_type(objects[k])[0]
                }
            elif type(objects[k]) is dict:
                if 'path' not in objects[k] and 'content' not in objects[k]:
                    raise ValueError(f'expected path or content in objects for key {k}')
                elif 'path' in objects[k] and type(objects[k]['path']) is not str:
                    raise TypeError(f'expected path in objects for key {k} to be a string')
                elif 'content' in objects[k] and type(objects[k]['content']) is not bytes:
                    raise TypeError(f'expected content in objects for key {k} to be bytes')
                if 'mime' not in objects[k]:
                    if 'path' in objects[k]:
                        objects[k]['mime'] = mimetypes.guess_type(objects[k]['path'])[0]
                    else:
                        raise ValueError(f'mime property required with content for key {k} to be bytes')
                elif type(objects[k]['mime']) is not str:
                    raise TypeError(f'expected mime in objects for key {k} to be a string')
            else:
                raise TypeError(f'objects[{k}] should be a string or bytes or a map')
            if not isSync:
                if 'path' in objects[k] and not os.path.exists(objects[k]['path']):
                    raise ValueError(f'cannot find file for object {k}, it does not exist')
            else:
                if objects[k]['path'] in syncPaths:
                    raise ValueError(f'cannot sync to the same file in a given dataset, object {k}')
                syncPaths = objects[k]['path']
        if type(connector) is not str:
            raise TypeError('connector should be a string')
        connector = connector.lower()
        if connectorProps is None:
            connectorProps = {}
        return node, objects, connector, connectorProps, chunkSize

    def version(self):
        """
        Retrieves the version of the data.

        Returns
        -------
        str
            The version of the data object.
        """
        return self._version

    def gapi(self):
        """
        Retrieves the gridded API for a gridded geospatial dataset.

        Returns
        -------
        GSData | None
            The gridded API object for the dataset if exists.
        """
        if self._version is not None and 'Geom:v1' in self._version['fetchInterfaces']:
            return GSData(adapter=self._adapter, resource=self._resource, data=self)
        return None
