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
import time
from typing import Generator
from urllib.parse import urlparse, parse_qs
from json import dumps as jdump

from .ern import Ern
from .oapi.creds import AccessTokenCreds as OAPIAccessTokenCreds
from .oapi.adapter import Adapter as OAPIAdapter

from .gsdata import GSData
from .errors import PolicyError

from .dsutil.hashtree import HashTree

_logger = logging.getLogger(__name__)

class DataVersionOnNode:
    """
    A class to interact with Eratos' datasets for a given version on a node.
    """
    @staticmethod
    def is_data_version_on_node(v):
        """
        A utility function to determine that the object is of type Data.

        Returns
        -------
        bool
            True or False depending on the type of the object.
        """
        return isinstance(v, DataVersionOnNode)

    def __init__(self, adapter, datasetVersion, content):
        self._adapter = adapter
        self._datasetVersion = datasetVersion
        self._node = None
        self._state = None
        self._set_props_from_content(content)

    def dataset_version(self):
        return self._datasetVersion

    def node(self):
        return self._node

    def state(self):
        return self._state

    def type_interface_http_endpoint(self, typeInterface='files:v1'):
        if self._state is None:
            return None
        if 'typeHTTPInterfaces' not in self._state:
            return None
        if typeInterface not in self._state['typeHTTPInterfaces']:
            return None
        return self._state['typeHTTPInterfaces'][typeInterface]

    def _set_props_from_content(self, content, merge=False, skip_check=False):
        if not merge:
            self._node = None
            self._state = None
        for k in content.keys():
            if k == 'version':
                if type(content[k]) is str:
                    ern = Ern(ern=content[k])
                elif type(content[k]) is Ern:
                    ern = content[k]
                else:
                    raise ValueError('expected string or ern for version')
                if self._datasetVersion is None or self._datasetVersion.ern() != ern:
                    self._datasetVersion = self._adapter.DataVersion(ern=ern)
            elif k == 'node':
                if type(content[k]) is str:
                    ern = Ern(ern=content[k])
                elif type(content[k]) is Ern:
                    ern = content[k]
                else:
                    raise ValueError('expected string or ern for node')
                self._node = ern
            elif k == 'state':
                if type(content[k]) is not dict:
                    raise ValueError('expected dict for state')
                self._state = content[k]


