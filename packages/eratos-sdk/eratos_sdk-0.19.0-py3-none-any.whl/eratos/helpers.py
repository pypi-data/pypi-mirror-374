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

import csv
import json
import os

from netCDF4 import Dataset
from tabulate import tabulate

from .adapter import CachedPoolAdapter
from .resource import Resource
from .ern import Ern

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


def print_gridded_dataset_meta_data(adapter, block_ERN):
    """
    Prints the metadata for a given gridded dataset within Eratos.

    Parameters
    ----------
    adapter : Adapter
      The adapter with valid credentials to interact with the gridded dataset.
    block_ERN : Ern
      The unique Eratos Resource Name (ERN) to the block containing the gridded dataset.
    """
    if type(block_ERN) is str:
      ern = Ern(ern=block_ERN)
    elif type(block_ERN) is Resource:
      ern = block_ERN.ern()
    elif type(block_ERN) is Ern:
      ern = block_ERN
    else:
      raise ValueError('Block ERN should be a string, eratos resource or eratos ern')

    input_res = adapter.Resource(ern=ern)      
    input_keys = input_res.props().keys()
    edata_gridded = input_res.data().gapi()
    times = edata_gridded.get_subset_as_array('time')
    lats = edata_gridded.get_subset_as_array('lat')
    lons = edata_gridded.get_subset_as_array('lon')
    spacingLat, spacingLon, spacingTime = lats[1]-lats[0], lons[1]-lons[0], times[1] - times[0]
    creator_L_name = adapter.Resource(ern = input_res.props()['creator']).props()['legalName']
    
    name = input_res.props()['name']
    short_descript = input_res.props()['shortDescription']
    primary_dataset = input_res.props()['primary']
    dataset_res = adapter.Resource(primary_dataset)
    if 'temporalFrequency' in dataset_res.props():
      temporalFrequency = dataset_res.props()['temporalFrequency']
    else:
      temporalFrequency = 'no temporal frequency defined'
    if 'temporalRange' in dataset_res.props():
      temporalRange = dataset_res.props()['temporalRange']
    else:
      temporalRange = 'no temporal range defined'
    variables = dataset_res.props()['variables']
    #var_num = variables['variables@count']
    
    var_key = variables[0]['key']
    var_name = variables[0]['name']

    ds_grid = dataset_res.props()['grid']
    ds_grid_type = ds_grid['type']
    
    head = ['Var key','Unit','Spacing','Spacing Value']
    print_table = [head]
    for grid_dim in ds_grid['dimensions']:
        grid_Var = []
        grid_Var.append(grid_dim['key'])
        grid_Var.append(adapter.Resource(ern = grid_dim['unit']).props()['name'])
        grid_Var.append(grid_dim['spacing'])
        if grid_dim['key'] == 'time':
            grid_Var.append(str(spacingTime))
        if grid_dim['key'] == 'lat':
            grid_Var.append(str(spacingLat))
        if grid_dim['key'] == 'lon':
            grid_Var.append(str(spacingLon))
        print_table.append(grid_Var)

    print(f"""
The Key Metadata for the {str(name)} dataset is as follows:

{str(short_descript)}

Creator: {str(creator_L_name)}
temporalFrequency: {str(temporalFrequency)} 
temporalRange: {str(temporalRange)} 
Dependent Variable Name: {str(var_name)} 
Dependent Variable Key: {str(var_key)} 
Dataset Grid Type: {str(ds_grid_type)} 

Grid Dimensions    
    """) 
    print(tabulate(print_table, headers='firstrow', tablefmt='fancy_grid'))
    print(" ")   

    return

def write_dataset_block_meta(fpath, resIter, propMap, verbose=False):
  # Sanitise inputs.
  if type(fpath) is not str:
    raise TypeError('fpath should be a string')
  try:
    iter(resIter)
  except TypeError:
    raise TypeError('resIter should be a resource iterator')
  if type(propMap) is not dict:
    raise TypeError('fpath should be a dict')
  bn, fext = os.path.splitext(fpath)
  fext = fext.lower()
  if fext not in ['.json', '.csv']:
    raise TypeError('fpath should have a csv or json extension')
  # Create the base path if it doesn't already exist.
  fdir = os.path.dirname(fpath)
  if fdir != '' and not os.path.exists(fdir):
    os.makedirs(fdir)
  # Create a pooled adapter for the duration of the request.
  resCnt = len(resIter)
  if resCnt > 0:
    origAdapter = resIter[0]._adapter
    adp = CachedPoolAdapter(origAdapter, 86400)
    for i in range(resCnt):
      resIter[i]._adapter = adp
  # Construct the data from the mapping.
  # Note we are not streaming the content, TODO: future opt.
  propKeys = list(propMap.keys())
  data = []
  if fext == '.csv':
    data += [list([k for k in propKeys])]
  for res, i in zip(resIter, range(resCnt)):
    if verbose and (i % 100) == 0:
      print('Exporting resources % 5d ... %d / %d' % (i, min(i+100, resCnt), resCnt))
    if fext == '.csv':
      row = []
      for k in propKeys:
        row += [res.prop_path(propMap[k], None, sep=';')]
      data += [row]
    else:
      elem = {}
      for k in propKeys:
        elem[k] = res.prop_path(propMap[k], None, sep=';')
  # Write the data.
  if fext == '.csv':
    with open(fpath, 'w+', newline='') as f:
      csvwtr = csv.writer(f)
      csvwtr.writerows(data)
  else:
    with open(fpath, 'w+', newline='') as f:
      json.dump(data, f, indent=2)
  # Reset to the original adapter.
  for i in range(resCnt):
    resIter[i] = origAdapter
