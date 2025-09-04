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

import base64
import re
from urllib.parse import ParseResult, urlparse, urlencode, parse_qsl, quote, unquote

class Ern:
    """
    A class to interact with Eratos' unique Eratos Resource Names (ERNs).
    """
    _valid_types = [
        'meter',
        'tracker',
        'user',
        'node',
        'policy',
        'schema',
        'resource',
        'dataset'
    ]

    _types_req_id = [
        'user',
        'node',
        'policy',
        'schema',
        'resource',
        'dataset'
    ]

    _types_req_node = [
        'policy',
        'schema',
        'resource',
        'dataset'
    ]

    _res_common_id_re = re.compile(r'^([a-z]+[a-z0-9_-]*)(\.[a-z0-9]+[a-z0-9_-]*)+$')

    def __init__(self, ern: str=None, node: str=None, type: str=None, id: str=None, path: str='', query: dict={}):
        construct_ern, construct_parts = False, False
        if ern is not None:
            construct_ern = True
        if node is not None or type is not None:
            construct_parts = True
        if construct_ern and construct_parts:
            raise ValueError('cannot define ern with node or type in call')
        elif construct_ern:
            self._parse_ern(ern)
        elif construct_parts:
            self._node = node if node is not None else ''
            self._type = type
            self._id = id if id is not None else ''
            self._path = path
            self._query = query
            self._validate_ern()
        else:
            raise ValueError('must defined one of ern or node and type in call')

    def node(self):
        """
        Retrieves the node for a given Eratos Resource Name (ERN).

        Returns
        -------
        str
            The node ID for a given ERN.
        """
        return self._node

    def node_ern(self):
        """
        Retrieves the node's ERN object.

        Returns
        -------
        Ern | None
            The node ERN object for a given ERN.
        """
        if self._node is None:
            return None
        return Ern(type='node', id=self._node)

    def type(self):
        """
        Retrieves the type for the unique Eratos Resource Name (ERN).

        Returns
        -------
        str
            The type of the ERN object.
        """
        return self._type

    def id(self):
        """
        Retrieves the unique Eratos Resource Name (ERN) string ID.

        Returns
        -------
        str
            The unique Eratos Resource Name (ERN) ID of the current ERN object.
        """
        return self._id

    def path(self):
        """
        Retrieves the path related to the ERN object.

        Returns
        -------
        str
            The path of the ERN object.
        """
        return self._path
    
    def query(self):
        """
        Retrieves the query of the ERN object.

        Returns
        -------
        dict
            The dictionary of the ERN object.
        """
        return self._query

    def query_param(self, key):
        """
        Retrieves a query parameter of the ERN object.

        Returns
        -------
        str | None
            The value of the query paramter (None if missing).
        """
        return self._query[key] if key in self._query else None

    def __str__(self):
        return self._string()

    def __repr__(self):
        return self._string()

    def __eq__(self, other):
        if type(other) is str:
            other = Ern(ern=other)
        if self._node != other._node:
            return False
        if self._type != other._type:
            return False
        if self._id != other._id:
            return False
        if self._path != other._path:
            return False
        for k in self._query.keys():
            if k not in other._query or self._query[k] != other._query[k]:
                return False
        for k in other._query.keys():
            if k not in self._query or self._query[k] != other._query[k]:
                return False
        return True

    def root(self):
        """
        Retrieves the root ERN object.

        Returns
        -------
        Ern
            The root ERN object.
        """
        return Ern(node=self._node, type=self._type, id=self._id)

    def _string(self):
        if self._id is None or self._id == '':
            pr = ParseResult('', '', (self._type+'/'+quote(self._path)).strip('/'), '', urlencode(self._query, quote_via=quote), '')
            return 'ern:%s:%s' % (self._node, pr.geturl())
        else:
            pr = ParseResult('', '', (self._id+'/'+quote(self._path)).strip('/'), '', urlencode(self._query, quote_via=quote), '')
            return 'ern:%s:%s:%s' % (self._node, self._type, pr.geturl())

    def _parse_ern(self, ern: str):
        # ern:<node>:<type>:<id>
        elems = ern.split(':')
        if elems[0] != 'ern' or len(elems) < 3 or len(elems) > 4:
            raise ValueError('invalid ERN \'%s\', expected \'ern:<format>:<type>(:<id>)?(/<query>)?(?<query>)?\'' % ern)
        leqp = urlparse(elems[-1])
        pl = leqp.path.split('/', 2)
        netloc = pl[0]
        path = ''
        if len(pl) > 1:
            path = pl[1]
        self._node = elems[1]
        if len(elems) == 3:
            self._type = netloc
        else:
            self._type = elems[2]
        if self._type in self._types_req_id:
            self._id = netloc
        else:
            self._id = None
        self._path = unquote(path)
        self._query = dict(parse_qsl(leqp.query, keep_blank_values=True))
        self._validate_ern()

    def _validate_ern(self):
        if type(self._node) is not str:
            raise TypeError('invalid type for ERN node: %s' % type(self._node))
        if type(self._type) is not str:
            raise TypeError('invalid type for ERN type: %s' % type(self._type))
        if self._id is not None and type(self._id) is not str:
            raise TypeError('invalid type for ERN id: %s' % type(self._id))
        if type(self._path) is not str:
            raise TypeError('invalid type for ERN path: %s' % type(self._path))
        if type(self._query) is not dict:
            raise TypeError('invalid type for ERN query: %s' % type(self._query))
        if self._type not in self._valid_types:
            raise ValueError('invalid ERN type \'%s\', expected one of %s' % (self._type, '/'.join(self._valid_types)))
        if self._type in self._types_req_node and self._node == '':
            raise ValueError('invalid ERN \'%s\', expected node to be defined for type \'%s\'' % (self.__str__(), self._type))
        if self._type == 'policy' or self._type == 'dataset' or self._type == 'user':
            try:
                if self._id != '*':
                    base64.b32decode(self._id.encode('utf8'))
            except:
                raise ValueError('invalid ERN \'%s\', invalid id \'%s\'' % (self.__str__(), self._id))
        if self._type == 'resource':
            common_id = '.' in self._id
            if self._id != '*' and not common_id:
                try:
                    base64.b32decode(self._id.encode('utf8'))
                except:
                    raise ValueError('invalid ERN \'%s\', invalid id \'%s\'' % (self.__str__(), self._id))
            elif common_id and self._res_common_id_re.match(self._id) is None:
                raise ValueError('invalid ERN \'%s\', invalid common id \'%s\'' % (self.__str__(), self._id))
