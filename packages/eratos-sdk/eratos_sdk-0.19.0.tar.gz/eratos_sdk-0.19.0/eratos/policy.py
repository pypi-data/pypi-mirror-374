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
from json import dumps as jdump, loads as jload
from yaml import load as yload, dump as ydump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .ern import Ern
from .errors import PolicyError, ResourceError
from .util import move_prefix_to_new_format

_logger = logging.getLogger(__name__)

class Policy:
    """
    A class used to interact with the Policy attached to Eratos' Resources and Nodes.
    """
    TYPE_NODE = 'Node'
    TYPE_RESOURCE = 'Resource'

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
        A utility function to determine the validity of a policy's fields.

        Returns
        -------
        bool
            True or False depending on the validity of a field.
        """
        if self._ern is None or type(self._ern) is not Ern:
            return False
        if self._type is None or type(self._type) is not Ern:
            return False
        return True

    def ern(self):
        """
        Retrieves the unique Eratos Resource Name (ERN) for a policy.

        Returns
        -------
        Ern
            The unique Eratos Resource Name (ERN).
        """
        return self._ern

    def date(self):
        """
        Retrieves the date a policy was created.

        Returns
        -------
        str
            Date string.
        """
        return self._date

    def type(self):
        """
        Retrieves the type of entities a policy adheres to.

        Returns
        -------
        str | None
            The policy type if exists.
        """
        if 'type' in self._props:
            return self._props['type']
        else:
            return None

    def for_entity(self):
        """
        Retrieves the unique Eratos Resource Name (ERN) of the entity a policy applies to.

        Returns
        -------
        Ern | None
            The unique Eratos Resource Name (ERN) of the entity if exists.
        """
        if 'for' in self._props:
            return self._props['for']
        else:
            return None

    def rules(self):
        """
        Retrieves the set of rules that apply to a policy.

        Returns
        -------
        list[dict]
            The policy rules. (Can be an empty list)
        """
        if 'rules' in self._props:
            return self._props['rules']
        else:
            return []

    def __repr__(self):
        return '%s (%s)' % (self._ern, self._type)

    def __str__(self):
        return '%s (%s)' % (self._ern, self._type)
    
    def fetch(self):
        """
        Gets a policy.

        Raises
        ------
        ResourceError
            If the @id has not been set for the policy. (The policy is missing it's unique Eratos Resource Name (ERN).)

        Returns
        -------
        Policy
            The Eratos Policy object.
        """
        if self._ern is None:
            raise ResourceError('@id must be specified before fetching')
        json_resp = self._adapter.request(self._ern.node_ern(), 'GET', '/policies/%s' % self._ern.id())
        self._set_props_from_content(json_resp, skip_check=True)
        return self
    
    def save(self):
        """
        Posts a policy.

        Raises
        ------
        PolicyError
            If the user does not have permission to create a policy.
 
        Returns
        -------
        Policy
            The Eratos Policy object.
        """
        if self._ern is None:
            raise PolicyError('you may not create a policy directly')
        else:
            if self._ern is not None:
                target_node = self._ern.node_ern()
            elif target_node is None:
                target_node = self._adapter.master_pn()
            json_resp = self._adapter.request(target_node, 'PUT', '/policies/%s' % self._ern.id(), data=self.json(for_push=True).encode('utf-8'))
            self._set_props_from_content(json_resp, skip_check=True)
        return self

    def _set_props_from_content(self, content, merge=False, skip_check=False):
        if not merge:
            self._props = {}
        for k in content.keys():
            if k == '@id':
                ern = Ern(ern=content[k])
                if not skip_check and self._ern is not None and self._ern.root() != ern.root():
                    raise ValueError('cannot replace resource id with a different id')
                self._ern = ern
            elif k == '@date':
                self._date = content[k]
            elif not skip_check and k.startswith('@'):
                raise ValueError('unknown special property \'%s\'' % k)
            else:
                self._props[k] = content[k]
    
    def yaml_set(self, yaml, merge=False):
        """
        Set a policy's properties via yaml.

        Parameters
        ----------
        yaml : str
            The yaml str object containing the policy's properties.
        merge : bool
            True to merge the content with an existing Policy, or False to overwrite. (Default value is False)
        """
        return self._set_props_from_content(yload(yaml, Loader=Loader), merge)

    def json_set(self, obj, merge=False):
        """
        Set a policy's properties via json.

        Parameters
        ----------
        obj : dict
            The json object containing the policy's properties.
        merge : bool
            True to merge the content with an existing Policy, or False to overwrite. (Default value is False)
        """
        return self._set_props_from_content(jload(obj), merge)

    def _construct_ordered_content(self, for_push=False):
        content = {}
        if self._ern is not None:
            content['@id'] = str(self._ern)
        for k in self._props.keys():
            if for_push and '@' in k:
                continue
            content[k] = self._props[k]
        return content

    def json(self, for_push=False, **kwargs):
        """
        Creates a policy's properties in json.

        Parameters
        ----------
        for_push : bool
            A bool to set whether the object is to be pushed. (Default value is False)
        kwargs : args
            Optional keyword property arguments to add to the Policy object.

        Returns
        -------
        dict
            The json dictionary object containing the Policy properties.
        """
        return jdump(self._construct_ordered_content(for_push), **kwargs)
    
    def yaml(self, **kwargs):
        """
        Creates a policy's properties in yaml.

        Parameters
        ----------
        kwargs : args
            Optional keyword property arguments to add to the Policy object.

        Returns
        -------
        str
            The yaml string object containing the Policy properties.
        """
        return ydump(self._construct_ordered_content(), Dumper=Dumper, sort_keys=False, **kwargs).strip()
