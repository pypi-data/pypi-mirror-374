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

import os
import io
import base64
import hashlib
import logging
import pprint
import binascii
import urllib

from .dsutil.manifest import Manifest
from .ext import iter_to_stream

_logger = logging.getLogger(__name__)

def move_prefix_to_new_format(content):
  ch_content = {}
  for k in content.keys():
    if k[0] == '$':
      _logger.warn('deprecated use of $ prefixes, move to @')
      if k == '$schema':
        nk = '@type'
      else:
        nk = '@' + k[1:]
      ch_content[nk] = content[k]
    else:
      ch_content[k] = content[k]
  return ch_content


def decode_request_content_response(req):
  ct = req.headers.get('Content-Type')
  if ct == None:
    return req.content
  cta = ct.split(';')[0].lower().strip()
  if cta == 'application/json':
    return req.json()
  elif cta == 'plain/text' or cta == 'application/vnd.eratos.tok':
    return req.text
  elif cta == 'application/vnd.eratos.manifest':
    # We assume the request is streaming.
    return Manifest(fp=iter_to_stream(req.iter_content(io.DEFAULT_BUFFER_SIZE)))
  elif cta == 'application/octet-stream':
    return req.content
  else:
    return req.content

def iter_bitmap_ones(bitmap):
  bitmapLength = bitmap['count']
  bs = base64.urlsafe_b64decode(bitmap['bitmap'])
  for i in range(bitmapLength):
    if (bs[i//8] >> (i%8))&1 != 1:
      yield i
