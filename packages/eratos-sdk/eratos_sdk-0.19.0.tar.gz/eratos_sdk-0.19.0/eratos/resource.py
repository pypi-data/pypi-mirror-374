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

import logging
import gzip
from json import dumps as jdump, loads as jload
from typing import Optional
from yaml import load as yload, dump as ydump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from collections import OrderedDict

from .ern import Ern
from .errors import ResourceError
from .util import move_prefix_to_new_format

from shapely import wkt
import numpy as np

_logger = logging.getLogger(__name__)

class Resource(object):
    """
    A class used to interact with Eratos' Resource objects.
    """
    @staticmethod
    def is_resource(v):
        """
        A utility function to determine that the object is of type Resource.

        Returns
        -------
        bool
            True or False depending on the type of the object.
        """
        return isinstance(v, Resource)

    def __init__(self, adapter, ern=None, yaml=None, json=None, content=None):
        self._adapter = adapter
        if ern is not None:
            if type(ern) is str:
                self._ern = Ern(ern=ern)
            elif type(ern) is Ern:
                self._ern = ern
            else:
                raise TypeError('expected string or Ern for ern')
        else:
            self._ern = None
        self._date = None
        self._type = None
        self._owner = None
        self._policy = None
        self._geo = None
        self._public = None
        self._data = None
        self._props = {}

        if self._ern is not None:
            self.fetch()
        elif json is not None:
            self._set_props_from_content(jload(json))
        elif yaml is not None:
            self._set_props_from_content(yload(yaml, Loader=Loader))
        elif content is not None:
            self._set_props_from_content(content)

    def is_valid(self):
        """
        A utility function to determine the validity of a resource's fields.

        Returns
        -------
        bool
            True or False depending on the validity of a field.
        """
        if self._ern is None or type(self._ern) is not Ern:
            return False
        if self._type is None or type(self._type) is not Ern:
            return False
        if self._owner is None or type(self._owner) is not Ern:
            return False
        if self._owner.type() == 'user':
            if self._policy is None or type(self._policy) is not Ern:
                return False
        if self._public is not None and type(self._public) is not bool:
            return False
        return True

    def ern(self):
        """
        Retrieves the unique Eratos Resource Name (ERN) for a resource.

        Returns
        -------
        Ern
            The unique Eratos Resource Name (ERN).
        """
        return self._ern

    def date(self):
        """
        Retrieves the date a resource was created.

        Returns
        -------
        str
            Date string.
        """
        return self._date

    def type(self):
        """
        Retrieves the type of a resource.

        Returns
        -------
        Ern
            The unique Eratos Resource Name (ERN) for the type of a resource.
        """
        return self._type

    def owner(self):
        """
        Retrieves the owner of a resource.

        Returns
        -------
        Ern
            The unique Eratos Resource Name (ERN) for the owner of a resource.
        """
        return self._owner
    
    def policy(self):
        """
        Retrieves the policy of a resource.

        Returns
        -------
        Ern
            The unique Eratos Resource Name (ERN) for the policy of a resource.
        """
        return self._adapter.Policy(ern=self._policy)

    def data(self):
        """
        Retrieves the underlying data of a resource.

        Returns
        -------
        Resource | Data | None
            The unique Eratos Resource Name (ERN) for the underlying data of a resource or the resource for the data if it exists.
        """
        
        if self._type == 'ern:e-pn.io:schema:block' and 'primary' in self._props:
            pr = self._adapter.Resource(ern=self._props['primary'])
            return pr.data()
        else:
            return self._adapter.Data(self, ern=self._data, pndn=self._props.get('pndn'))

    def has_geo(self):
        return self._geo is not None

    def     get_geo(self, detail='max', asVec=False):
        """
        Retrieves the geospatial geometry specified for a resource.

        Parameters
        ----------
        detail : str
            The detail level of a geospatial geometry. The value can be one of 'point', 'box' or 'max'. (Default value is 'max')
        asVec : bool
            Returns the geometry as a vector/array if set to True. (Default value is False)

        Raises
        ------
        ValueError
            If detail is not set to one of 'point', 'box' or 'max'.

        Returns
        -------
        arr | str
            The vector/array of coordinates if asVec is True, or the Well-Known Text formatted geometry string.
        """
        if self._geo is None:
            return None
        if detail not in ['point', 'box', 'max']:
            raise ValueError('detail should be one of point/box/max')
        wkt_data = self._adapter.request(self._ern.node_ern(), 'GET', '/resources/%s/geo?type=wkt&detail=%s' % (self._ern.id(), detail)).decode('utf-8')
        wkt_elem = wkt.loads(wkt_data.split(';')[-1])
        if asVec:
            if detail == 'point':
                return np.asarray(wkt_elem)
            elif detail == 'box':
                return np.asarray(list(zip(*wkt_elem.exterior.coords.xy)))
        else:
            return wkt_elem

    def set_geo(self, wkt):
        """
        Sets the geospatial geometry for a given resource.

        Parameters
        ----------
        wkt : str
            Well-Known Text formatted geometry string.
        """
        self._geo = wkt
    
    def public(self):
        """
        Retrieves whether a given resource is public or not.

        Returns
        -------
        bool
            True or False.
        """
        return False if self._public is None else self._public

    def props(self):
        """
        Retrieves the properties of a given resource.

        Returns
        -------
        dict
            A dictionary of the properties.
        """
        return self._props

    def prop(self, key, default=None):
        """
        Retrieves a property of a given resource corresponding to a key name.

        Parameters
        ----------
        key : str
            The property name/key.
        default : str
            A default to return if the property is not found. (Default value is None)

        Returns
        -------
        Any
            The value of a given property for a resource.
        """
        if key in self._props:
            return self._props[key]
        else:
            return default

    def set_prop(self, key, value):
        """
        Adds a property to a given resource.

        Parameters
        ----------
        key : str
            The key/name of the property to set.
        value : str
            The value of the property to set.
        """
        self._set_props_from_content({key: value}, merge=True)

    def prop_path(self, propPath, default=None, sep=None):
        """
        Gets the value of a property for a given resource.

        Parameters
        ----------
        propPath : str
            The key/name of the property to get.
        default : str
            A default to return if the property is not found. (Default value is None)
        sep : str
            A separator to use in returning the property's values if more than one is found. (Default value is None)
        
        Returns
        -------
        vals
            The value(s) found for of a given property in a resource.
        """
        vals = list(self._prop_path_impl(self.props(), propPath, default=default))
        if len(vals) > 1:
            if sep is not None:
                return sep.join([str(v) for v in vals])
            else:
                return vals
        return vals[0]

    def _prop_path_impl(self, obj, propPath, default=None):
        if type(obj) is str and obj.startswith("ern:"):
            try:
                ern = Ern(ern=obj)
                if ern.type() != 'resource':
                    return default
                res = self._adapter.Resource(ern=ern)
                yield from res._prop_path_impl(res.props(), propPath, default=default)
            except (TypeError, ValueError):
                yield default
        elif type(obj) is list:
            for o in obj:
                yield from self._prop_path_impl(o, propPath, default=default)
        elif type(obj) is dict:
            elems = propPath.strip().split(".")
            if len(elems) == 1:
                if elems[0] == '@id':
                    yield str(self.ern())
                elif elems[0] == '@type':
                    yield str(self.type())
                elif elems[0] == '@date':
                    yield self.date()
                elif elems[0] == '@owner':
                    yield self.owner()
                elif elems[0] == '@policy':
                    yield self.policy()
                elif elems[0] == '@geo':
                    yield self.get_geo()
                elif elems[0] in obj:
                    yield obj[elems[0]]
                else:
                    yield default
            elif elems[0] in obj:
                yield from self._prop_path_impl(obj[elems[0]], ".".join(elems[1:]), default=default)
            else:
                yield default
        else:
            yield default

    def __repr__(self):
        return '%s (%s)' % (self._ern, self._type)

    def __str__(self):
        return '%s (%s)' % (self._ern, self._type)

    def fetch(self):
        """
        Gets a resource.

        Raises
        ------
        ResourceError
            If the @id has not been set for the resource. (The resource is missing it's unique Eratos Resource Name (ERN).)

        Returns
        -------
        Resource
            The Eratos Resource object.
        """
        if self._ern is None:
            raise ResourceError('@id must be specified before fetching')
        json_resp = self._adapter.request(self._ern.node_ern(), 'GET', '/resources/%s' % self._ern.id())
        self._set_props_from_content(json_resp, skip_check=True)
        return self
    
    def transfer_owner(self, ern=None, email=None, space_params=None):
        """
        Transfers a resource to another user. Special consideration for space resources.
        For space resources, the space_params argument  must be specified.

        Parameters
        ----------
        ern : str
            The ern of the user (may not be specified with email).
        email : str
            The email of the user (may not be specified with ern).
        space_params: dict
            Optional.
            Below is the expected shape of the argument.

            { "spaceAction": { "leaveSpace": <bool>, "newRole": <str> }}

            If the resource being acted upon is of type ern:e-pn.io:schema:space, and the outgoing owner chooses to
            leave the space, spaceAction.leaveSpace will be set to True by default. In this case, space_params need
            not be specified and can be called with transfer_owner(email="") or transfer_owner(ern="").

            If the resource being acted upon is of type ern:e-pn.io:schema:space and the outgoing owner chooses to
            remain in the space, spaceAction.leaveSpace must equal False and spaceAction.newRole must be "Admin" or
            "Contributor" or "Member".

        Raises
        ------
        ResourceError
            If the resource cannot be acted upon.
        """
        params = dict()
        if ern is None and email is None:
            raise ValueError('either ern or email must be specified')
        elif ern is not None:
            if type(ern) is str:
                ern = Ern(ern)
            if type(ern) is not Ern:
                raise TypeError('ern should either be a str or Ern')
            params = {'ern': str(ern)}
        elif email is not None:
            if type(email) is not str:
                raise TypeError('email should be a str')
            params = {'email': email}

        if self._type == 'ern:e-pn.io:schema:space':
            if space_params is None:
                space_params = {
                    'spaceAction': {
                        'leaveSpace': True
                    }
                }
            params = {**params, **space_params}
        elif space_params is not None:
            raise KeyError("space_params can only be provided for resources that are of type ern:e-pn.io:schema:space")

        return self.perform_action('TransferOwner', params)

    def save(self, target_node: Ern=None):
        """
        Posts a resource.

        Parameters
        ----------
        target_node : Ern
            The unique Eratos Resource Name (ERN) for the node to post to. (Default value is None)

        Returns
        -------
        Resource
            The Eratos Resource object.
        """
        if self._ern is not None:
            target_node = self._ern.node_ern()
        elif target_node is None:
            target_node = self._adapter.master_pn()
        json_resp = self._adapter.request(target_node, 'POST', '/resources', data=self.json(for_push=True).encode('utf-8'))
        self._set_props_from_content(json_resp, skip_check=True)
        return self

    def remove(self):
        """
        Deletes a resource.

        Raises
        ------
        ResourceError
            If the resource cannot be removed.

        Returns
        -------
        Resource
            The Eratos Resource object.
        """
        if not self.is_valid():
            raise ResourceError('resource not in a state to remove')
        self._adapter.request(self._ern.node_ern(), 'DELETE', '/resources/%s' % self._ern.id())
        self._set_props_from_content({}, skip_check=True)
        return self

    def perform_action(self, action, params: Optional[dict] = None):
        """
        Performs an action on a resource.

        Parameters
        ----------
        action : str
            The action to perform.
        params : str
            Parameters for the action to perform.

        Raises
        ------
        ResourceError
            If the resource cannot be acted upon.

        Returns
        -------
        json
            The json response object from the performed action.
        """
        if not self.is_valid():
            raise ResourceError('resource not in a state to perform an action')
        for_action = {"action": action}
        if params:
            for_action["parameters"] = params

        json_resp = self._adapter.request(self._ern.node_ern(), 'POST', '/resources/%s/action' % self._ern.id(), data=jdump(for_action).encode('utf-8'))
        return json_resp

    def authactions(self):
        """
        Gets the authorized actions available for a resource.

        Raises
        ------
        ResourceError
            If authorized actions cannot be retrieved for the given resource.

        Returns
        -------
        json
            The json response object from the performed action.
        """
        if not self.is_valid():
            raise ResourceError('resource not in a state to get authactions')
        json_resp = self._adapter.request(self._ern.node_ern(), 'GET', '/resources/%s/authactions' % self._ern.id())
        return json_resp

    def _set_props_from_content(self, content, merge=False, skip_check=False):
        if not merge:
            self._props = {}
        for k in content.keys():
            if k == '@id':
                if type(content[k]) is str:
                    ern = Ern(ern=content[k])
                elif type(content[k]) is Ern:
                    ern = content[k]
                else:
                    raise ValueError('expected string or ern for @id')
                if not skip_check and self._ern is not None and self._ern.root() != ern.root():
                    raise ValueError('cannot replace resource id with a different id')
                self._ern = ern
            elif k == '@type':
                if type(content[k]) is str:
                    ern = Ern(ern=content[k])
                elif type(content[k]) is Ern:
                    ern = content[k]
                else:
                    raise ValueError('expected string or ern for @type')
                if not skip_check and self._type is not None and self._type.root() != ern.root():
                    raise ValueError('cannot replace resource type with a different type')
                self._type = ern
            elif k == '@owner':
                if type(content[k]) is str:
                    ern = Ern(ern=content[k])
                elif type(content[k]) is Ern:
                    ern = content[k]
                else:
                    raise ValueError('expected string or ern for @owner')
                if not skip_check and self._owner is not None and self._owner.root() != ern.root():
                    raise ValueError('cannot replace resource owner with a different owner')
                self._owner = ern
            elif k == '@policy':
                if type(content[k]) is str:
                    ern = Ern(ern=content[k])
                elif type(content[k]) is Ern:
                    ern = content[k]
                else:
                    raise ValueError('expected string or ern for @policy')
                if not skip_check and self._policy is not None and self._policy.root() != ern.root():
                    raise ValueError('cannot replace resource policy with a different policy')
                self._policy = ern
            elif k == '@data':
                if type(content[k]) is str:
                    ern = Ern(ern=content[k])
                elif type(content[k]) is Ern:
                    ern = content[k]
                else:
                    raise ValueError('expected string or ern for @data')
                if not skip_check and self._data is not None and self._data.root() != ern.root():
                    raise ValueError('cannot replace resource data with a different data')
                self._data = ern
            elif k == '@date':
                if type(content[k]) is not str:
                    raise ValueError('expected string for @date')
                self._date = content[k]
            elif k == '@geo':
                if type(content[k]) is not str:
                    raise ValueError('expected string for @geo')
                self._geo = content[k]
            elif k == '@public':
                if type(content[k]) is not bool:
                    raise ValueError('expected bool for @public')
                self._public = content[k]
            elif not skip_check and k.startswith('@'):
                raise ValueError('unknown special property \'%s\'' % k)
            else:
                self._props[k] = content[k]

    def yaml_set(self, yaml, merge=False):
        """
        Set a resource's properties via yaml.

        Parameters
        ----------
        yaml : str
            The yaml str object containing the resource's properties.
        merge : bool
            True to merge the content with an existing Resource, or False to overwrite. (Default value is False)
        """
        return self._set_props_from_content(yload(yaml, Loader=Loader), merge)

    def json_set(self, obj, merge=False):
        """
        Set a resource's properties via json.

        Parameters
        ----------
        obj : dict
            The json object containing the resource's properties.
        merge : bool
            True to merge the content with an existing Resource, or False to overwrite. (Default value is False)
        """
        return self._set_props_from_content(jload(obj), merge)

    def _construct_ordered_content(self, for_push=False):
        content = {}
        if self._ern is not None:
            content['@id'] = str(self._ern)
        if self._type is not None:
            content['@type'] = str(self._type)
        if self._owner is not None:
            content['@owner'] = str(self._owner)
        if self._policy is not None:
            content['@policy'] = str(self._policy)
        if self._data is not None:
            content['@data'] = str(self._data)
        if self._geo is not None:
            content['@geo'] = str(self._geo)
        if self._public is not None:
            content['@public'] = bool(self._public)
        for k in self._props.keys():
            if for_push and '@' in k:
                continue
            content[k] = self._props[k]
        return content

    def json(self, for_push=False, **kwargs):
        """
        Creates a resource's properties in json.

        Parameters
        ----------
        for_push : bool
            A bool to set whether the object is to be pushed. (Default value is False)
        kwargs : args
            Optional keyword property arguments to add to the Resource object.

        Returns
        -------
        dict
            The json dictionary object containing the Resource properties.
        """
        return jdump(self._construct_ordered_content(for_push), **kwargs)
    
    def yaml(self, **kwargs):
        """
        Creates a resource's properties in yaml.

        Parameters
        ----------
        kwargs : args
            Optional keyword property arguments to add to the Resource object.

        Returns
        -------
        str
            The yaml string object containing the Resource properties.
        """
        return ydump(self._construct_ordered_content(), Dumper=Dumper, sort_keys=False, **kwargs).strip()
