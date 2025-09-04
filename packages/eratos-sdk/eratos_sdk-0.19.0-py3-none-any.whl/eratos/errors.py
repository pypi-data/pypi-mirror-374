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

from json import dumps as jdump

class SearchError(Exception):
    """
    Search errors class
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

class DataError(Exception):
    """
    Data errors class
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

class SliceError(Exception):
    """
    Slice errors class
    """
    def __init__(self, obj):
        self.obj = obj

    def __str__(self) -> str:
        return jdump(self.obj)

class ResourceError(Exception):
    """
    Resource errors class
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

class PolicyError(Exception):
    """
    Policy errors class
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

class CommError(Exception):
    """
    Comms errors class
    """
    def __init__(self, status_code, pdata):
        self.status_code = status_code
        self.code = pdata['code']
        if 'msg' in pdata:
            self.message = pdata['msg']
        elif 'message' in pdata:
            self.message = pdata['message']
        else:
            self.message = None
        if 'extra' in pdata:
            self.extra = pdata['extra']
        elif 'fields' in pdata:
            self.extra = pdata['fields']
        else:
            self.extra = None

    def __str__(self) -> str:
        if self.message is not None:
            emsg = f'{self.message} ({self.code})'
        else:
            emsg = f'({self.code})'
        if self.extra is not None:
            emsg += ' - %s' % jdump(self.extra)
        return emsg
