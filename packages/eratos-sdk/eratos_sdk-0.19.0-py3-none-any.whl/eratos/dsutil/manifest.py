import base64
import os
import hashlib
import io
import copy
import mimetypes
import csv
import json

from .hashtree import HashTree
from ..constants import GRIDDED_V1

def _calc_chunk_count(contentSize, chunkSize):
    chunkCount = contentSize // chunkSize
    if chunkCount == 0 or contentSize%chunkSize > 0:
        chunkCount += 1
    return chunkCount

def _fill_chunk_hash(content, chunkSize):
    left = chunkSize - len(content)
    if left > 0:
        content += b'\x00' * left
    return content

def _content_chunks(fp, contentSize, chunkSize):
    if contentSize == 0:
        yield _fill_chunk_hash(b'', chunkSize)
        return
    contentPos = 0
    while True:
        contentLeft = contentSize - contentPos
        if contentLeft >= chunkSize:
            yield fp.read(chunkSize)
            contentPos += chunkSize
        elif contentLeft > 0:
            chunk_content = fp.read(contentLeft)
            yield _fill_chunk_hash(chunk_content, chunkSize)
            contentPos += contentLeft
            break
        else:
            break

def _hash_chunk(data):
    h = hashlib.shake_256()
    h.update(data)
    return h.digest(HashTree.HashSize)

def _get_dir_names(path):
    subPaths = []
    while True:
        path = os.path.dirname(path)
        if path == "":
            break
        subPaths += [path]
    return subPaths

