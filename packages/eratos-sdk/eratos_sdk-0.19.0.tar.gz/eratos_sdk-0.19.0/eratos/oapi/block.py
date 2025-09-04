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

from .errors import PolicyError, CommError
from .util import decode_request_content_response

_logger = logging.getLogger(__name__)

class Block:
    def __init__(self, adapter, id=None, blocks=None, resources=None, operators=None, datasets=None):
        self.adapter = adapter
        self.host = None
        self.blocks = []
        self.resources = []
        self.operators = []
        self.datasets = []
        if id is not None:
            self.content = {
                'id': id
            }
        elif blocks is not None:
            self.blocks = blocks
            self.resources = resources
            self.operators = operators
            self.datasets = datasets

    def is_valid(self):
        if self.content is None:
            return False
        if 'id' not in self.content:
            return False
        return True

    def id(self):
        return self.content['id']

    def blocks(self, query):
        return None

    def resources(self, query, *k, **kw):
        return None

    def operators(self, query, *k, **kw):
        return None

    def datasets(self, query, *k, **kw):
        return None