class DataVersion:
    """
    A class to interact with Eratos' datasets for a given version.
    """
    @staticmethod
    def is_data_version(v):
        """
        A utility function to determine that the object is of type Data.

        Returns
        -------
        bool
            True or False depending on the type of the object.
        """
        return isinstance(v, DataVersion)
    
    def __init__(self, adapter, dataset, ern=None, content=None):
        self._adapter = adapter
        self._dataset = dataset
        self._resource = dataset._resource
        self._reset_content()
        if ern is not None:
            if type(ern) is str:
                self._ern = Ern(ern=ern)
            elif type(ern) is Ern:
                self._ern = ern
            else:
                raise TypeError('expected string or Ern for ern')
            if self._ern.query_param("version") is None:
                raise TypeError('expected version parameter in ern')
        if self._ern is not None:
            self.fetch()
        elif content is not None:
            self._set_props_from_content(content)

    def ern(self):
        """
        Retrieves the unique Eratos Resource Name (ERN) ID.

        Returns
        -------
        str
            The unique Eratos Resource Name (ERN) ID of the current DatasetVersion.
        """
        return self._ern

    def version_id(self):
        return self._ern.query_param("version")

    def dataset(self):
        """
        Retrieves the Eratos dataset associated with this dataset version.

        Returns
        -------
        Resource
            The resource object.
        """
        return self._dataset

    def resource(self):
        """
        Retrieves the Eratos resource associated with this dataset version.

        Returns
        -------
        Resource
            The resource object.
        """
        return self._resource

    def get_node_state(self, node):
        for nvs in self._nodes:
            if nvs._node == node:
                return nvs
        return None

    def poll_sync(self, verbose=True, pollTime=1.0):
        def vprint(*args, **kwargs):
            if verbose:
                print(*args, **kwargs)
        while True:
            if self._syncNode is None:
                vprint('Not a sync dataset')
                break
            nvs = self.get_node_state(self._syncNode)
            if nvs is None:
                vprint('No sync node information')
                break
            if 'syncStatus' in nvs._state:
                if nvs._state['syncStatus'] == 'Partial':
                    vprint('Sync Progress: %.1f' % nvs._state['syncProgress'])
                elif nvs._state['syncStatus'] == 'Error':
                    vprint(f'Sync Error: {nvs._state["syncMessage"] if "syncMessage" in nvs._state else "unknown"}')
                    break
                elif nvs._state['syncStatus'] == 'Complete':
                    vprint('Sync Complete.')
                    break
            time.sleep(pollTime)
            self.fetch()

    def resync_objects(self, keys=None):
        if self._syncNode is None:
            return
        params = {}
        if keys is not None:
            params['key'] = keys
        self._adapter.request(self._syncNode, 'POST', '/datasets/%s/%s/versions/%s/resync' % (self._ern.node(), self._ern.id(), self._ern.query_param("version")), params=params)
        time.sleep(3) # Wait for a few seconds so the reset state is sent to the pn.
        self.fetch()

    def is_valid(self):
        if self._ern is None:
            return False
        if self._dataset is None:
            return False
        if self._isActive is None:
            return False
        return True
    
    def get_first_active_node(self):
        for nvs in self._nodes:
            if nvs._state is None:
                continue
            if not nvs._state.get('isNodeActive', False):
                continue
            if nvs._state.get('status', '') != 'FullContent':
                continue
            return nvs.node()
        return None

    def is_active(self):
        return self._isActive

    def fetch(self):
        """
        Fetches the data object.

        Returns
        -------
        Data
            The data object.
        """
        if self._ern is None:
            raise PolicyError('ern must be specified before fetching')
        json_resp = self._adapter.request(self._ern.node_ern(), 'GET', '/datasets/%s/versions/%s' % (self._ern.id(), self._ern.query_param("version")))
        self._set_props_from_content(json_resp, skip_check=True)

    def remove(self):
        if not self.is_active():
            return
        self._adapter.request(self._ern.node_ern(), 'DELETE', '/datasets/%s/versions/%s' % (self._ern.id(), self._ern.query_param("version")))

    def remove_from_node(self, node):
        if type(node) is str:
            node = Ern(node)
        elif type(node) is not Ern:
            raise TypeError('node should be a str or Ern')
        if not self.is_active():
            return
        self._adapter.request(self._ern.node_ern(), 'DELETE', '/datasets/%s/versions/%s/nodes/%s' % (self._ern.id(), self._ern.query_param("version"), node.id()))
        self.fetch()

    def pull_files(self, destDir, removeUnknown=False):
        """
        Pulls the dataset files into a given directory.
        DEPRECATED: Use pull_objects instead.

        Parameters
        ----------
        destDir : str
            The destination path to store the pulled data objects.
        removeUnknown : bool
            If True, remove files in the destination directory that do not match an object in the dataset.

        Raises
        ------
        AttributeError
            If invalid values exist.
        """
        return self.pull_objects(destDir, removeUnknown)

    def pull_objects(self, destDir, removeUnknown=False):
        """
        Pulls the dataset objects into a given directory.

        Parameters
        ----------
        destDir : str
            The destination path to store the pulled data objects.
        removeUnknown : bool
            If True, remove files in the destination directory that do not match an object in the dataset.
        """

        # Create the output directory.
        os.makedirs(destDir, exist_ok=True)

        # Find a node that contains the dataset.
        pullNode = self._find_valid_node()
        if pullNode is None:
            raise Exception('failed to get node with full content for the given dataset version')

        # Fetch the manifest.
        dsVerManifest = self._pull_manifest()

        # Check which objects need to be fetched by determining the merkel hash for the object.
        fetchObjs = dsVerManifest.objects_need_fetching(destDir)
        _logger.debug('pull_objects: pulling %d objects for dataset %s from %s' % (len(fetchObjs), self.ern(), pullNode))

        # Pull all the objects that need to be fetched.
        for fk in fetchObjs:
            dstFile = os.path.join(destDir, fk['key'])
            _logger.debug('pull_objects: pulling %s to %s for dataset %s from %s' % (fk['key'], dstFile, self.ern(), pullNode))
            os.makedirs(os.path.dirname(dstFile), exist_ok=True)
            with open(dstFile, 'wb') as f:
                f.truncate()
                for i in range(fk['chunkCount']):
                    _logger.debug('pull_objects: pulling chunk %d for %s in dataset %s from %s' % (i, fk['key'], self.ern(), pullNode))
                    # Fetch chunk and load partial hash tree.
                    params = {
                        'key': fk['key'],
                        'chunk': str(i)
                    }
                    chunk, req = self._adapter.request(pullNode, 'GET', '/datasets/%s/%s/versions/%s/objects' % (self._ern.node(), self._dataset._ern.id(), self.version_id()), params=params, retRequest=True)
                    vht = HashTree(fk['chunkCount'])
                    vht.load(req.headers['x-chunk-validation'], allowPartial=True)
                    if vht.get_root(True) != fk['contentHashB32']:
                        raise Exception('failed to validate root merkel tree for chunk %d in %s' % (i, fk['key']))
                    # Calculate the chunk hash.
                    h = hashlib.shake_256()
                    h.update(chunk)
                    left = fk['chunkSize'] - len(chunk)
                    if left > 0:
                        h.update(b'\x00' * left)
                    data = h.digest(HashTree.HashSize)
                    # Validate the chunk against the validation tree.
                    if not vht.validate_leaf(i, data):
                        raise Exception('failed to validate chunk %d in %s' % (i, fk['key']))
                    f.seek(i*fk['chunkSize'])
                    f.write(chunk)

        # Remove based on removeUnknown
        if removeUnknown:
            dirsInDataset = dsVerManifest.get_directories()
            dirsToRemove = []
            filesToRemove = []
            for root, dirs, files in os.walk(destDir):
                path = root.split(os.sep)
                for dName in dirs:
                    dPath = os.path.join(root, dName)
                    dRelPath = os.path.relpath(dPath, destDir)
                    if dRelPath not in dirsInDataset:
                        dirsToRemove += [dPath]
                for fName in files:
                    fPath = os.path.join(root, fName)
                    fRelPath = os.path.relpath(fPath, destDir)
                    if not dsVerManifest.has_key(fRelPath):
                        filesToRemove += [fPath]
            for fp in filesToRemove:
                _logger.debug('pull_objects: removing path %s' % (fp))
                os.remove(fp)
            dirsToRemove.sort(reverse=True)
            for dp in dirsToRemove:
                _logger.debug('pull_objects: removing path %s' % (dp))
                os.rmdir(dp)

    def list_objects(self):
        """
        Gets the lists of objects for a dataset version.

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
        if not self.is_valid():
            return []
        
        # Get a node with the correct type interface.
        pullNode = self._find_valid_node(typeInterface='files:v1')
        if pullNode is None:
            raise Exception('failed to get node with full content for the given dataset version')

        # Loop until no more results are given.
        _logger.debug('list_objects: listing files for dataset %s from %s' % (self.ern(), pullNode))
        params = { 'cmd': 'list', 'start': 0, 'limit': 1000 }
        while True:
            resp = self._adapter.request(pullNode, 'GET', '/datasets/%s/%s/versions/%s/tifaces/files:v1' % (self._ern.node(), self._dataset._ern.id(), self.version_id()), params=params)
            for item in resp['items']:
                yield item
            if 'next' not in resp or resp['next'] is None or resp['next'] == '':
                return
            params = parse_qs(urlparse(resp['next']).query)


    def _fetch_object(self, key: str):
        # Get the version to pull the data from.
        if not self.is_valid():
            return []
        
        # Get a node with the correct type interface.
        pullNode = self._find_valid_node(typeInterface='files:v1')
        if pullNode is None:
            raise Exception('failed to get node with full content for the given dataset version')

        # Stream the content to the file.
        _logger.debug('fetch_object: fetching file for object %s in dataset %s from %s' % (key, self.ern(), pullNode))
        params = { 'cmd': 'fetch', 'key': key }
        return self._adapter.request(pullNode, 'GET', '/datasets/%s/%s/versions/%s/tifaces/files:v1' % (self._ern.node(), self._dataset._ern.id(), self.version_id()), params=params, stream=True, retOnlyRequest=True)



    def fetch_streamed_object(self, key: str) -> Generator[bytes, None, None]:
        """
        Downloads data according to a specific key into a raw binary stream.

        Parameters
        ----------
        key : str
            The key of the data to fetch.

        Raises
        ------
        AttributeError
            If invalid values exist.

        Yields
        ------
        bytes
            Chunked bytes of the given data object
        """
        resp = self._fetch_object(key) 
        for chunk in resp.iter_content(chunk_size=8192):
            yield chunk


    def fetch_object(self, key: str, dest: str = ".") -> None:
        """
        Downloads data according to a specific key into a destination.

        Parameters
        ----------
        key : str
            The key of the data to fetch.
        dest : str
            The location to store the data. (Default is ".")

        Raises
        ------
        AttributeError
            If invalid values exist.
        """
        # Create the dest path if dest is a path.
        if os.path.exists(dest) and os.path.isdir(dest):
            dest = os.path.join(dest, key)
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        resp = self._fetch_object(key) 

        with open(dest, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)


    def _pull_manifest(self, sync=False):
        # Find a node that contains the dataset.
        pullNode = self._find_valid_node()
        if pullNode is None:
            raise Exception('failed to get node with full content for the given dataset version')

        # Fetch the manifest.
        _logger.debug('_pull_manifest: pulling manifest for dataset %s from %s' % (self.ern(), pullNode))
        params = { 'sync': 'true' if sync else 'false' }
        dsVerManifest = self._adapter.request(pullNode, 'GET', '/datasets/%s/%s/versions/%s/manifest' % (self._ern.node(), self._dataset._ern.id(), self.version_id()), params=params, stream = True)
        return dsVerManifest

    def _reset_content(self):
        self._ern = None
        self._createdAt = None
        self._createdBy = None
        self._comment = None
        self._isActive = None
        self._syncNode = None
        self._contentManifestHash = None
        self._syncManifestHash = None
        self._nodes = None

    def _set_props_from_content(self, content, merge=False, skip_check=False):
        if not merge:
            self._createdAt = None
            self._createdBy = None
            self._comment = None
            self._isActive = None
            self._syncNode = None
            self._contentManifestHash = None
            self._syncManifestHash = None
            self._nodes = None
        for k in content.keys():
            if k == 'version':
                if type(content[k]) is str:
                    ern = Ern(ern=content[k])
                elif type(content[k]) is Ern:
                    ern = content[k]
                else:
                    raise ValueError('expected string or ern for version')
                if not skip_check and self._ern is not None and self._ern != ern:
                    raise ValueError('cannot replace dataset version with a different version')
                self._ern = ern
                if self._dataset is None or self._dataset.ern() != ern.root():
                    self._dataset = self._adapter.Data(ern=ern.root(), resource=self._resource)
            elif k == 'resource':
                if type(content[k]) is str:
                    ern = Ern(ern=content[k])
                elif type(content[k]) is Ern:
                    ern = content[k]
                else:
                    raise ValueError('expected string or ern for @type')
                if not skip_check and self._resource is not None and self._resource._ern.root() != ern.root():
                    raise ValueError('cannot replace dataset resource ern with a different ern')
                if self._resource is None or self._resource.ern() != ern:
                    self._resource = self._adapter.Resource(ern=ern)
            elif k == 'createdAt':
                if type(content[k]) is not str:
                    raise ValueError('expected string for createdAt')
                self._createdAt = content[k]
            elif k == 'createdBy':
                if type(content[k]) is not str:
                    raise ValueError('expected string for createdBy')
                self._createdBy = content[k]
            elif k == 'comment':
                if type(content[k]) is not str:
                    raise ValueError('expected string for comment')
                self._comment = content[k]
            elif k == 'isActive':
                if type(content[k]) is not bool:
                    raise ValueError('expected bool for isActive')
                self._isActive = content[k]
            elif k == 'syncNode':
                if type(content[k]) is str:
                    ern = Ern(ern=content[k])
                elif type(content[k]) is Ern:
                    ern = content[k]
                else:
                    raise ValueError('expected string or ern for syncNode')
                self._syncNode = ern
            elif k == 'contentManifestHash':
                if type(content[k]) is not str:
                    raise ValueError('expected string for contentManifestHash')
                self._contentManifestHash = content[k]
            elif k == 'syncManifestHash':
                if type(content[k]) is not str:
                    raise ValueError('expected string for syncManifestHash')
                self._syncManifestHash = content[k]
            elif k == 'nodes':
                self._nodes = [
                    DataVersionOnNode(self._adapter, self, content=dsvon)
                    for dsvon in content[k]
                ]

    def _find_node(self, node):
        if type(node) is str:
            node = Ern(node)
        if type(node) is not Ern:
            raise TypeError('node should be an Ern or str')
        if self._nodes is not None:
            for nver in self._nodes:
                if nver._node == node:
                    return nver
        return None

    def _find_valid_node(self, typeInterface=None):
        # Find a node that contains the dataset.
        if self._nodes is not None:
            for nver in self._nodes:
                if nver._state is None:
                    continue
                elif nver._state['status'] != 'FullContent':
                    continue
                if typeInterface is None:
                    return nver.node()
                if 'typeHTTPInterfaces' not in nver._state:
                    continue
                if typeInterface.lower() not in nver._state['typeHTTPInterfaces']:
                    continue
                return nver.node()
        return None
