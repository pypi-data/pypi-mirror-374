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
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import urllib

validAdapterProps = [
    "Query",
    "Type",
    "Count",
    "ExternalSources",
    "Location",
    "Relation",
    "Functions",
    "Start",
    "Lat",
    "Lon",
    "ExcludeType"
]

searchQueryMap = {
    'Query': 'q',
    'Start': 'start',
    'Type': 'type',
    'Relation': 'rel',
    'ExternalSources': 'extSource',
    'FromTime': 'fromTime',
    'ToTime': 'toTime',
    'Count': 'cnt',
    'Location': 'loc',
    'Lat': 'lat',
    'Lon': 'lon',
    'ExcludeType': 'excludeType',
}

def map_query(obj):
    nobj = {}
    for k in obj.keys():
        if k in searchQueryMap:
            nobj[searchQueryMap[k]] = obj[k]
        else:
            nobj[k] = obj[k]
    return nobj

class SearchAdapter:
    def __init__(self, adapter, props={}, limit=None):
        self.adapter = adapter
        self.limit = limit
        self.idx = 0
        self.reset()
        self.set_props(props)

    def reset(self):
        self.params = {
            "Query": "*",
            "Type": None,
            "ExternalSources": None,
            "Location": None,
            "Relation": None,
            "Lat": None,
            "Lon": None,
            "Functions": {},
            "Count": 20,
            "Start": 0,
            "ExcludeType": None
        }
        self.cur_idx = 0
        self.cur_resources = []
        self.next_page = 0
        self.count = 0
        self.idx = 0
        self.facets = {}

    def set_props(self, props):
        assert(isinstance(props, dict))
        for k in props.keys():
            if k not in validAdapterProps:
                raise Exception("%s is an invalid search property" % k)
            self.params[k] = props[k]

    def perform_request(self):
        # Create the query.
        query = {}
        for p in validAdapterProps:
            if p != "Functions" and self.params[p] is not None:
                query[p] = self.params[p]
        if "Query" not in query or query["Query"] is None:
            query["Query"] = "*"
        if self.params["Functions"] is not None:
            for k in self.params["Functions"].keys():
                query[k] = self.params["Functions"][k]
        # Perform the query.
        data = self.adapter.request("GET", "/search?" + urllib.parse.urlencode(map_query(query)))
        # Get the facets.
        self.facets = {} if "facets" not in data else data["facets"]
        # Wrap the results.
        self.count = data["count"]
        if "nextPage" in data:
            self.next_page = data["nextPage"]
            self.params["Start"] = self.next_page
        else:
            self.next_page = -1
        self.cur_idx = 0
        self.cur_resources = list(self.adapter.Resource(content=res) for res in data["resources"])
        return 

    def search(self):
        while True:
            # Check if we've returned the limit of items.
            if self.limit is not None and self.idx >= self.limit:
                break
            # If we need to read the next search page, do so.
            if self.cur_idx == len(self.cur_resources):
                if self.next_page < 0:
                    return
                else:
                    self.perform_request()
                    continue
            # Return the next resource.
            yield self.cur_resources[self.cur_idx]
            self.cur_idx += 1
            self.idx += 1
