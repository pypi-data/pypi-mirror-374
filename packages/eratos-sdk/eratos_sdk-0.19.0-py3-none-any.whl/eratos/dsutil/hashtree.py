import os
import base64
import json
import hashlib

class HashTreeNoRootException(Exception):
    pass

class HashTreeNotValidException(Exception):
    pass

class HashTreeFloatingVertexException(Exception):
    pass

class HashTreeMissingVertexException(Exception):
    pass

class HashTreeLeafIndexOOBException(Exception):
    pass

class HashTreeInvalidVertexIDException(Exception):
    pass

class HashTree:
    """Implementation of a Merkel hash tree (supports full or partial trees)"""

    MAX_TREE_SIZE = 1 << 16
    HashSize  = 480 // 8
    PrependBytesLeaf = b'\x00'
    PrependBytesInternal = b'\x01'

    EmptyVerts = [
        b'\x12\xb2\xbb\x9e\x84\x8b\xb8\xaa\x15\x98\x28\x68\x28\xff\xcb\xb0\x96\xea\x2d\x2a\x92\x2c\x16\x33\x6d\x1d\x1a\x26\x69\x02',
        b'\xf5\x6e\xcd\x27\xe9\x82\x38\x65\x27\x89\x96\xf7\x51\x95\x2e\xa4\xc4\x97\x09\x1b\x1d\x86\x08\x38\xe2\x63\x03\x3e\x92\x9a',
        b'\x81\xf1\xec\xd4\x3e\x78\x33\xf6\x29\x0b\xdc\x55\xe3\xe2\xa6\xc4\xbd\x99\xcd\x57\xc2\x9d\xc1\x38\x02\x51\x79\xb4\x7d\x04',
        b'\x52\xbb\xdc\x8b\x21\x16\x31\xef\x63\x47\x2b\x67\xf7\x78\x93\x01\xc3\x33\x5b\x2b\x80\x4f\xe2\xeb\xfa\x81\x35\x36\x56\xc4',
        b'\x61\xf1\xc6\x02\x5a\x24\x9e\x32\xcb\x71\xce\xc2\x6e\x7f\xd2\xb5\x47\x6c\xc8\xb2\x15\x9b\x74\x15\xc6\xc7\x1d\xfc\x6e\x78',
        b'\x3d\x28\xa0\xad\xee\x78\x03\xf6\x57\xe9\xa3\xdf\x47\x6c\xe8\x8c\x41\xf5\xcd\x8a\xc1\x82\x33\x0c\xb8\xcf\x79\xb5\xf6\x24',
        b'\xf4\xb0\x90\x47\x6c\x06\x10\xea\x7a\xe4\xd1\x25\x68\x2b\xd5\x58\x27\x12\x28\x4b\x8c\x35\x2f\xf8\x7b\xc5\xb9\xea\x8a\x4a',
        b'\x81\xea\xae\xfc\xa4\x2c\xc2\x66\xca\xce\x4c\x15\x7d\x8b\x5b\x25\x65\x80\xec\x8a\xb5\xbb\x40\xa4\x14\x02\x08\x5f\x09\xde',
        b'\xf0\x25\x7d\xd1\xbd\xb0\x68\x6e\x31\x9e\x61\xb9\xaf\x2c\x55\x1f\xf6\x0f\xd2\xad\x11\x79\xb8\x29\x9e\x9b\x65\xb8\xfa\x56',
        b'\x46\x6c\x04\xba\xd6\x89\xf5\xd5\xed\xfa\xda\xb5\xed\xf6\x18\x0b\x7d\x38\x6c\x2e\xf8\x1d\xf9\xcb\xf2\x0e\x31\xfd\x61\xb5',
        b'\x33\x86\x53\xc1\x89\x66\xaf\xad\xc1\xed\xe0\x60\x48\x11\xc7\xf2\x16\xb7\x55\x55\xa0\x93\x49\xb1\xca\x1d\xab\x29\xa5\x5a',
        b'\xa7\x08\x75\x0b\x68\xbf\x20\xf6\x99\xe8\xd1\x30\xb7\xaf\xf1\x94\x49\x9f\x30\x05\xd0\xc3\xab\x9d\xa8\xd1\xc1\xaf\x59\x34',
        b'\xd1\xc3\x50\xc8\x72\x11\x1d\x51\x6e\xaa\x86\xb4\x9f\x86\xbf\x1b\xd2\x2a\x54\x87\x4e\x70\xa6\xbc\xc4\xbd\x15\x71\xd7\x1e',
        b'\x45\xae\x1f\x3b\x2d\x9c\x27\xa7\xcc\x81\xc4\x8a\xca\x82\xc6\x02\x63\x95\x59\x11\xad\x74\x02\x6c\xed\x91\x98\x1c\xfb\xb2',
        b'\x33\xe8\x68\x5a\x98\x1e\x74\x0c\x36\x87\x8e\xa3\x9c\xfd\x5a\xd2\x36\x99\xed\x7e\xff\x9f\x7a\xea\x9f\xaa\xf0\x6e\xc7\xd2',
        b'\xa9\xcb\x53\x9c\x0c\x7d\x9d\x01\x43\x9d\xa4\x36\x83\xcd\xf9\x80\x4a\x56\x17\x46\xb6\x01\x68\x05\x7b\x2a\x89\xd4\x98\xd6',
        b'\xc5\x5a\x60\xe6\x01\xae\x2b\x6a\xfc\x5c\xab\xb3\x03\x7c\x07\xf7\xb1\xde\x4a\xce\xcb\x0f\xb9\x9a\xd9\x69\x0b\xad\xfb\x43',
        b'\xc7\x11\x98\xd3\x78\xb8\xa4\x39\x3e\x5a\xd4\x69\x39\x7c\xc2\x92\xa4\xcb\xdc\x35\x81\x9c\x8d\x14\x6c\xe8\x39\x51\x98\x02',
        b'\x99\x1a\x97\xbf\x12\xb4\xed\xec\xd9\x37\x4b\xca\x95\x9e\xe3\x03\xa9\xeb\xbb\x5f\x9d\x3d\x5a\x1d\x95\x39\x7e\x86\x7a\x08',
        b'\x18\x8c\x99\x87\x60\x89\x93\x1f\x20\x32\x69\xb1\x4d\x2e\x18\xae\x48\x15\x0d\x78\xb1\x0b\x37\x9f\x6c\x18\x23\xde\x82\x7b',
        b'\x22\x8d\xf9\x30\x0f\x65\xe3\x5f\x2f\xbe\x89\x3e\x62\x12\x62\x98\xf1\xeb\x1a\x2b\xb9\x4b\x10\x88\x16\x5a\xb1\x77\xa5\xd8',
        b'\x3b\x2c\xb4\xb4\xb3\x4b\x9c\x6e\xaf\xb2\x58\x6d\x86\x53\x89\x9e\x44\xfe\x9d\x0b\x9e\x04\x56\xde\x4e\xda\x01\x9b\x73\xb8',
        b'\x4a\xfb\x2d\x4a\xf0\x9c\x10\x48\xd6\x72\x49\x2b\x47\x29\x87\x3c\x07\xec\x1b\x26\x61\x69\x6d\x3d\x6a\x6e\x95\x36\x49\xd1',
        b'\x7e\xd8\xa6\x10\x8b\x3a\x54\x4c\x90\xff\x79\x83\x67\xe7\x94\x51\xb4\x91\xb9\xd7\xcd\xcc\x74\x10\x87\x05\x14\x37\x6d\x8e',
        b'\x6b\xd1\x83\xa0\x30\x78\x3f\xb1\xfd\x4a\x12\xc0\x39\xd6\x7b\xbf\xeb\xf4\x17\x0b\x95\x8f\x45\xcb\x88\xf7\x46\xd1\x7b\x66',
        b'\x31\xf5\xc5\x75\x3f\x63\xf4\xfd\x44\xc6\x7c\x20\xaf\xd5\x20\x6b\x66\x0f\xdb\xbd\x7c\x8d\x60\xf2\xb8\x5c\x9a\x1e\xe8\x47',
        b'\x0b\x29\xb2\x3a\x27\x4b\xb6\x02\x33\xd9\x55\xa6\x69\xc5\x08\x03\x2c\x88\x3b\xfe\x62\x87\x60\xb1\xe5\xbb\x1d\x17\xed\x4a',
        b'\x14\x7e\xb4\x8e\x7f\x62\xf4\xb8\x9a\x06\x19\x64\x97\x72\x4d\xb9\x66\xae\xb7\x63\x46\xc9\xc2\x23\xcc\x82\xde\xeb\xc8\x01',
        b'\x3b\x8e\x56\x4d\x03\xf6\xbb\x30\x7a\x7a\xe9\xca\xbd\xf7\xb5\x6f\xd6\x37\x7d\xf1\xe3\xe9\x35\x75\xb0\x2b\xe0\x90\x36\xe1',
        b'\xb9\xf6\x59\xba\x74\x7b\x6f\xb9\x87\x0a\x3f\x39\x1f\x8f\xce\xb5\xc3\x11\xb2\x17\xea\xea\xed\xb8\xce\x2a\x4f\xf6\xaa\x78',
        b'\x8d\x80\x3b\xc9\x06\xc9\xba\x83\x23\x25\x07\x2b\x77\x8c\x33\xb8\x2a\x09\xaa\xf1\x5e\x7c\xa0\x80\xa1\x46\xb5\x87\x46\x43',
        b'\xcf\x14\xf8\x85\x9f\x91\x11\xb2\xac\x94\x43\x6b\x6c\x16\x9e\x55\xef\x60\xe6\x4c\x36\xfa\x37\xdd\xf7\xa0\xb6\x6d\x8b\x6a'
    ]

    def __calc_tree_depth(self, leafCount):
        if leafCount == 1:
            return 1
        depth = 0
        while leafCount > (1 << depth):
            depth += 1
        return depth + 1

    def __init__(self, leafCount):
        if type(leafCount) is not int:
            raise TypeError('leafCount shoud be of type int')
        if leafCount == 0:
            raise ValueError('leafCount should be > 0')
        if leafCount > self.MAX_TREE_SIZE:
            raise ValueError('leafCount should be <= %d' % self.MAX_TREE_SIZE)
        self.leafCount = leafCount
        self.depth = self.__calc_tree_depth(leafCount)
        self.verticies = {}
    
    def __calc_leaf_vertex_id(self, leafIdx):
        if type(leafIdx) is not int:
            raise TypeError('leafIdx shoud be of type int')
        rootID = 1 << (self.depth - 1)
        return rootID | (~leafIdx & (rootID - 1))

    def __is_vertex_id_a_leaf(self, id):
        if type(id) is not int:
            raise TypeError('id shoud be of type int')
        rootID = 1 << (self.depth - 1)
        return (id & rootID) == rootID

    def __calc_vertex_id_depth(self, id):
        if type(id) is not int:
            raise TypeError('id shoud be of type int')
        depth = 1
        while id > 1:
            id >>= 1
            depth += 1
        return depth

    def __is_vertex_id_in_tree(self, id):
        if type(id) is not int:
            raise TypeError('id shoud be of type int')
        if id == 1:
            return True
        elif self.__is_vertex_id_a_leaf(id):
            return id >= self.__calc_leaf_vertex_id(self.leafCount-1)
        else:
            # Check if the left most leaf node that is a decendant of this vertex exists in the tree.
            s = self.depth - self.__calc_vertex_id_depth(id)
            lml = (id << s) | ((1 << s) - 1)
            return lml >= self.__calc_leaf_vertex_id(self.leafCount-1)

    def __get_sibling_vertex_id(self, id):
        if type(id) is not int:
            raise TypeError('id shoud be of type int')
        return id ^ 1
    
    def __get_parent_vertex_id(self, id):
        if type(id) is not int:
            raise TypeError('id shoud be of type int')
        return id >> 1

    def __get_child_vertex_id(self, id, left):
        if type(id) is not int:
            raise TypeError('id shoud be of type int')
        if type(left) is not bool:
            raise TypeError('left shoud be of type bool')
        if left:
            return (id << 1) | 1
        else:
            return id << 1

    def validate_tree_structure(self, allowPartial):
        if type(allowPartial) is not bool:
            raise TypeError('allowPartial shoud be of type bool')
        if 1 not in self.verticies:
            raise HashTreeNoRootException
        for k in self.verticies.keys():
            if k!=1 and k>>1 not in self.verticies:
                raise HashTreeFloatingVertexException
        if not allowPartial:
            for i in range(0, self.leafCount):
                vertID = self.__calc_leaf_vertex_id(i)
                if vertID not in self.verticies:
                    raise HashTreeNotValidException('failed to validate full tree structure, missing tree leaf %d' % i)

    def load(self, cs, allowPartial=False):
        if type(cs) is bytes:
            content = cs.decode('ascii')
        elif type(cs) is str:
            content = cs
        else:
            raise TypeError('cs shoud be of type bytes or str')
        if type(allowPartial) is not bool:
            raise TypeError('allowPartial shoud be of type bool')
        n = 0
        for vert in content.split(';'):
            vertLine = vert.strip()
            if vertLine == "":
                continue
            vertElems = vertLine.split(':', 2)
            try:
                vertID = int(vertElems[0], 16)
            except:
                raise ValueError('cs item %d has invalid vertex id %s' % (n, vertElems[0]))
            if vertID == 0 or vertID >= (self.MAX_TREE_SIZE << 1):
                raise ValueError('cs item %d has vertex id %s that is greater than supported by the maximum tree size' % (n, vertElems[0]))
            if vertID in self.verticies:
                raise ValueError('cs item %d is a duplicate vertex id %s' % (n, vertElems[0]))
            try:
                vertHash = base64.b32decode(vertElems[1])
            except:
                raise ValueError('cs item %d has invalid hash %s' % (n, vertElems[1]))
            self.verticies[vertID] = vertHash
            n += 1
        self.validate_tree_structure(allowPartial)

    def save(self, leafIDs=None):
        if leafIDs is not None and type(leafIDs) is not list:
            raise TypeError('leafIDs shoud be of type list or None')
        if leafIDs is None:
            keys = self.verticies
        else:
            keys = {1:None}
            for lid in leafIDs:
                vid = self.__calc_leaf_vertex_id(lid)
                while vid > 1:
                    keys[vid] = None
                    keys[self.__get_sibling_vertex_id(vid)] = None
                    vid >>= 1
        sortedKeys = list(keys.keys())
        sortedKeys.sort()
        objs = []
        for k in sortedKeys:
            data = self.__get_vertex_data(k)
            objs += [hex(k)[2:] + ':' + base64.b32encode(data).decode('ascii')]
        return ';'.join(objs)

    def get_leaf_hash(self, leafIdx):
        return base64.b32encode(self.verticies[self.__calc_leaf_vertex_id(leafIdx)]).decode('ascii')

    def get_root(self, hex=False):
        if 1 not in self.verticies:
            raise HashTreeNoRootException
        if hex:
            return base64.b32encode(self.verticies[1]).decode('ascii').upper()
        return self.verticies[1]

    def compare_root(self, hash):
        if 1 not in self.verticies:
            raise HashTreeNoRootException
        return self.verticies[1] == hash

    def __hash_data(self, data, isLeaf):
        if type(data) is not bytes:
            raise TypeError('data shoud be of type bytes')
        if type(isLeaf) is not bool:
            raise TypeError('isLeaf shoud be of type bool')
        h = hashlib.shake_256()
        if isLeaf:
            h.update(self.PrependBytesLeaf)
        else:
            h.update(self.PrependBytesInternal)
        h.update(data)
        return h.digest(self.HashSize)

    def __get_vertex_data(self, id):
        if not self.__is_vertex_id_in_tree(id):
            leafDist = self.depth - self.__calc_vertex_id_depth(id)
            if leafDist >= len(self.EmptyVerts):
                raise Exception("tree depth too large, ran out of empty vertex definitions")
            return self.EmptyVerts[leafDist]
        elif id in self.verticies:
            return self.verticies[id]
        else:
            return None

    def __update_vertex(self, id, data):
        if type(id) is not int:
            raise TypeError('id shoud be of type int')
        if type(data) is not bytes:
            raise TypeError('data shoud be of type bytes')
        self.verticies[id] = self.__hash_data(data, self.__is_vertex_id_a_leaf(id))
        if id == 1:
            return
        sid = self.__get_sibling_vertex_id(id)
        sidData = self.__get_vertex_data(sid)
        if sidData is not None:
            if id > sid:
                comb = self.verticies[id] + sidData
            else:
                comb = sidData + self.verticies[id]
            self.__update_vertex(self.__get_parent_vertex_id(id), comb)

    def update_leaf(self, leafIdx, data):
        if type(leafIdx) is not int:
            raise TypeError('leafIdx shoud be of type int')
        if type(data) is not bytes:
            raise TypeError('data shoud be of type bytes')
        if leafIdx < 0 or leafIdx >= self.leafCount:
            raise ValueError('leafIdx of %d out of bounds' % leafIdx)
        self.__update_vertex(self.__calc_leaf_vertex_id(leafIdx),data)

    def __validate_vertex(self, id, data):
        if id not in self.verticies:
            raise HashTreeInvalidVertexIDException
        vertData = self.verticies[id]
        if self.__hash_data(data, self.__is_vertex_id_a_leaf(id)) != vertData:
            return False
        if id == 1:
            return True
        sid = self.__get_sibling_vertex_id(id)
        sidData = self.__get_vertex_data(sid)
        if sidData is None:
            raise HashTreeMissingVertexException
        if id > sid:
            comb = vertData + sidData
        else:
            comb = sidData + vertData
        return self.__validate_vertex(self.__get_parent_vertex_id(id), comb)
        
    def validate_leaf(self, leafIdx, data):
        if type(leafIdx) is not int:
            raise TypeError('leafIdx shoud be of type int')
        if type(data) is not bytes:
            raise TypeError('data shoud be of type bytes')
        if leafIdx < 0 or leafIdx >= self.leafCount:
            raise ValueError('leafIdx of %d out of bounds' % leafIdx)
        return self.__validate_vertex(self.__calc_leaf_vertex_id(leafIdx), data)

    def __validate_against_children(self, id):
        if type(id) is not int:
            raise TypeError('id shoud be of type int')
        if self.__is_vertex_id_a_leaf(id):
            return True
        vertData = self.verticies[id]
        if vertData is None:
            raise HashTreeInvalidVertexIDException
        leftChildID = self.__get_child_vertex_id(id, True)
        leftChildData = self.__get_vertex_data(leftChildID)
        if leftChildData is None:
            return HashTreeInvalidVertexIDException
        rightChildID = self.__get_child_vertex_id(id, False)
        rightChildData = self.__get_vertex_data(rightChildID)
        if rightChildData is None:
            return HashTreeInvalidVertexIDException
        vHash = self.__hash_data(leftChildData+rightChildData, False)
        if vHash != vertData:
            return False
        if not self.__validate_against_children(leftChildID):
            return False
        if self.__is_vertex_id_in_tree(rightChildID) and not self.__validate_against_children(rightChildID):
            return False
        return True

    def validate_tree(self):
        return self.__validate_against_children(1)
