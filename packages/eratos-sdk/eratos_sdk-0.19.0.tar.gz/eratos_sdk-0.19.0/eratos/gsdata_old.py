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
from shapely import wkt, geometry
from datetime import timezone
import datetime
import numpy as np
from pyproj import CRS
from pyproj import Transformer

from .errors import CommError, SliceError

_logger = logging.getLogger(__name__)

def datatype_to_bytesize(dt):
  """
  Utility function to get the bytesize of a given data type.
  """
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
    """
    A class to handle geospatial data.
    """
    def __init__(self, adapter, resource, data):
        self._adapter = adapter
        self._resource = resource
        self._data = data
        self._geom = data.version()['fetchInterfaces']['Geom:v1']

    def dimensions(self):
      """
      Retrieves the dimensions for a given dataset.

      Returns
      -------
      dict[]
          The list of dimension dictionaries including a key, spacing, variable (is) and unit.
      """
      return self._geom['dimensions']

    def spaces(self):
      """
      Retrieves the spaces for a given dataset.

      Returns
      -------
      str[]
          The list of spaces.
      """
      return self._geom['spaces']

    def variables(self):
      """
      Retrieves the variables.

      Returns
      -------
      dict[]
          The list of variables and their data types and spaces. The dictionary keys are the variable keys.
      """
      vlist = {}
      for k in self._geom['variables'].keys():
        vlist[k] = {
          'dataType': self._geom['variables'][k]['returnType'] if 'returnType' in self._geom['variables'][k] else self._geom['variables'][k]['dataType'],
          'space': self._geom['variables'][k]['space'],
        }
      return vlist

    def perform_sapi_command_with_numpyres(self, params):
      """
      Utility function.
      """
      for n in range(5):
        try:
          return self._perform_sapi_command_with_numpyres_impl(params)
        except SliceError as err:
          pass
        time.sleep(2**n)
        
    def _perform_sapi_command_with_numpyres_impl(self, params):
      # Find a node we have permission to pull from.
      dn = None
      ds_ver = self._data.version()
      for loc in ds_ver['nodes'].keys():
        if 'Geom:v1' not in ds_ver['nodes'][loc]['fetchInterfaces']:
          continue
        ds_ver['nodes'][loc]['id'] = loc
        dn = ds_ver['nodes'][loc]
        break
      if dn is None:
          raise AttributeError('you do not have access to a data node with the given content')
      # Perform the command.
      ep = ds_ver['nodes'][dn['id']]['fetchInterfaces']['Geom:v1']
      headers = {}
      headers['Accept'] = 'application/octet-stream'
      _logger.debug('perform_sapi_command: running command %s params=%s' % (ep, pprint.pformat(params, width=1024*1024)))
      with self._adapter.dnstreamrequest('GET', ep, params=params, headers=headers) as req:
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
      """
      Utility function to decode streaming slices.
      """
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
      """
      Extract a desired subset from an Eratos gridded dataset.

      Parameters
      ----------
      var : str
          The variable key of the variable to fetch.
      starts : int[] or float[]
          A list of start numbers. (Default value is None)
      ends : int[] or float[]
          A list of end numbers. (Default value is None)
      strides : int[] or float[]
          A list of stride numbers. (Default value is None)
      
      Raises
      ------
      Exception
          Starts, ends, strides are invalid.

      Returns
      -------
      arr
          An array of the variable's data.
      """
      if var not in self._geom['variables']:
        raise Exception('variable name is invalid')
      sdef = self._geom['spaces'][self._geom['variables'][var]['space']]
      ndims = len(sdef['dimensions'])
      if starts is None:
        starts = [0] * ndims
      if ends is None:
        ends = [self._geom['dimensions'][d]['size'] for d in sdef['dimensions']]
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
          starts[i] = self._geom['dimensions'][sdef['dimensions'][i]]['size'] + starts[i] + 1
        if ends[i] < 0:
          ends[i] = self._geom['dimensions'][sdef['dimensions'][i]]['size'] + ends[i] + 1
      params = {
        'cmd': 'ISUB',
        'var': var,
        'starts': '['+','.join([str(int(v)) for v in starts])+']',
        'ends': '['+','.join([str(int(v)) for v in ends])+']',
        'strides': '['+','.join([str(int(v)) for v in strides])+']',
      }
      return self.perform_sapi_command_with_numpyres(params)

    def get_point_slices(self, var, mask, pts, starts=None, ends=None, strides=None, indexed=False):
      """
      Extract a desired subset of a given point from an Eratos gridded dataset.

      Parameters
      ----------
      var : str
          The variable key of the variable to fetch.
      mask : str
          The mask to apply to fetch.
      pts : int[] or float[]
          A list of points to fetch.
      starts : int[] or float[]
          A list of start numbers. (Default value is None)
      ends : int[] or float[]
          A list of end numbers. (Default value is None)
      strides : int[] or float[]
          A list of stride numbers. (Default value is None)
      indexed : bool
          Set whether the points are indexed. (Default value is False)
      
      Raises
      ------
      Exception
          Starts, ends, strides are invalid.

      Returns
      -------
      arr
          An array of the variable's data.
      """
      if var not in self._geom['variables']:
        raise Exception('variable name is invalid')
      sdef = self._geom['spaces'][self._geom['variables'][var]['space']]
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
          ends = [self._geom['dimensions'][d]['size'] for d in slcIdx]
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
          ends[i] = self._geom['dimensions'][sdef['dimensions'][d]]['size'] + ends[i] + 1
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

    def get_timeseries_at_points(self, var, point_list, startDate, endDate, time_stride=1):
      """
      Extract desired timeseries data at given point(s) from an Eratos gridded dataset for a given time range.

      Parameters
      ----------
      var : str
          The variable key of the variable to fetch.
      point_list : str[]
          A list of Well-Known Text (WKT) formatted string points. (Minimum of 1)
      startDate : str
          The start date for the fetched timeseries. (ex. "2021-01-01" following the Eratos Date-Time Data Standards)
      endDate : str
          The end date for the fetched timeseries. (ex. "2021-01-01" following the Eratos Date-Time Data Standards)
      time_stride : int
          The stride in the time dimension. Note: for a dataset with a daily temporal frequency 'time_stride' of 2, it would extract every second day. (Default value is 1)

      Raises
      ------
      TypeError
          If invalid parameter types are present.
      Exception
          If no location points are given.
      ValueError
          If the location points are not in WKT format.

      Returns
      -------
      arr
          An array of the variable's data at given location(s) for a given time range.
      """
      # Check input variables are correct type 
      if type(point_list) is not list:
          raise TypeError('invalid type for point_list: %s' % type(point_list))
      if len(point_list) < 1:
          raise Exception('point_list is empty, please ensure there is at least one WKT point inside list')
      if type(var) is not str:
          raise TypeError('invalid type for var: %s' % type(var))
      if type(startDate) is not str:
          raise TypeError('invalid type for endDate: %s' % type(startDate))
      if type(endDate) is not str:
          raise TypeError('invalid type for endDate: %s' % type(endDate))    
      
      # Assume input WGS84, if dataset projection is not WGS84, convert point projection
      wkt_list = []
      grid_proj = self._resource.prop_path('grid.geo.proj')
      fromCRS = CRS.from_proj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
      toCRS = CRS.from_proj4(grid_proj if grid_proj is not None else "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
      transformer = Transformer.from_crs(fromCRS, toCRS)

      for point in point_list:
        p = wkt.loads(point)
        x,y = transformer.transform(p.x, p.y)
        loc= [y, x]
        wkt_list.append(loc)
          
      #2 date: Create a Unix timestamp in UTC timezone from the YYYY-MM-DD formatted date string - e.g. "2022-01-01"
       # or the YYYY-MM-DDTHH:MM:SSZ  formatted datetime string - e.g. "2022-01-01T22:00:00Z"
      day_date_length = 10
      if len(startDate) > day_date_length:
          unix_ts_utc_start = datetime.datetime.strptime(startDate, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp()
      else:
          unix_ts_utc_start = datetime.datetime.strptime(startDate, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()

      if len(endDate) > day_date_length:
          unix_ts_utc_end = datetime.datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp()
      else:
          unix_ts_utc_end = datetime.datetime.strptime(endDate, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()

      times = self.get_subset_as_array('time')
      start_idx = np.where(times == unix_ts_utc_start)[0][0]
      end_idx = (np.where(times == unix_ts_utc_end)[0][0])+1
     
      data_query_array = self.get_point_slices(var, 'SPP', pts=wkt_list, starts=[start_idx], ends=[end_idx],strides =  [time_stride])
      
      return data_query_array

    def get_geospatial_slice_at_times_as_array(self, var, time_list, bottomLeftPoint, topRightPoint, lat_stride=1, lon_stride=1, verbose=True):
      """
      Extract data for a given point at given times from an Eratos gridded dataset.

      Parameters
      ----------
      var : str
          The variable key of the variable to fetch.
      time_list : str[]
          An array of datetimes in Eratos Date-Times Data Standards (ex. "2021-01-01"), with a minimum of 1.
      bottomLeftPoint : str
          The bottom left point for the fetched geospatial grid in Well-Known Text format. (ex. "POINT(147, -44)")
      topRightPoint : str
          The top right point for the fetched geospatial grid in Well-Known Text format. (ex. "POINT(147, -44)")
      lat_stride : int
          The stride in the latitude dimension. (Default value is 1)
      lon_stride : int
          The stride in the longitude dimension. (Default value is 1)
      verbose : bool
          Prints statement that details the specifics of the output. (Default value is True)

      Raises
      ------
      TypeError
          If invalid parameter types are present.
      Exception
          If no location points are given.
      ValueError
          If the location points are not in WKT format.

      Returns
      -------
      arr
          An array of the variable's data at given times in a given location.
      """
      # Check input variables are correct type 
      if type(time_list) is not list:
          raise TypeError('invalid type for time_list: %s' % type(time_list))
      if len(time_list) < 1:
          raise Exception('time_list is empty, please ensure there is at least one time inside list')
      if type(var) is not str:
          raise TypeError('invalid type for var: %s' % type(var))

      #2 date: Create a Unix timestamp in UTC timezone from the YYYY-MM-DD formatted date string - e.g. "2022-01-01"
      # or the YYYY-MM-DDTHH:MM:SSZ  formatted datetime string - e.g. "2022-01-01T22:00:00Z"
      day_date_length = 10
      time_utc_list = []
      for time in (time_list):
          if len(time) > day_date_length:
            unix_ts_utc_time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp()
          else:
            unix_ts_utc_time = datetime.datetime.strptime(time, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()
          time_utc_list.append([unix_ts_utc_time])
          
      bottomLeftPoint_shape = wkt.loads(bottomLeftPoint)
      if type(bottomLeftPoint_shape) is not geometry.Point:
          raise ValueError('value inside bottomLeftPoint should be a WKT point')
      topRightPoint_shape = wkt.loads(topRightPoint)
      if type(topRightPoint_shape) is not geometry.Point:
          raise ValueError('value inside topRightPoint should be a WKT point')
   
      lats = self.get_subset_as_array('lat')
      lons = self.get_subset_as_array('lon')
      spacingLat, spacingLon = lats[1]-lats[0], lons[1]-lons[0]
      minLatIdx, maxLatIdx = np.argmin(np.abs(lats-bottomLeftPoint_shape.y)), np.argmin(np.abs(lats-topRightPoint_shape.y))
      minLonIdx, maxLonIdx = np.argmin(np.abs(lons -bottomLeftPoint_shape.x)), np.argmin(np.abs(lons -topRightPoint_shape.x))
      # Use fundamental function to pull requested slices
      data_query_array = self.get_point_slices(var, 'PSS', pts=time_utc_list, starts=[minLatIdx,minLonIdx], ends=[maxLatIdx, maxLonIdx], indexed=False, strides =  [lat_stride,lon_stride])
      if verbose:
          print(f""" 
          The following bottom left, {str(bottomLeftPoint)}, and top right {str(topRightPoint)} Points of the grid were provided.
          As the grid corners must correspond to the dataset's underlying grid these points were snapped to the following points: 
          bottom left, {str('Point('+str(lons[minLonIdx]) + " " + str(lats[minLatIdx]) +")")}, and top right {str('Point('+str(lons[maxLonIdx]) + " " + str(lats[maxLatIdx])+")")}""")
          print(f"""
          The returned numpy array will have the following shape: {str(data_query_array.shape)}
          The first array dimension is time with length {str(data_query_array.shape[0])}

          The second array dimension is a south-north vector with length {str(data_query_array.shape[1])} where the index = 0 is the southern most point of the grid {str(lats[minLatIdx])}
          Incrementing at {str(round(spacingLat,2))} degree per 1 increase in index ending at {str(lats[maxLatIdx])}.

          The third array dimension is a west-east vector with length {str(data_query_array.shape[2])} where the index = 0 is the eastern most point of the grid {str(lons[minLonIdx])}
          Incrementing at {str(round(spacingLon,2))} degree per 1 increase in index ending at {str(lons[maxLonIdx])}.
              """)

      return data_query_array

    def get_3d_subset_as_array(self, var, startDate, endDate, bottomLeftPoint, topRightPoint, time_stride=1, lat_stride=1, lon_stride=1, verbose=True):
      """
      Extract a desired 3D subset for a given time range at a given location from an Eratos gridded dataset.

      Parameters
      ----------
      var : str
          The variable key of the variable to fetch.
      startDate : str
          The start date for the fetched timeseries. (ex. "2021-01-01" following the Eratos Date-Time Data Standards)
      endDate : str
          The end date for the fetched timeseries. (ex. "2021-01-01" following the Eratos Date-Time Data Standards)
      bottomLeftPoint : str
          The bottom left point for the fetched geospatial grid in Well-Known Text format. (ex. "POINT(147, -44)")
      topRightPoint : str
          The top right point for the fetched geospatial grid in Well-Known Text format. (ex. "POINT(147, -44)")
      time_stride : int
          The stride in the time dimension. (Default value is 1)
      lat_stride : int
          The stride in the latitude dimension. (Default value is 1)
      lon_stride : int
          The stride in the longitude dimension. (Default value is 1)
      verbose : bool
          Prints statement that details the specifics of the output. (Default value is True)

      Raises
      ------
      TypeError
          If invalid parameter types are present.
      ValueError
          If the location points are not in WKT format.

      Returns
      -------
      arr
          An array of the variable's data for a given time range at a given location.
      """
      if type(var) is not str:
          raise TypeError('invalid type for var: %s' % type(var))
      if type(startDate) is not str:
          raise TypeError('invalid type for endDate: %s' % type(startDate))
      if type(endDate) is not str:
          raise TypeError('invalid type for endDate: %s' % type(endDate))    

      #2 date: Create a Unix timestamp in UTC timezone from the YYYY-MM-DD formatted date string - e.g. "2022-01-01"
      # or the YYYY-MM-DDTHH:MM:SSZ  formatted datetime string - e.g. "2022-01-01T22:00:00Z"
      day_date_length = 10
      if len(startDate) > day_date_length:
          unix_ts_utc_start = datetime.datetime.strptime(startDate, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp()
      else:
          unix_ts_utc_start = datetime.datetime.strptime(startDate, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()

      if len(endDate) > day_date_length:
          unix_ts_utc_end = datetime.datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp()
      else:
          unix_ts_utc_end = datetime.datetime.strptime(endDate, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()

      times = self.get_subset_as_array('time')
      startTime_idx = np.where(times == unix_ts_utc_start)[0][0]
      endTime_idx = (np.where(times == unix_ts_utc_end)[0][0])+1
      spacingTime = times[startTime_idx]-times[endTime_idx]
  
      bottomLeftPoint_shape = wkt.loads(bottomLeftPoint)
      if type(bottomLeftPoint_shape) is not geometry.Point:
          raise ValueError('value inside bottomLeftPoint should be a WKT point')
      topRightPoint_shape = wkt.loads(topRightPoint)
      if type(topRightPoint_shape) is not geometry.Point:
          raise ValueError('value inside topRightPoint should be a WKT point')
      # Extract lat and lon to compute indexs
      lats = self.get_subset_as_array('lat')
      lons = self.get_subset_as_array('lon')
      spacingLat, spacingLon = lats[1]-lats[0], lons[1]-lons[0]
      minLatIdx, maxLatIdx = np.argmin(np.abs(lats-bottomLeftPoint_shape.y)), np.argmin(np.abs(lats-topRightPoint_shape.y))
      minLonIdx, maxLonIdx = np.argmin(np.abs(lons -bottomLeftPoint_shape.x)), np.argmin(np.abs(lons -topRightPoint_shape.x))

      data_query_array = self.get_subset_as_array(var, starts=[startTime_idx,minLatIdx,minLonIdx], ends=[endTime_idx,maxLatIdx,maxLonIdx], strides =  [time_stride,lat_stride,lon_stride])
      if verbose:
          print(f""" 
          The following bottom left, {str(bottomLeftPoint)}, and top right {str(topRightPoint)} Points of the grid were provided.
          As the grid corners must correspond to the dataset's underlying grid these points were snapped to the following points: 
          bottom left, {str('Point('+str(lons[minLonIdx]) + " " + str(lats[minLatIdx]) +")")}, and top right {str('Point('+str(lons[maxLonIdx]) + " " + str(lats[maxLatIdx])+")")}""")
          print(f"""
          The returned numpy array will have the following shape: {str(data_query_array.shape)}
          The first array dimension is time with length {str(data_query_array.shape[0])}

          The second array dimension is a south-north vector with length {str(data_query_array.shape[1])} where the index = 0 is the southern most point of the grid {str(lats[minLatIdx])}
          Incrementing at {str(round(spacingLat,2))} degree per 1 increase in index ending at {str(lats[maxLatIdx])}.

          The third array dimension is a west-east vector with length {str(data_query_array.shape[2])} where the index = 0 is the eastern most point of the grid {str(lons[minLonIdx])}
          Incrementing at {str(round(spacingLon,2))} degree per 1 increase in index ending at {str(lons[maxLonIdx])}.
              """)
      return data_query_array

    def get_key_variables(self):
      """
      Get the keys for an Eratos gridded dataset's variable(s).

      Returns
      -------
      arr
          A list of the dataset's variable key(s).
      """
      gs_vars = self._resource.prop('variables')
      var_list = []

      for var in gs_vars:

        var_list.append(var['key'])

      return var_list