class Manifest:
    MAX_KEY_SIZE = 2048

    def __init__(self, fp=None, objects=None, connectorId=None, connectorProps=None, isSync=None):
        self.sortedKeys = []
        self.connectorId = connectorId
        self.connectorProps = connectorProps
        self.objects = {}
        self.isSync = isSync
        if fp is not None:
            self.load(fp)
        if objects is not None:
            self.merge_objects(objects)

    def merge_objects(self, objects):
        if type(objects) is not dict:
            raise TypeError('objects should be of type dict')
        for k in objects.keys():
            # Check the object is valid.
            if type(k) is not str:
                raise TypeError('keys in objects should be of type str')
            if len(k) > self.MAX_KEY_SIZE:
                raise ValueError('key "%s" in objects too long' % k)
            if type(objects[k]) is not dict:
                raise TypeError('key "%s" in objects should be of type dict' % k)
            if 'path' in objects[k] and 'content' in objects[k]:
                raise ValueError('key "%s" in objects has both "path" and "content" keys' % k)
            elif 'path' not in objects[k] and 'content' not in objects[k]:
                raise ValueError('key "%s" in objects is missing either "path" or "content" keys' % k)
            if 'mime' not in objects[k]:
                if 'path' not in objects[k]:
                    raise ValueError('key "%s" in objects has missing mime property which is required for non-file objects' % k)
                else:
                    mime = mimetypes.guess_type(objects[k]['path'], strict=False)[0]
                    if mime is None:
                        raise ValueError('could not determine mime for path "%s" for key "%s"' % (objects[k]['path'], k))
                    objects[k]['mime'] = mime

            # If not syncing calculate the Merkel root hash and insert into the manifests object list.
            if not self.isSync:
                if 'path' in objects[k]:
                    contentSize = os.stat(objects[k]['path']).st_size
                else:
                    content = objects[k]['content'] if type(objects[k]['content']) is bytes else objects[k]['content'].encode('utf-8')
                    contentSize = len(content)
                if 'chunk_size' in objects[k]:
                    chunkSize = objects[k]['chunk_size']
                elif 'chunkSize' in objects[k]:
                    chunkSize = objects[k]['chunkSize']
                else:
                    chunkSize = self.__calc_auto_chunk_size(contentSize)
                chunkCount = _calc_chunk_count(contentSize, chunkSize)
                ht = HashTree(chunkCount)
                if 'path' in objects[k]:
                    with open(objects[k]['path'], 'rb') as f:
                        chIdx = 0
                        for ch in _content_chunks(f, contentSize, chunkSize):
                            ht.update_leaf(chIdx, _hash_chunk(ch))
                            chIdx += 1
                else:
                    content = objects[k]['content'] if type(objects[k]['content']) is bytes else objects[k]['content'].encode('utf-8')
                    with io.BytesIO(content) as f:
                        chIdx = 0
                        for ch in _content_chunks(f, contentSize, chunkSize):
                            ht.update_leaf(chIdx, _hash_chunk(ch))
                            chIdx += 1
            else:
                if 'chunk_size' in objects[k]:
                    chunkSize = objects[k]['chunk_size']
                elif 'chunkSize' in objects[k]:
                    chunkSize = objects[k]['chunkSize']
                else:
                    chunkSize = -1
                contentSize = -1
            self.objects[k] = {
                'mime': objects[k]['mime'],
                'chunkSize': chunkSize,
                'contentSize': contentSize
            }
            if not self.isSync:
                self.objects[k]['hashTree'] = ht
                self.objects[k]['contentHashB32'] = ht.get_root(True)
            else:
                self.objects[k]['syncPath'] = objects[k]['path']
        self.sortedKeys = list(self.objects.keys())
        self.sortedKeys.sort()

    def remove_objects(self, keys):
        if type(keys) is not list:
            raise TypeError('keys should be of type list')
        for k in keys:
            if type(k) is not str:
                raise TypeError('elements of keys should be of type str')
            if k in self.objects:
                del self.objects[k]
            if self.connectorId == GRIDDED_V1.lower() and self.connectorProps is not None:
                for var in self.connectorProps['variables'].values():
                    if k in var['slices']:
                        del var['slices'][k]
                        
        self.sortedKeys = list(self.objects.keys())
        self.sortedKeys.sort()

    def rename_objects(self, keys: dict[str,str]):
        for old_file, new_file in keys.items():
            if old_file not in self.objects:
                raise KeyError(f"{old_file} does not exist")

            self.sortedKeys.remove(old_file)
            self.sortedKeys.append(new_file)

            self.objects[new_file] = self.objects.pop(old_file)
            if self.connectorId == GRIDDED_V1.lower() and self.connectorProps is not None:
                for var in self.connectorProps['variables'].values():
                    if old_file in var['slices']:
                        var['slices'][new_file] = var['slices'].pop(old_file)

        self.sortedKeys.sort()

    def clone(self):
        m = Manifest({})
        m.sortedKeys = copy.deepcopy(self.sortedKeys)
        m.objects = copy.deepcopy(self.objects)
        return m

    def save(self, fp):
        tinp = io.TextIOWrapper(fp, encoding='utf-8', write_through=True, newline='\n')
        csvWriter = csv.writer(tinp, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvWriter.writerow([self.connectorId])
        csvWriter.writerow([json.dumps(self.connectorProps)])
        for k in self.sortedKeys:
            obj = self.objects[k]
            csvWriter.writerow([
                k,
                'y' if self.isSync else 'n',
                obj['mime'],
                obj['contentSize'] if obj['contentSize'] >= 0 else '',
                obj['chunkSize'] if obj['chunkSize'] >= 0 else '',
                obj['syncPath'] if self.isSync else obj['contentHashB32']
            ])
        tinp.detach()

    def load(self, fp):
        self.connectorId = None
        self.connectorProps = None
        self.sortedKeys = []
        self.objects = {}
        tinp = io.TextIOWrapper(fp, encoding='utf-8')
        csvReader = csv.reader(tinp, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        line = 0
        for row in csvReader:
            if line == 0:
                if len(row) != 1:
                    raise Exception('expected 1 column for line 1 of a manifest')
                self.connectorId = row[0]
            elif line == 1:
                if len(row) != 1:
                    raise Exception('expected 1 column for line 2 of a manifest')
                self.connectorProps = json.loads(row[0])
            else:
                if len(row) != 6:
                    raise Exception('expected 6 columns for line >2 of a manifest')
                self.sortedKeys += [row[0]]
                self.objects[row[0]] = {
                    'isSync': row[1] == 'y',
                    'mime': row[2],
                    'contentSize': int(row[3]),
                    'chunkSize': int(row[4])
                }
                if self.objects[row[0]]['isSync']:
                    self.objects[row[0]]['syncPath'] = row[5]
                else:
                    self.objects[row[0]]['contentHashB32'] = row[5]
            line += 1

    def calc_hash(self):
        with io.BytesIO() as f:
            self.save(f)
            f.seek(0)
            h = hashlib.shake_256()
            data = f.read()
            h.update(data)
            return base64.b32encode(h.digest(HashTree.HashSize)).decode('ascii')


    def num_chunks(self, key):
        return _calc_chunk_count(self.objects[key]['contentSize'], self.objects[key]['chunkSize'])
    
    def objects_need_fetching(self, dir):
        if not os.path.exists(dir):
            return []
        keysToFetch = []
        for k in self.sortedKeys:
            chunkCount = _calc_chunk_count(self.objects[k]['contentSize'], self.objects[k]['chunkSize'])
            fetchItem = {
                'key': k,
                'chunkCount': chunkCount,
                'chunkSize': self.objects[k]['chunkSize'],
                'contentHashB32': self.objects[k]['contentHashB32']
            }
            objPath = os.path.join(dir, k)
            if not os.path.exists(objPath):
                keysToFetch += [fetchItem]
                continue
            ht = HashTree(chunkCount)
            with open(objPath, 'rb') as f:
                f.seek(0, io.SEEK_END)
                fileContentSize = f.tell()
                f.seek(0)
                if fileContentSize != self.objects[k]['contentSize']:
                    keysToFetch += [fetchItem]
                    continue
                chIdx = 0
                for ch in _content_chunks(f, fileContentSize, self.objects[k]['chunkSize']):
                    ht.update_leaf(chIdx, _hash_chunk(ch))
                    chIdx += 1
            rootHashB32 = ht.get_root(True)
            if rootHashB32 != self.objects[k]['contentHashB32']:
                keysToFetch += [fetchItem]
                continue
        return keysToFetch

    def get_directories(self):
        dirs = {}
        for key in self.sortedKeys:
            for dName in _get_dir_names(key):
                dirs[dName] = True
        return dirs

    def has_key(self, key):
        return key in self.objects

    def __calc_auto_chunk_size(self, contentSize):
        fileToHashSize = [
            [10485760, 262144],
            [20971520, 524288],
            [41943040, 1048576],
            [83886080, 2097152],
            [167772160, 4194304],
            [335544320, 8388608],
            [671088640, 16777216]
        ]
        for hs in fileToHashSize:
            if contentSize < hs[0]:
                return hs[1]
        return fileToHashSize[-1][1]


