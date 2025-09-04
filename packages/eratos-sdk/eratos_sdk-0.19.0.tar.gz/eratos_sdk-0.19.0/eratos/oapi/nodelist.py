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

_logger = logging.getLogger(__name__)

class NodeList:
    def __init__(self, adapter, incEratosNodes=False):
        self.adapter = adapter
        self.nodes = []
        self.fetch(incEratosNodes)

    def fetch(self, incEratosNodes=False):
        self.nodes = [self.adapter.Node(content=nd) for nd in self.adapter.request('GET', '/nodes') if nd['owner'] != 'eratos' or incEratosNodes]
        return self

    def length(self):
        return len(self.nodes)
    
    def find(self, exp):
        for i in range(len(self.nodes)):
          if self.nodes[i].id() == exp or self.nodes[i].content['friendlyId'] == exp:
            return self.nodes[i]
        return None
