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
from urllib.parse import urlparse
from datetime import datetime
import hashlib
import hmac
import base64

_logger = logging.getLogger(__name__)

class AccessTokenCreds:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        mp = len(client_secret) % 4
        if mp > 0:
            self.client_secret = client_secret + '=' * (4 - mp)
        else:
            self.client_secret = client_secret

    def __call__(self, r):
        # Calculate the sha256 hash of the body.
        h = hashlib.sha256()
        if r.body is None:
            h.update(b'')
        else:
            h.update(r.body)
        req_hash = h.hexdigest()
        # Set the current date.
        r.headers['X-Eratos-Date'] = datetime.now().isoformat()
        # Generate the canonical request.
        headers_req = ['X-Eratos-Date']
        if r.body is not None:
            headers_req += ['Content-Type']
        url = urlparse(r.url)
        canon_req = r.method.upper() + '\n' + url.path + '\n' + url.query + '\n'
        canon_req += 'host:' + url.hostname+((':'+'%d'%url.port) if url.port is not None else '') + '\n'
        for h in headers_req:
            canon_req += h.lower() + ':' + r.headers[h] + '\n'
        canon_req += req_hash
        # Sign the incoming request.
        s = hmac.new(base64.urlsafe_b64decode(self.client_secret), digestmod=hashlib.sha256)
        s.update(canon_req.encode('utf-8'))
        req_sig = s.hexdigest()
        # Authorize the request.
        req_heads = ';'.join(h.lower() for h in ['Host']+headers_req)
        r.headers['Authorization'] = 'ERATOS-HMAC-SHA256 Credential=%s, SignedHeaders=%s, Signature=%s' % (self.client_id, req_heads, req_sig)
        _logger.debug('AUTH HEADER: %s' % r.headers['Authorization'])
        return r



