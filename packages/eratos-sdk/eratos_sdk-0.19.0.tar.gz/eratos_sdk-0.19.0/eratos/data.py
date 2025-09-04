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

import gzip
import io
import logging
import mimetypes
import os
import pprint
from json import dumps as jdump

from eratos.dsutil.netcdf import gridded_geotime_netcdf_props

from .data_old import Data as OldGNData
from .dataversion import DataVersion
from .dsutil.manifest import Manifest
from .ern import Ern
from .errors import PolicyError
from .gsdata import GSData
from .util import iter_bitmap_ones
from .constants import GRIDDED_V1, FILES_V1

_logger = logging.getLogger(__name__)

class Data:

    """
    Gridded connector type
    """
    GRIDDED_V1 = GRIDDED_V1 

    """
    Files connector type
    """
    FILES_V1 = FILES_V1 

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
    
    def __init__(self, adapter, resource, ern=None, pndn=None):
        self._adapter = adapter
        self._resource = resource
        self._reset_content()
        if ern is not None:
            if type(ern) is str:
                self._ern = Ern(ern=ern)
            elif type(ern) is Ern:
                self._ern = ern
            else:
                raise TypeError('expected string or Ern for ern')
        if pndn is not None and self._adapter._check_dn_token():
            self._old_data = OldGNData(adapter, resource, id=pndn)
        else:
            self._old_data = None
        if self._ern is not None:
            self.fetch()

    def is_valid(self):
        """
        A utility function to determine the validity of a Data resource's fields.

        Returns
        -------
        bool
            True or False depending on the validity of a field.
        """
        oldDataValid = False
        if self._old_data is not None:
            oldDataValid = self._old_data.is_valid()
        if self._ern is None:
            return oldDataValid
        if self._resource is None:
            return oldDataValid
        if self._versions is None:
            return oldDataValid
        return True

    def id(self):
        """
        Retrieves the unique Eratos Resource Name (ERN) ID.

        DEPRECATED, use ern() instead.

        Returns
        -------
        str
            The unique Eratos Resource Name (ERN) ID of the current Resource.
        """
        if self._ern is None and self._old_data is not None:
            return self._old_data.id()
        return self._ern

    def ern(self):
        """
        Retrieves the unique Eratos Resource Name (ERN) ID.

        Returns
        -------
        str
            The unique Eratos Resource Name (ERN) ID of the current Resource.
        """
        return self._ern

    def resource(self):
        """
        Retrieves the Eratos resource associated with this dataset.

        Returns
        -------
        Resource
            The resource object.
        """
        return self._resource

    def fetch(self):
        """
        Fetches the data object.

        Returns
        -------
        Data
            The data object.
        """
        if self._old_data is not None:
            self._old_data.fetch()
        if self._ern is None:
            if self._old_data is not None:
                return # Don't return an error for old datasets.
            raise PolicyError('ern must be specified before fetching')
        jsonResp = self._adapter.request(self._ern.node_ern(), 'GET', '/datasets/%s' % self._ern.id())
        _logger.debug('fetch: fetched dataset: %s: %s' % (self._ern,pprint.pformat(jsonResp, width=1024*1024)))
        self._set_props_from_content(jsonResp, skip_check=True)
        return self

    def versions(self):
        """
        Retrieves the data versions if exists.

        Returns
        -------
        list[str]
            The versions that exist for a data object.
        """
        if self._ern is None and self._old_data is not None:
            return self._old_data.versions()
        return [] if self._versions is None else self._versions

    def version(self, id):
        """
        Fetches a version of the dataset given the id.

        Parameters
        ----------
        id : str
            ID of the dataset version to return.
        """
        if self._versions is None:
            return None
        for dsv in self._versions:
            if dsv.version_id == id:
                return dsv
        return None

    def latest(self, active=True):
        """
        Fetches the latest version of the dataset.

        Parameters
        ----------
        active : bool
            If True, returns the latest inavtive dataset.
        """
        if self._versions is None:
            return None
        if not active and len(self._versions) > 0:
            return self._versions[0]
        for dsv in self._versions:
            if dsv.is_active() is not None and dsv.is_active():
                return dsv
        return None

    def remove(self):
        """
        Removes a dataset.
        """
        if not self.is_valid():
            return
        self._adapter.request(self._ern.node_ern(), 'DELETE', '/datasets/%s' % (self._ern.id()))

    def remove_from_node(self, node):
        """
        Removes a dataset from the given node.

        Parameters
        ----------
        node : str | Ern
            The ERN of the node to remove the dataset from.
        """
        if type(node) is str:
            node = Ern(node)
        elif type(node) is not Ern:
            raise TypeError('node should be a str or Ern')
        if not self.is_valid():
            return
        self._adapter.request(self._ern.node_ern(), 'DELETE', '/datasets/%s/nodes/%s' % (self._ern.id(), node.id()))
        self.fetch()

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
            The node ern for which the data is available on.
        """
        if self._ern is None and self._old_data is not None:
            return self._old_data.content_available(allow_partial=allow_partial)
        elif self._ern is None:
            return None
        dsv = self.latest()
        if dsv is None:
            return None
        return dsv.get_first_active_node()

    def sync_file_list(self):
        """
        Fetches the latest file paths for synced files.
        """
        if self._ern is None and self._old_data is not None:
            return self._old_data.sync_file_list()
        elif self._ern is None:
            return []
        dsv = self.latest()
        if dsv is None or dsv._syncNode is None:
            return []
        manifest = dsv._pull_manifest(sync=True)
        for k in manifest.objects.keys():
            if not manifest.objects[k]['isSync']:
                continue
            yield manifest.objects[k]['syncPath']
        
    def pull_files(self, dest):
        """
        Validate and pull objects into a given directory.

        DEPRECATED: Use pull_objects instead.

        Parameters
        ----------
        dest : str
            The directory to output the data to.
        """
        self.pull_objects(destDir=dest)
        
    def pull_objects(self, destDir, removeUnknown=False):
        """
        Validate and pull objects into a given directory.

        Parameters
        ----------
        destDir : str
            The directory to output the data to.
        removeUnknown : bool
            If True, remove files in the destination directory that do not match an object in the dataset.
        """

        # If the data only exists on the old gn network, pull it from their.
        if self._ern is None and self._old_data is not None:
            return self._old_data.pull_objects(dest=destDir)

        # Create the dataset if the dataset exists and has an active latest version.
        if self._ern is None:
            raise Exception("no dataset found for the given resource")
        self.fetch()
        
        # Find the latest active version.
        dsVer = self._search_for_latest_active_version()
        if dsVer is None:
            raise Exception("no active version found for the given dataset")
        
        return dsVer.pull_objects(destDir, removeUnknown)

    def list_objects(self, version=None):
        """
        Gets the lists of objects from the latest active version.

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
        if self._ern is None and self._old_data is not None:
            return self._old_data.list_objects(version=version)

        dsv = self.latest()
        if dsv is None:
            return []

        return dsv.list_objects()

    def fetch_object(self, key, dest=".", stream_file: bool = False):
        """
        Fetch and object from the latest active version.

        Parameters
        ----------
        key : str
            The key of the data to fetch.
        dest : str
            The location to store the data. (Default is ".")
        stream_file : bool
            Whether to return a raw binary stream, if True dest will have no effect
        Raises
        ------
        AttributeError
            If invalid values exist.
        """
        if self._ern is None and self._old_data is not None:
            return self._old_data.fetch_object(key, dest=dest)

        dsv = self.latest()
        if dsv is None:
            raise AttributeError('no active version available with valid dataset')

        if stream_file:
            return dsv.fetch_streamed_object(key)

        return dsv.fetch_object(key, dest=dest)

    def push_objects(self, node, objects, connector=FILES_V1, connectorProps=None, chunkSize=None, keepOldVersions=False, forceChunkCheck=False):
        """
        Pushes data to a node.

        Parameters
        ----------
        node : str
            The node to push the data to.
        objects : dict
            The data files to push e.g. { "file.txt" : "./files/file.txt" }
        connector : str
            A specific type of connector to use on the data. This is specific to the file type. (Default value is 'Objects:Files:v1')
        connectorProps : dict
            The properties for the connector. (Default value is None)
        chunkSize : int64
            The size to chunk the data by. (Default value is None)
        keepOldVersion : bool
            If true, the old version of the dataset is kept on the gateway node.
        forceChunkCheck : bool
            If true, all files and chunks are checked (Default value is False)
        """
        # Validate parameters.
        node, objects, connector, connectorProps, chunkSize = \
            self._check_pushsync_inputs(False, node, objects, connector, connectorProps, chunkSize)

        # Create the manifest and calcualte the hash.
        _logger.debug('push_objects: calculating manifest for %s' % (self._ern))
        manifest = Manifest(objects=objects, connectorId=connector, connectorProps=connectorProps, isSync=False)

        manifestHash = manifest.calc_hash()
        _logger.debug('push_objects: calculated manifest hash %s: %s' % (self._ern, manifestHash))

        # Create the dataset if it doesn't exist and add the node to the dataset.
        self._check_exists()
        self._add_node(node)

        # Check if the manifest hash has the same value as the latest version,
        # if so use that version, if not create a new version.
        dsVer = self._search_for_version_with_hash(node, manifestHash, isSync=False, bailOnActive=True)
        if dsVer is None:
            _logger.debug('push_objects: creating new version for %s' % (self._ern))
            data = jdump({'manifestHash': manifestHash}).encode('utf-8')
            verResp = self._adapter.request(self._ern.node_ern(), 'POST', '/datasets/%s/versions' % (self._ern.id()), data=data)
            dsVer = DataVersion(self._adapter, self, content=verResp)
        elif dsVer._isActive:
            _logger.debug('push_objects: found active version with given hash: %s' % (dsVer.ern()))
            return dsVer
        else:
            _logger.debug('push_objects: found inactive version with given hash: %s' % (dsVer.ern()))

        updateKeys = manifest.sortedKeys

        # Setup the dataset on the gateway node.
        _logger.debug('push_objects: adding dataset version %s on %s' % (dsVer.ern(), node))

        # If not forcing a chunk update, check what files need to be pushed.
        self._push_objects(forceChunkCheck, dsVer, node, objects, manifest, connector, connectorProps,
                          keepOldVersions, updateKeys=updateKeys)

    def add_objects(self, node, objects, connector=FILES_V1, connectorPropsFn=None, chunkSize=None, keepOldVersions=False, forceChunkCheck=False):
        """
        Add data to a node. The dataset must exist on the node and new objects will be merged without removing existing objects on the node. This differs from
        push_objects() where by existing datasets will be fully replaced when using push_objects as opposed to being merged when using add_objects().

        Parameters
        ----------
        node : str
            The node to push the data to.
        objects : dict
            The data files to push e.g. { "file.txt": "./files/file.txt", ... }
        connector : str
            A specific type of connector to use on the data. This is specific to the file type. (Default value is 'Objects:Files:v1')
        connectorProps : dict
            Callback function to allow merging and manipulation of existing connector props (if present) and include new properties.
            Signature callbackPropsFn(existingProps: Optional[dict]) -> connectorProps: dict (Default value is None)
        chunkSize : int64
            The size to chunk the data by. (Default value is None)
        keepOldVersion : bool
            If true, the old version of the dataset is kept on the gateway node.
        forceChunkCheck : bool
            If true, all files and chunks are checked (Default value is False)
        """

        connectorProps = None

        if connectorPropsFn and connector == self.GRIDDED_V1:
            gapi = self.gapi()
            if gapi:
                connectorProps = connectorPropsFn(gapi.connectorProperties())
        print("connectorProps", connectorProps)


        # Validate parameters.
        node, objects, connector, connectorProps, chunkSize = \
            self._check_pushsync_inputs(False, node, objects, connector, connectorProps, chunkSize)

        self._check_exists()
        self._add_node(node)

        # Pull latest version.
        dsVer = self._search_for_latest_active_version()

        if dsVer is None:
            raise Exception("no active version found for the given dataset")

        # Pull the existing manifest
        manifest = dsVer._pull_manifest()

        # Merge objects.
        manifest.connectorId = connector
        manifest.connectorProps = connectorProps
        manifest.merge_objects(objects)
        updateKeys = objects.keys()
        manifestHash = manifest.calc_hash()

        _logger.debug('add_objects: creating new version for %s' % (self._ern))
        data = jdump({'manifestHash': manifestHash}).encode('utf-8')
        verResp = self._adapter.request(self._ern.node_ern(), 'POST', '/datasets/%s/versions' % (self._ern.id()), data=data)
        dsVer = DataVersion(self._adapter, self, content=verResp)

        # Setup the dataset on the gateway node.
        _logger.debug('add_objects: adding dataset version %s on %s' % (dsVer.ern(), node))

        self._push_objects(forceChunkCheck, dsVer, node, objects, manifest, connector, connectorProps, keepOldVersions, updateKeys=updateKeys)

    def rename_objects(self,node : str | Ern,files : dict[str, str]):
        """
        Rename objects on a node. The dataset must exist on the node and a new dataset version will be committed 
        without affecting the underlying file storage.

        Parameters
        ----------
        node : str
            The node to rename keys on. 
        files: dict
            A mapping { old_key: new_key, ... }
        """
        if isinstance(node, str):
            node = Ern(ern = node)
        dsVer = self._search_for_latest_active_version()
        if dsVer is None:
            raise Exception("no active version found for the given dataset")
        manifest = dsVer._pull_manifest()
        manifest.rename_objects(files)

        manifestHash = manifest.calc_hash()
        data = jdump({'manifestHash': manifestHash}).encode('utf-8')
        verResp = self._adapter.request(self._ern.node_ern(), 'POST', '/datasets/%s/versions' % (self._ern.id()), data=data)
        dsVer_new = DataVersion(self._adapter, self, content=verResp)
        self._adapter.request(node, 'POST', '/datasets/%s/%s/versions/%s' % (self._ern.node(), self._ern.id(), dsVer_new.version_id()))
        with io.BytesIO() as f:
            with gzip.GzipFile(fileobj=f, mode='w') as gf:
                manifest.save(gf)
            f.seek(0)
            headers = {'Content-Type': 'application/vnd.eratos.manifest', 'Content-Encoding': 'gzip'}
            self._adapter.request(node, 'PUT', '/datasets/%s/%s/versions/%s/manifest' % (self._ern.node(), self._ern.id(), dsVer_new.version_id()), headers=headers, data=f)

        self._adapter.request(node, 'GET', '/datasets/%s/%s/versions/%s' % (self._ern.node(), self._ern.id(), dsVer_new.version_id()))
        params = {
            'deleteOldVersions': 'true' 
        }
        self._adapter.request(node, 'POST', '/datasets/%s/%s/versions/%s/commit' % (self._ern.node(), self._ern.id(), dsVer_new.version_id()), params=params)
        verResp = self._adapter.request(self._ern.node_ern(), 'GET', '/datasets/%s/versions/%s' % (self._ern.id(), dsVer_new.version_id()))
        if not verResp['isActive']:
            raise Exception('dataset is not active after push')

    def replace_objects(self, node: str | Ern, files: dict[str,str],chunkSize = None, forceChunkCheck:bool = False):
        """
        Replace objects on a node. The dataset and existing keys must exist on the node. 

        Parameters
        ----------
        node : str
            The node to replace files on. 
        files: dict
            A mapping { old_key: "/path/to/new_file", ... }. The new keys in the dataset will be based on the basename of the path provided for each old key.
        forceChunkCheck : bool
            If true, all files and chunks are checked (Default value is False)
        """
        dsVer = self._search_for_latest_active_version()
        if dsVer is None:
            raise Exception("no active version found for the given dataset")
        manifest = dsVer._pull_manifest()
        renamer = {old: os.path.basename(new) for old,new in files.items()}
        fmap = {os.path.basename(f) : f for f in files.values()}
        manifest.rename_objects(renamer)
        node, objects, connector, connectorProps, chunkSize = \
            self._check_pushsync_inputs(False, node, fmap, manifest.connectorId, manifest.connectorProps, chunkSize)

        manifest.connectorProps = connectorProps
        manifest.merge_objects(objects)
        updateKeys = objects.keys()
        manifestHash = manifest.calc_hash()
        data = jdump({'manifestHash': manifestHash}).encode('utf-8')
        verResp = self._adapter.request(self._ern.node_ern(), 'POST', '/datasets/%s/versions' % (self._ern.id()), data=data)
        dsVer_new = DataVersion(self._adapter, self, content=verResp)
        self._adapter.request(node, 'POST', '/datasets/%s/%s/versions/%s' % (self._ern.node(), self._ern.id(), dsVer_new.version_id()))
        self._push_objects(forceChunkCheck, dsVer_new, node, objects, manifest, connector, connectorProps, keepOldVersions = False, updateKeys=updateKeys)

    def _push_objects(self, forceChunkCheck, dsVer, node, objects, manifest, connector, connectorProps, keepOldVersions, updateKeys):

        dsvResp = self._adapter.request(node, 'POST', '/datasets/%s/%s/versions/%s' % (self._ern.node(), self._ern.id(), dsVer.version_id()))
        if dsvResp['status'] == 'NoManifest':
            # Push the manifest to the gateway node.
            _logger.debug('push_objects: pushing manifest for dataset %s to %s' % (dsVer.ern(), node))
            with io.BytesIO() as f:
                with gzip.GzipFile(fileobj=f, mode='w') as gf:
                    manifest.save(gf)
                f.seek(0)
                headers = {'Content-Type': 'application/vnd.eratos.manifest', 'Content-Encoding': 'gzip'}
                self._adapter.request(node, 'PUT', '/datasets/%s/%s/versions/%s/manifest' % (self._ern.node(), self._ern.id(), dsVer.version_id()), headers=headers, data=f)
            # Refetch the dataset state.
            _logger.debug('push_objects: checking objects to update in dataset %s on %s' % (dsVer.ern(), node))
            dsvResp = self._adapter.request(node, 'GET', '/datasets/%s/%s/versions/%s' % (self._ern.node(), self._ern.id(), dsVer.version_id()))

        if not forceChunkCheck:
            if dsvResp['status'] == 'FullContent':
                updateKeys = []
            elif dsvResp['status'] == 'PartialContent':
                invalidFiles = list(iter_bitmap_ones(dsvResp['files']))
                updateKeys = list([manifest.sortedKeys[i] for i in invalidFiles])
            else:
                raise Exception(f'unknown status returned from node {dsvResp["status"]}')

        # Push the chunks of each object to the gateway node.
        _logger.debug('push_objects: %d objects to update in dataset %s on %s' % (len(updateKeys), dsVer.ern(), node))
        for key in updateKeys:
            _logger.debug('push_objects: checking object %s in dataset %s on %s' % (key, dsVer.ern(), node))
            params = {'key': key}
            objMeta = self._adapter.request(node, 'GET', '/datasets/%s/%s/versions/%s/objects' % (self._ern.node(), self._ern.id(), dsVer.version_id()), params=params)
            invalidChunks = list(iter_bitmap_ones(objMeta['chunks'])) if not forceChunkCheck else list(range(objMeta['chunks']['count']))
            _logger.debug('push_objects: found %d invalid chunks for object %s in dataset %s on %s' % (len(invalidChunks), key, dsVer.ern(), node))
            for chunk in invalidChunks:
                _logger.debug('push_objects: pushing chunk %d for object %s in dataset %s on %s' % (chunk, key, dsVer.ern(), node))
                # Read the chunk data.
                chunkPos = chunk * manifest.objects[key]['chunkSize']
                chunkSize = manifest.objects[key]['chunkSize']
                if chunkPos + chunkSize > manifest.objects[key]['contentSize']:
                    chunkSize = manifest.objects[key]['contentSize'] - chunkPos
                if 'path' in objects[key]:
                    with open(objects[key]['path'], 'rb') as f:
                        f.seek(chunkPos)
                        chunkData = f.read(chunkSize)
                else:
                    content = objects[key]['content'] if type(objects[key]['content']) is bytes else objects[key]['content'].encode('utf-8')
                    with io.BytesIO(content) as f:
                        f.seek(chunkPos)
                        chunkData = f.read(chunkSize)
                # Compress the chunk.
                with io.BytesIO() as f:
                    with gzip.GzipFile(fileobj=f, mode='w') as gf:
                        gf.write(chunkData)
                    f.seek(0)
                    chunkData = f.read()
                # Pipe to the gn.
                params = {'key': key, 'chunk': chunk}
                headers = {
                    'Content-Type': 'application/octet-stream',
                    'Content-Encoding': 'gzip',
                    'X-Chunk-Validation': manifest.objects[key]['hashTree'].save([chunk])
                }
                self._adapter.request(node, 'PUT', '/datasets/%s/%s/versions/%s/objects' % (self._ern.node(), self._ern.id(), dsVer.version_id()), params=params, headers=headers, data=chunkData)

        # Commit the version.
        params = {
            'deleteOldVersions': 'false' if keepOldVersions else 'true'
        }
        _logger.debug('push_objects: committing new version for %s' % (self._ern))
        self._adapter.request(node, 'POST', '/datasets/%s/%s/versions/%s/commit' % (self._ern.node(), self._ern.id(), dsVer.version_id()), params=params)

        # Verify the status.
        _logger.debug('push_objects: verifying new version for %s' % (self._ern))
        verResp = self._adapter.request(self._ern.node_ern(), 'GET', '/datasets/%s/versions/%s' % (self._ern.id(), dsVer.version_id()))
        if not verResp['isActive']:
            raise Exception('dataset is not active after push')

        # Push a copy to the old gn network.
        if self._old_data is not None and self._adapter._check_dn_token():
            self._old_data.push_objects(node, objects, connector=connector, connectorProps=connectorProps, chunkSize=chunkSize)

        return DataVersion(self._adapter, self, content=verResp)

    def sync_objects(self, node, objects, connector=FILES_V1, connectorProps=None, chunkSize=None, keepOldVersions=False, forceReSync=False):
        """
        Sync files on a given node (Creating a new dataset if required).

        Parameters
        ----------
        node : str
            The node to sync the data to.
        objects : arr
            The data filepaths to sync.
        connector : str
            A specific type of connector to use on the data. This is specific to the file type. (Default value is 'Objects:Files:v1')
        connectorProps : dict
            The properties for the connector. (Default value is None)
        chunkSize : int64
            The size to chunk the data by. (Default value is None)
        keepOldVersion : bool
            If true, the old version of the dataset is kept on the gateway node.
        forceReSync : bool
            If true, forces the files to be resynced.
        """
        # Validate parameters.
        node, objects, connector, connectorProps, chunkSize = \
            self._check_pushsync_inputs(True, node, objects, connector, connectorProps, chunkSize)

        # Create the manifest and calcualte the hash.
        _logger.debug('sync_objects: calculating manifest for %s' % (self._ern))
        manifest = Manifest(objects=objects, connectorId=connector, connectorProps=connectorProps, isSync=True)
        manifestHash = manifest.calc_hash()
        _logger.debug('sync_objects: calculated manifest hash %s: %s' % (self._ern, manifestHash))

        # Create the dataset if it doesn't exist and add the node to the dataset..
        self._check_exists()
        self._add_node(node)

        # Check if the manifest hash has the same value as the latest version,
        # if so use that version, if not create a new version.
        dsVer = self._search_for_version_with_hash(node, manifestHash, isSync=True, bailOnActive=True)
        if dsVer is None:
            _logger.debug('sync_objects: creating new version for %s' % (self._ern))
            data = jdump({'manifestHash':manifestHash,'syncNode':str(node)}).encode('utf-8')
            verResp = self._adapter.request(self._ern.node_ern(), 'POST', '/datasets/%s/versions' % (self._ern.id()), data=data)
            dsVer = DataVersion(self._adapter, self, content=verResp)
        elif dsVer._isActive:
            _logger.debug('sync_objects: found active version with given hash: %s' % (dsVer.ern()))
            return dsVer
        else:
            _logger.debug('sync_objects: found inactive version with given hash: %s' % (dsVer.ern()))

        # Setup the dataset on the gateway node.
        _logger.debug('sync_objects: adding dataset version %s on %s' % (dsVer.ern(), node))
        dsvResp = self._adapter.request(node, 'POST', '/datasets/%s/%s/versions/%s' % (self._ern.node(), self._ern.id(), dsVer.version_id()))
        if dsvResp['status'] == 'NoManifest':
            # Push the manifest to the gateway node.
            _logger.debug('sync_objects: pushing manifest for dataset %s to %s' % (dsVer.ern(), node))
            with io.BytesIO() as f:
                with gzip.GzipFile(fileobj=f, mode='w') as gf:
                    manifest.save(gf)
                f.seek(0)
                headers = {'Content-Type': 'application/vnd.eratos.manifest', 'Content-Encoding': 'gzip'}
                self._adapter.request(node, 'PUT', '/datasets/%s/%s/versions/%s/manifest' % (self._ern.node(), self._ern.id(), dsVer.version_id()), headers=headers, data=f)
            # Refetch the dataset state.
            _logger.debug('sync_objects: checking objects to update in dataset %s on %s' % (dsVer.ern(), node))
            dsvResp = self._adapter.request(node, 'GET', '/datasets/%s/%s/versions/%s' % (self._ern.node(), self._ern.id(), dsVer.version_id()))

        # Commit the version.
        params = {
            'deleteOldVersions': 'false' if keepOldVersions else 'true'
        }
        _logger.debug('sync_objects: committing new version for %s' % (self._ern))
        self._adapter.request(node, 'POST', '/datasets/%s/%s/versions/%s/commit' % (self._ern.node(), self._ern.id(), dsVer.version_id()), params=params)

        # Verify the status.
        _logger.debug('sync_objects: verifying new version for %s' % (self._ern))
        verResp = self._adapter.request(self._ern.node_ern(), 'GET', '/datasets/%s/versions/%s' % (self._ern.id(), dsVer.version_id()))
        if not verResp['isActive']:
            raise Exception('dataset is not active after push')

        # Push a copy to the old gn network.
        if self._old_data is not None and self._adapter._check_dn_token():
            self._old_data.sync_objects(node, objects, connector=connector, connectorProps=connectorProps, chunkSize=chunkSize)

        return DataVersion(self._adapter, self, content=verResp)

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
        if self._ern is None and self._old_data is not None:
            return self._old_data.gapi()

        dsv = self.latest()
        if dsv is None:
            return None
        return GSData(adapter=self._adapter, resource=self._resource, data=self, dataVersion=dsv)

    def _reset_content(self):
        self._ern = None
        self._createdAt = None
        self._updatedAt = None
        self._versions = None

    def _check_exists(self):
        if self._ern is not None:
            return
        _logger.debug('_check_exists: creating dataset for resource %s' % self._resource._ern)
        data = {"resource":str(self._resource._ern)}
        _logger.debug('_check_exists: creating dataset: %s' % pprint.pformat(data, width=1024*1024))
        jsonResp = self._adapter.request(self._resource._ern.node_ern(), 'POST', '/datasets', data=jdump(data).encode('utf-8'))
        _logger.debug('_check_exists: created dataset: %s' % pprint.pformat(jsonResp, width=1024*1024))
        self._set_props_from_content(jsonResp, skip_check=True)

    def _add_node(self, node: Ern):
        _logger.debug('_add_node: adding node %s for %s' % (node, self._ern))
        self._adapter.request(self._ern.node_ern(), 'PUT', '/datasets/%s/nodes/%s' % (self._ern.id(), node.id()))

    def _search_for_version_with_hash(self, node: Ern, hash: str, isSync: bool, bailOnActive: bool):
        if self._versions is None:
            return None
        for ver in self._versions:
            if ver._find_node(node) is None:
                return None
            if not isSync and ver._contentManifestHash == hash:
                return ver
            if isSync and ver._syncManifestHash == hash:
                return ver
            if bailOnActive and ver._isActive:
                return None
        return None
    
    def _search_for_latest_active_version(self):
        if self._versions is None:
            return None
        for ver in self._versions:
            if ver._isActive:
                return ver
        return None

    def _set_props_from_content(self, content, merge=False, skip_check=False):
        if not merge:
            self._createdAt = None
            self._updatedAt = None
            self._versions = None
        for k in content.keys():
            if k == 'id':
                if type(content[k]) is str:
                    ern = Ern(ern=content[k])
                elif type(content[k]) is Ern:
                    ern = content[k]
                else:
                    raise ValueError('expected string or ern for id')
                if not skip_check and self._ern is not None and self._ern.root() != ern.root():
                    raise ValueError('cannot replace dataset id with a different id')
                self._ern = ern
            elif k == 'resource':
                if type(content[k]) is str:
                    ern = Ern(ern=content[k])
                elif type(content[k]) is Ern:
                    ern = content[k]
                else:
                    raise ValueError('expected string or ern for resource')
                if not skip_check and self._resource is not None and self._resource.root() != ern.root():
                    raise ValueError('cannot replace dataset resource ern with a different ern')
                if self._resource is None or self._resource.ern() != ern:
                    self._resource = self._adapter.Resource(ern=ern)
            elif k == 'createdAt':
                if type(content[k]) is not str:
                    raise ValueError('expected string for createdAt')
                self._createdAt = content[k]
            elif k == 'updatedAt':
                if type(content[k]) is not str:
                    raise ValueError('expected string for updatedAt')
                self._updatedAt = content[k]
            elif k == 'versions':
                self._versions = [
                    DataVersion(self._adapter, self, content=dsv)
                    for dsv in content[k]
                ]

def scan_fs_objects(rootDir, exclude=[], useAbsPath=False):
    if useAbsPath:
        if os.path.isabs(rootDir):
            fsRoot = os.path.dirname(rootDir)
        else:
            fsRoot = os.getcwd()
    objs = {}
    for root, subdirs, files in os.walk(rootDir):
        for filename in files:
            path = os.path.join(root, filename)
            key = os.path.relpath(path, rootDir)
            if key in exclude:
                continue
            objs[key] = { 'path': os.path.join(fsRoot, path) if useAbsPath else path }
    return objs
