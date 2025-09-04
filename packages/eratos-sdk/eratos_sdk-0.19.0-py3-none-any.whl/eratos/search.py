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

from urllib.parse import urlparse, parse_qsl
from json import dumps as jdump

from .ern import Ern

class SearchAdapter:
    """
    A Search Adapter class for use with Eratos.
    """
    def __init__(self, adapter, return_limit=-1, **kwargs):
        self._adapter = adapter
        self.reset(return_limit, **kwargs)
    
    def reset(self, return_limit=-1, **kwargs):
        """
        Resets the search adapter object to certain parameters.

        Parameters
        ----------
        return_limit : int
            A set return limit. (Default value is -1)
        kwargs : args
            Optional keyword arguments for a search.
            Arguments can include any of:
            | *query* = A string to query (ex. '*')
            | *limit* = An integer depicting the number of resources to limit the return (ex. 20)
            | *start* = An integer depicting the start index (ex. 0)
            | *exclude* = A list of ERNs to exclude.
            | *type* = A list of types to search for.
            | *excludeType* = A list of types to exclude from the search.
            | *owner* = A list of owner ERN's to search against.
            | *collections* = A list of collection ERN's to search against.
            | *facets* = A list of facets to search against.
            | *geom* = A geospatial geometry to search within.

        Raises
        ------
        TypeError
            If an unexpected type is set.
        ValueError
            If the value returned is not within an expected range.
        """
        self._return_limit = return_limit
        self._params = {
            'query': '*',
            'limit': 20,
            'start': 0,
            'exclude': [],
            'type': [],
            'excludeType': [],
            'owner': [],
            'collections': [],
            'facets': [],
            'scope': '',
            'geom': ''
        }
        if 'query' in kwargs:
            if type(kwargs['query']) is not str:
                raise TypeError('expected query to be a string')
            elif kwargs['query'] != '':
                self._params['query'] = kwargs['query']
        if 'limit' in kwargs:
            if type(kwargs['limit']) is not int:
                raise TypeError('expected limit to be an integer')
            elif kwargs['limit'] < 1 or kwargs['limit'] > 100:
                raise ValueError('expected limit to be between 1 and 100 (inclusive)')
            self._params['limit'] = kwargs['limit']
        if 'start' in kwargs:
            if type(kwargs['start']) is not int:
                raise TypeError('expected start to be an integer')
            elif kwargs['start'] < 0:
                raise ValueError('expected start to be greater or equal to 0')
            self._params['start'] = kwargs['start']
        if 'scope' in kwargs:
            if type(kwargs['scope']) is not str:
                raise TypeError('expected scope to be an string')
            self._params['scope'] = kwargs['scope']
        self._params['exclude'] = self._extract_str_arr('exclude', **kwargs)
        self._params['type'] = self._extract_str_arr('type', **kwargs)
        self._params['excludeType'] = self._extract_str_arr('excludeType', **kwargs)
        self._params['owner'] = self._extract_str_arr('owner', **kwargs)
        self._params['collections'] = self._extract_str_arr('collections', **kwargs)
        self._params['facets'] = self._extract_str_arr('facets', **kwargs)
        if 'geom' in kwargs:
            if type(kwargs['geom']) is not str:
                raise TypeError('expected geom to be a string')
            elif kwargs['geom'] != '':
                self._params['geom'] = kwargs['geom']
        for k in kwargs.keys():
            if not k.startswith('fn['):
                continue
            self._params[k] = self._extract_str_arr(k, **kwargs)
        self._found_count = 0
        self._facets = None
        self._count = None
        self._next_page = self._construct_fetch()

    def facets(self):
        """
        Retrieves the facets in a search.

        Returns
        -------
        Any | dict | None
            The facets if exists.
        """
        if self._facets is None:
            self._params['limit'] = 1
            self._perform_request()
        return self._facets

    def count(self):
        """
        Retrieves the number of items found in a search.

        Returns
        -------
        int | None
            The number of items found.
        """
        return self._count

    def search(self):
        """
        Performs the search.
        """
        while True:
            # If we need to read the next search page, do so.
            if self._next_page is not None:
                items = self._perform_request()
            else:
                break
            # Return this block of resources.
            for v in items:
                yield v
                self._found_count += 1
                # Check if we've returned the limit of items.
                if self._return_limit > 0 and self._found_count >= self._return_limit:
                    break

    def _extract_str_arr(self, key, **kwargs):
        res = []
        if key in kwargs:
            if type(kwargs[key]) is str:
                res += [kwargs[key]]
            elif type(kwargs[key]) is list:
                for v in kwargs[key]:
                    if type(v) is not str:
                        raise TypeError('%s value to be a string' % key)
                    res += [v]
            else:
                raise TypeError('%s must be either a string or list of strings' % key)
        return res

    def _construct_fetch(self):
        if self._return_limit > 0 and self._params['start']+self._params['limit'] > self._return_limit:
            self._params['limit'] = self._return_limit - self._params['start']
        if self._params['limit'] <= 0:
            return None
        content = {}
        for k in self._params.keys():
            if self._params[k] is None:
                continue
            if type(self._params[k]) is str and self._params[k] == '':
                continue
            if type(self._params[k]) is list and len(self._params[k]) == 0:
                continue
            if type(self._params[k]) is list:
                content[k] = ','.join(self._params[k])
            else:
                content[k] = self._params[k]
        
        return content

    def _perform_request(self):
        # Perform the query.
        data = self._adapter.request(Ern(type='tracker'), 'POST', '/search', data=jdump(self._next_page).encode('utf-8'))
        # Get the facets.
        self._facets = {} if 'facets' not in data else data['facets']
        # Wrap the results.
        self._count = int(data['count'])
        if 'nextPage' in data and data['nextPage'] is not None and data['nextPage'] != '':
            elems = urlparse(data['nextPage'])
            qp = dict(parse_qsl(elems.query, keep_blank_values=True))
            for k in qp.keys():
                if k in ['limit', 'start']:
                    self._params[k] = int(qp[k])
                else:
                    self._params[k] = qp[k]
            self._next_page = self._construct_fetch()
        else:
            self._next_page = None
        return list(self._adapter.Resource(content=res) for res in data['items'])
