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

from functools import reduce
import logging
import os
import importlib.util
from json import dumps as jdump, loads as jload
from yaml import load as yload, dump as ydump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .resource import Resource
from .ern import Ern

_logger = logging.getLogger(__name__)

_operators = {}

# Operatos is used to define an operator function.
def operator(ern):
    """
    A wrapper to define an Eratos Operator function.

    Parameters
    ----------
    ern : str
        The Eratos Resource Name (ERN) string.
    
    Returns
    -------
    Any
        Wrapper or function.
    """
    def wrapper(fn):
        global _operators
        _operators[ern] = fn
        return fn
    return wrapper

class Operator:
    """
    A class used to interact with Eratos' Operators.
    """
    def __init__(self, adapter, ern=None, yaml=None, json=None, content=None):
        self._adapter = adapter
        self._resource = adapter.Resource(ern=ern, yaml=yaml, json=json, content=content)

    def is_valid(self):
        """
        Utility function to determine the validity of an operator's fields.

        Returns
        -------
        bool
            True or False depending on the validity of a field.
        """
        return self._resource.is_valid()

    def ern(self):
        """
        Retrieves the unique Eratos Resource Name (ERN) for an operator.

        Returns
        -------
        Ern
            The unique Eratos Resource Name (ERN).
        """
        return self._resource.ern()

    def __repr__(self):
        return self._resource.__repr__()

    def __str__(self):
        return self._resource.__str__()

    def resource(self):
        """
        Retrieves the resource for an operator.

        Returns
        -------
        Resource
            The underlying resource for the operator.
        """
        return self._resource

    def help(self):
        """
        Retrieves a help message for an operator.

        Raises
        ------
        AssertionError
            If the operator is not valid.

        Returns
        -------
        str
            Help message.
        """
        if not self.is_valid():
            raise AssertionError('cannot get help, opterator is not valid')
        co = self._resource.props()
        kvArgsDesc = map(lambda v: '%s=%s'%(v['name'], 'None' if v['default'] == '' else v['default']), co['inputs'])
        help = 'Operator:\n\n%s(%s)\n\nDescription:\n\n%s\n\nArguments:\n\n' % (co['name'], ', '.join(kvArgsDesc), co['description'])
        maxNameSz = reduce(lambda a, b: max(a, len(b)), [v['name'] for v in co['inputs']], 0)
        for var in co['inputs']:
            help += ('  %% %ds - %%s\n' % maxNameSz) % (var['name'], var['description'])
        return help+'\n'

    def examples(self):
        """
        Retrieves examples for an operator.

        Raises
        ------
        AssertionError
            If the operator is not valid.

        Returns
        -------
        str
            String examples.
        """
        if not self.is_valid():
            raise AssertionError('cannot get examples, opterator is not valid')
        exContent = ''
        for ex in self._resource.props()['examples']:
            exContent += '%s:\n\n%s\n\n' % (ex['name'], ex['description'])
        return exContent

    def find_input(self, name):
        """
        Retrieves an input's properties in an operator based on a provided name.

        Parameters
        ------
        name : str
            Name of the input.

        Returns
        -------
        dict
            Object containing an input's properties.
        """
        co = self._resource.props()
        for inp in co['inputs']:
            if inp['name'] == name:
                return inp
        return None

    def conv_r_inputs(self, inputs):
        rInputs = []
        co = self._resource.props()
        arg_keys = list([a['name'] for a in co['inputs']])
        for ka in inputs:
            if ka not in arg_keys:
                raise Exception('%s not found in operator arguments' % ka)
        for inp in co['inputs']:
            ka = inp['name']
            if ka not in inputs:
                raise Exception('%s not found in operator inputs' % inp['name'])
            if inp['type'] == 'resource' or (inp['type'] == 'geometry' and 'ern:' in inputs[ka]):
                rInputs += [self._adapter.Resource(ern=inputs[ka])]
            else:
                rInputs += [inputs[ka]]
        return rInputs

    def conv_r_outputs(self, outputs):
        for k in outputs:
            if isinstance(outputs[k], Resource):
                outputs[k] = str(outputs[k].ern())
            elif isinstance(outputs[k], Ern):
                outputs[k] = str(outputs[k])
        return outputs

    def __call__(self, codedir, *args, **kwds):
        global _operators
        # Build argument list.
        if len(args) > 0:
            raise Exception('all arguments past codedir must be of key-value form for operator call')
        co = self._resource.props()
        arg_keys = list([a['name'] for a in co['inputs']])
        for ka in kwds:
            if ka not in arg_keys:
                raise Exception('%s not found in operator arguments' % ka)
            inp = self.find_input(ka)
            if inp['type'] == 'resource' or (inp['type'] == 'geometry' and 'ern:' in kwds[ka]):
                kwds[ka] = self._adapter.Resource(ern=kwds[ka])
        # Validate argument list and convert resource ids, etc.
        # Load the entry point as a module.
        epc = os.path.join(codedir, 'entry.py')
        if not os.path.exists(epc):
            raise Exception('could not find entry.py in %s' % codedir)
        spec = importlib.util.spec_from_file_location('eratos_operator', epc)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # At this point the operator function should exist in _operators.
        oid = str(self.ern())
        if oid not in _operators:
            raise Exception('operator for %s not found in entry.py' % oid)
        # Execute the operator.
        fn = _operators[oid]
        return fn({'adapter': self._adapter}, **kwds)
