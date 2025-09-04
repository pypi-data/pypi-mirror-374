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

from netCDF4 import Dataset

def join_pfx(pfx, name):
  if pfx == "":
    return name
  else:
    return pfx+"/"+name

def get_ncdf_dims(grp, d):
  res = {}
  for k in d.dimensions:
    p = join_pfx(grp, k)
    res[p] = {
      "size": d.dimensions[k].size,
      "data": None
    }
  for k in d.groups:
    res.update(get_ncdf_dims(join_pfx(grp, k), d.groups[k]))
  return res

def get_ncdf_vars(grp, d):
  res = {}
  for k in d.variables:
    p = join_pfx(grp, k)
    res[p] = {
      "type": 'f4',
      "dimensions": list(d.variables[k].dimensions)
    }
  for k in d.groups:
    res.update(get_ncdf_vars(join_pfx(grp, k), d.groups[k]))
  return res

def get_ncdf_varsex(grp, d):
  vkeys = [
    'unit',
    'units',
    'long_name',
    'standard_name',
    'calendar',
    'axis'
  ]
  res = {}
  for k in d.variables:
    p = join_pfx(grp, k)
    res[p] = {}
    for v in vkeys:
      try:
        res[p][v] = d.variables[k].getncattr(v)
      except:
        pass
  for k in d.groups:
    res.update(get_ncdf_vars(join_pfx(grp, k), d.groups[k]))
  return res

def guess_netcdf_api(file, dims={}):
  ds = Dataset(file, "r", format="NETCDF4")
  # Extract the data.
  dd = get_ncdf_dims("", ds)
  vv = get_ncdf_vars("", ds)
  ve = get_ncdf_varsex("", ds)
  # Map the dimension data.
  for k in dd.keys():
    if k in dims and dims[k] in vv:
      dd[k]['data'] = dims[k]
    elif k in vv:
      dd[k]['data'] = k
    else:
      raise Exception("could not determine dimension data")
  # Generate the api structure.
  api = {
    "type": "structured",
    "content": "netcdf4",
    "dimensions": dd,
    "variables": vv
  }
  # Get global attributes.
  gattr = {}
  for k in ds.ncattrs():
    gattr[k.lower()] = getattr(ds, k)
  return api, ve, gattr
