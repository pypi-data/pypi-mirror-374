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

class SearchError(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

class DataError(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

class SliceError(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

class ResourceError(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

class PolicyError(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

class CommError(BaseException):
    def __init__(self, status_code, pdata):
        self.status_code = status_code
        self.code = pdata['code']
        if 'message' in pdata:
            self.message = pdata['message']
        else:
            self.message = None
        if 'sentryId' in pdata:
            self.sentryId = pdata['sentryId']
        else:
            self.sentryId = None
        if 'fields' in pdata:
            self.fields = pdata['fields']
        else:
            self.fields = []

    def __str__(self) -> str:
        if self.message is not None and self.message != "":
            emsg = '%s (%s)' % (self.message, self.code)
        else:
            emsg = self.code
        if self.sentryId is not None and self.sentryId != "":
            emsg += ' (%s)' % self.sentryId

        fielderrs = []
        for fe in self.fields:
            ferrs = []
            if 'type' in fe:
                ferrs += [fe['type']]
            if 'key' in fe:
                ferrs += [fe['key']]
            if 'message' in fe:
                ferrs += [fe['message']]
            fielderrs += [':'.join(ferrs)]
        emsg += ' [' + '; '.join(fielderrs) + ']'

        return '%d: %s' % (self.status_code, emsg)
