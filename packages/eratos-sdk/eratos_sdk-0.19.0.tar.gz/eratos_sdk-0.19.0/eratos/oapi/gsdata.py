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
import pprint
import json
import base64
import binascii
import time

import numpy as np

from .errors import CommError, SliceError

_logger = logging.getLogger(__name__)

def datatype_to_bytesize(dt):
  if dt == 'i1' or dt == 'u1':
    return 1
  elif dt == 'i2' or dt == 'u2':
    return 2
  elif dt == 'i4' or dt == 'u4' or dt == 'f4':
    return 4
  elif dt == 'i8' or dt == 'u8' or dt == 'f8':
    return 8
  raise AttributeError('unknown datatype %s' % dt)

class GSData:
    def __init__(self, adapter, resource, data):
        self.adapter = adapter
        self.resource = resource
        self.data = data
        self.geom = data.version['fetchInterfaces']['Geom:v1']

    def dimensions(self):
      return self.geom['dimensions']

    def spaces(self):
      return self.geom['spaces']

    def variables(self):
      vlist = {}
      for k in self.geom['variables'].keys():
        vlist[k] = {
          'dataType': self.geom['variables'][k]['returnType'] if 'returnType' in self.geom['variables'][k] else self.geom['variables'][k]['dataType'],
          'space': self.geom['variables'][k]['space'],
        }
      return vlist

    def perform_sapi_command_with_numpyres(self, params):
      for n in range(5):
        try:
          return self._perform_sapi_command_with_numpyres_impl(params)
        except SliceError as err:
          pass
        time.sleep(2**n)
        
    def _perform_sapi_command_with_numpyres_impl(self, params):
      # Find a node we have permission to pull from.
      dn = None
      for loc in self.data.version['nodes'].keys():
        if 'Geom:v1' not in self.data.version['nodes'][loc]['fetchInterfaces']:
          continue
        dn = self.adapter.Node(id=loc) # dn_list.find(loc)
        if dn is not None:
          break
      if dn is None:
          raise AttributeError('you do not have access to a data node with the given content')
      # Perform the command.
      ep = self.data.version['nodes'][dn.id()]['fetchInterfaces']['Geom:v1']
      headers = {}
      headers['Authorization'] = 'Bearer ' + self.adapter.get_data_node_token()
      headers['Accept'] = 'application/octet-stream'
      _logger.debug('perform_sapi_command: running command %s params=%s' % (ep, pprint.pformat(params, width=1024*1024)))
      with self.adapter.session().request('GET', ep, params=params, headers=headers, verify=not self.adapter.ignore_certs, stream=True) as req:
        _logger.debug('perform_sapi_command: initial result %d %s' % (req.status_code, pprint.pformat(req.headers, width=1024*1024)))
        if req.status_code >= 200 and req.status_code < 400:
          # Stream the results into a numpy array.
          if 'X-Eratos-Geom-Datatype' not in req.headers:
            raise AttributeError('missing X-Eratos-Geom-Datatype header from response')
          if 'X-Eratos-Geom-Shape' not in req.headers:
            raise AttributeError('missing X-Eratos-Geom-Shape header from response')
          dt = req.headers['X-Eratos-Geom-Datatype']
          shp = json.loads(req.headers['X-Eratos-Geom-Shape'])
          res = np.zeros(shp)
          for sl in self.decode_streaming_slices(req, dt, shp):
            starts = sl[0]
            counts = sl[1]
            arr = sl[2]
            arr_slice = tuple([slice(starts[d], starts[d]+counts[d]) for d in range(len(starts))])
            res[arr_slice] = arr
          return res
        else:
          if 'application/json' in req.headers.get('Content-Type'):
              raise CommError(req.status_code, req.json())
          else:
              raise CommError(req.status_code, { 'code': 'unknown', 'message': req.text })

    def decode_streaming_slices(self, req, dt, shp):
      dt_size = datatype_to_bytesize(dt)
      head_vec_size = len(shp) * 8
      header = None
      last_chunk_leftover = b''
      for chunk in req.iter_content(8*1024*1024):
        this_chunk = last_chunk_leftover + chunk
        while len(this_chunk) > 0:
          # We need to read the header.
          if header is None:
            # We're reading the header.
            hdrend = -1
            for i in range(len(this_chunk)-1):
              if this_chunk[i] == 13 and this_chunk[i+1] == 10:
                hdrend = i
                break
            if hdrend < 0: # End of the header wasn't found in this chunk, read the next.
              break
            try:
              hdrJSON = this_chunk[:hdrend].decode('utf-8')
              _logger.debug('decode_streaming_slices: retrieved header %s' % hdrJSON)
              header = json.loads(hdrJSON)
            except:
              _logger.debug('decode_streaming_slices: invalid header %s' % binascii.hexlify(this_chunk[:hdrend]))
              raise AttributeError('failed to decode the slice header')
            # Shift to the start of the payload.
            if len(this_chunk) >= hdrend+2:
              this_chunk = this_chunk[hdrend+2:]
            else:
              this_chunk = b''
          # Check the slice status.
          if header['status'] == "error":
            raise SliceError('received slice error: "%s"' % header['error'])
          elif header['status'] != "ok":
            raise AttributeError('received invalid header status: %s' % header['status'])
          # Calculate the size of the slice.
          starts = np.array(header['starts'])
          counts = np.array(header['counts'])
          for i in range(len(shp)):
            assert(starts[i] >= 0 and counts[i] > 0 and starts[i]+counts[i] <= shp[i])
          slice_size = np.prod(counts) * dt_size
          assert(slice_size == header['payloadSize'])
          # If we have the available data read the slice, otherwise read the next chunk
          if slice_size+2 <= len(this_chunk):
            _logger.debug('decode_streaming_slices: found slice %s, %s' % (pprint.pformat(starts, width=1024*1024), pprint.pformat(counts, width=1024*1024)))
            if np.prod(counts) == 0:
              raise AttributeError('received empty chunk')
            _logger.debug('this_chunk %s' % binascii.hexlify(this_chunk[:16]))
            yield (starts, counts, np.fromstring(this_chunk[:slice_size], dtype=dt).reshape(counts))
            assert(this_chunk[slice_size] == 13 and this_chunk[slice_size+1] == 10)
            this_chunk = this_chunk[slice_size+2:]
            header = None
          else:
            break
        last_chunk_leftover = this_chunk
      if len(last_chunk_leftover) != 0:
            raise AttributeError('there are an extra %d bytes in the response' % len(last_chunk_leftover))

    def get_subset_as_array(self, var, starts=None, ends=None, strides=None):
      if var not in self.geom['variables']:
        raise Exception('variable name is invalid')
      sdef = self.geom['spaces'][self.geom['variables'][var]['space']]
      ndims = len(sdef['dimensions'])
      if starts is None:
        starts = [0] * ndims
      if ends is None:
        ends = [self.geom['dimensions'][d]['size'] for d in sdef['dimensions']]
      if strides is None:
        strides = [1] * ndims
      if type(starts) is int or type(starts) is float:
        starts = [starts]
      if type(ends) is int or type(ends) is float:
        ends = [ends]
      if type(strides) is int or type(strides) is float:
        strides = [strides]
      if type(starts) is not list or len(starts) != ndims:
        raise Exception('starts expected to be a list of size %d' % ndims)
      if type(ends) is not list or len(ends) != ndims:
        raise Exception('ends expected to be a list of size %d' % ndims)
      if type(strides) is not list or len(strides) != ndims:
        raise Exception('strides expected to be a list of size %d' % ndims)
      for i in range(ndims):
        if starts[i] < 0:
          starts[i] = self.geom['dimensions'][sdef['dimensions'][i]]['size'] + starts[i] + 1
        if ends[i] < 0:
          ends[i] = self.geom['dimensions'][sdef['dimensions'][i]]['size'] + ends[i] + 1
      params = {
        'cmd': 'ISUB',
        'var': var,
        'starts': '['+','.join([str(int(v)) for v in starts])+']',
        'ends': '['+','.join([str(int(v)) for v in ends])+']',
        'strides': '['+','.join([str(int(v)) for v in strides])+']',
      }
      return self.perform_sapi_command_with_numpyres(params)

    def get_point_slices(self, var, mask, pts, starts=None, ends=None, strides=None, indexed=False):
      if var not in self.geom['variables']:
        raise Exception('variable name is invalid')
      sdef = self.geom['spaces'][self.geom['variables'][var]['space']]
      ndims = len(sdef['dimensions'])
      if type(pts) is list:
        if len(pts) > 0 and (type(pts[0]) is int or type(pts[0]) is float):
          pts = [pts]
        pts = np.array(pts)
      if type(mask) is not str or len(mask) != ndims:
        raise Exception('mask expected to be a string of size %d' % ndims)
      ptsIdx = []
      slcIdx = []
      for i in range(len(mask)):
        if mask[i] == 'S':
          slcIdx += [i]
        elif mask[i] == 'P':
          ptsIdx += [i]
        else:
          raise Exception('mask character invalid at index %d is invalid, should be one of S/P' % ndims)
      if len(pts.shape) != 2:
          raise Exception('expected the dimensionality of points to be 2 not %d' % len(pts.shape))
      if pts.shape[1] != len(ptsIdx):
          raise Exception('seconds pts dimension should be of size %d' % len(ptsIdx))
      if starts is None:
        if len(slcIdx) == 0:
          starts = []
        else:
          starts = [0] * len(slcIdx)
      if ends is None:
        if len(slcIdx) == 0:
          ends = []
        else:
          ends = [self.geom['dimensions'][d]['size'] for d in slcIdx]
      if strides is None:
        if len(slcIdx) == 0:
          strides = []
        else:
          strides = [1] * len(slcIdx)
      if type(starts) is int or type(starts) is float:
        starts = [starts]
      if type(ends) is int or type(ends) is float:
        ends = [ends]
      if type(strides) is int or type(strides) is float:
        strides = [strides]
      if type(starts) is not list or len(starts) != len(slcIdx):
        raise Exception('starts expected to be a list of size %d' % len(slcIdx))
      if type(ends) is not list or len(ends) != len(slcIdx):
        raise Exception('ends expected to be a list of size %d' % len(slcIdx))
      if type(strides) is not list or len(strides) != len(slcIdx):
        raise Exception('strides expected to be a list of size %d' % len(slcIdx))
      for i in range(len(slcIdx)):
        d = slcIdx[i]
        if ends[i] < 0:
          ends[i] = self.geom['dimensions'][sdef['dimensions'][d]]['size'] + ends[i] + 1
      ptsDT = 'i8' if indexed else 'f8'
      params = {
        'cmd': 'SPTS',
        'mask': mask,
        'var': var,
        'slicesStarts': '['+','.join([str(int(v)) for v in starts])+']',
        'slicesEnds': '['+','.join([str(int(v)) for v in ends])+']',
        'slicesStrides': '['+','.join([str(int(v)) for v in strides])+']',
        'pointsFormat': 'Binary',
        'points': base64.urlsafe_b64encode(b'\x00' + ptsDT.encode('ascii') + np.array([pts.shape[0]], 'u4').tobytes('C') + pts.astype(ptsDT).tobytes('C')).decode('ascii'),
        'pointsAreIndexes': indexed
      }
      return self.perform_sapi_command_with_numpyres(params)
