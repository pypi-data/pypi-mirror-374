import tempfile
import os

from shapely import wkt, geometry
from shapely.geometry import Point

import numpy as np
from netCDF4 import Dataset

from .ern import Ern
from .search import SearchAdapter
from .resource import Resource
import datetime

climateMetaMap = {
    'ERN': '@id',
    'Name': 'name',
    'Variable ERNs': 'primary.variables.is',
    'Variable Names': 'primary.variables.is.name',
    'Region ERN': 'primary.region',
    'Region Name': 'primary.region.name',
    'Model ERN': 'primary.model',
    'Model Name': 'primary.model.name',
    'Temporal Frequency': 'primary.temporalFrequency',
    'Cordex Variable Key': 'primary.climate.cordex.variable',
    'Cordex Model Key': 'primary.climate.cordex.modelId',
    'Cordex Experiment Key': 'primary.climate.cordex.experimentId',
    'Cordex Frequency Key': 'primary.climate.cordex.frequency',
    'Cordex Driving Model Key': 'primary.climate.cordex.drivingModelId',
    'Cordex Driving Model Ensemble Member Key': 'primary.climate.cordex.drivingModelEnsembleMember',
    'Cordex Driving Experiment Key': 'primary.climate.cordex.drivingExperimentName'
}

def list_variables(adapter, query='*', cordexVariable=None):
    """
    Lists the variables available.

    list_variables() returns a list of matching variable ERNs (can be empty) according to specific query parameters for a given adapter.

    Parameters
    ----------
    adapter : Adapter
        The Eratos adpater to query.
    query : str
        String to query. (Default value is '*')
    cordexVariable : str
        A CORDEX specific string to search on. (Default value is None)

    Returns
    -------
    arr
        An empty list or a list of unique Eratos Resource Name (ERN) strings of type Variable.
    """
    props = {
        'query': query,
        'limit': 100,
        'type': 'ern:e-pn.io:schema:variable'
    }
    if cordexVariable is not None:
        props['fn[climate.cordex.variable,eq]'] = cordexVariable
    return adapter.search_resources(**props)

def list_regions(adapter, query='*', regionSet=None, cordexDomain=None, lat=None, lon=None, location=None):
    """
    Lists the regions available.

    list_regions() returns a list of matching regions (can be empty) according to specific query parameters for a given adapter.

    Parameters
    ----------
    adapter : Adapter
        The Eratos adpater to query.
    query : str
        String to query. (Default value is '*')
    regionSet : str
        A specific regions string to search on. (Default value is None)
    cordexDomain : str
        A CORDEX specific domain string to search on. (Default value is None)
    lat : str
        A specific latitude to search on. (Default value is None)
    lon : str
        A specific longitude to search on. (Default value is None)
    location : str
        A specific location to search within. Can be an ERN or a WKT location string. (Default value is None)

    Returns
    -------
    arr
        An empty list or a list of unique region Eratos Resource Names (ERNs).
    """
    if lat is not None and location is not None:
        raise Exception('lat or lon and location must not be specified together')

    props = {
        'query': query,
        'limit': 100,
        'type': 'ern:e-pn.io:schema:location',
        'fn[featureType,eq]': 'ClimateRegion',
    }
    if regionSet is not None:
        props['fn[featureSet,eq]'] = regionSet
    if cordexDomain is not None:
        props['fn[climate.cordex.domain,eq]'] = cordexDomain
    if lat is not None and lon is not None:
        props['geom'] = 'POINT(%f %f)' % (lon, lat)
    if location is not None:
        if type(location) is str:
            try:
                if location[:4] == "ern:":
                    Ern(location)   # Validate ERN
                    props['geom'] = location
                else:
                    wkt.loads(location) # Validate WKT
                    props['geom'] = location
            except:
                raise ValueError('value inside location should be a valid resource ERN or WKT string')
        elif type(location) is Resource:
            if location.has_geo():
                props['geom'] = str(location.ern())
            else:
                raise Exception('the location input is a resource without a geometry, please add a geometry or enter a resource that contains one')
        elif isinstance(location, geometry):
            props['geom'] = wkt.dumps(location)
        else:
            raise TypeError('location should either be a resource, WKT string, or geometry')
            
    return adapter.search_resources(**props)

def list_models(adapter, query='*', cordexDrivingModelId=None):
    """
    Lists the models available.

    list_models() returns a list of matching model ERNs (can be empty) according to specific query parameters for a given adapter.

    Parameters
    ----------
    adapter : Adapter
        The Eratos adpater to query.
    query : str
        String to query. (Default value is '*')
    cordexDrivingModelId : str
        A CORDEX specific string to search on. (Default value is None)

    Returns
    -------
    arr
        An empty list or a list of unique Eratos Resource Name (ERN) strings of type Model.
    """
    props = {
        'query': query,
        'limit': 100,
        'type': 'ern:e-pn.io:schema:model'
    }
    if cordexDrivingModelId is not None:
        props['fn[climate.cordex.drivingModelId,eq]'] = cordexDrivingModelId
    return adapter.search_resources(**props)

def list_experiments(adapter, query='*', cordexExperimentId=None):
    """
    Lists the experiments available.

    list_experiments() returns a list of matching scenario ERNs (can be empty) according to specific query parameters for a given adapter.

    Parameters
    ----------
    adapter : Adapter
        The Eratos adpater to query.
    query : str
        String to query. (Default value is '*')
    cordexExperimentId : str
        A CORDEX specific string to search on. (Default value is None)

    Returns
    -------
    arr
        An empty list or a list of unique Eratos Resource Name (ERN) strings of type Scenario, containing climate experiments.
    """
    props = {
        'query': query,
        'limit': 100,
        'type': 'ern:e-pn.io:schema:scenario'
    }
    if cordexExperimentId is not None:
        props['fn[climate.cordex.experimentId,eq]'] = cordexExperimentId
    return adapter.search_resources(**props)

# TODO: can this be deleted? renamed to list_experiment_models?
# def list_experiments(adapter, query='*', cordexModelId=None):
#     props = {
#         'query': query,
#         'limit': 100,
#         'type': 'ern:e-pn.io:schema:experiment'
#     }
#     if cordexModelId is not None:
#         props['fn[climate.cordex.modelId,eq]'] = cordexModelId
#     return adapter.search_resources(**props)

def _conv_ern(name, val):
    if type(val) is str:
        return val
    elif type(val) is Ern:
        return str(val)
    elif type(val) is Resource:
        return str(val.ern())
    else:
        raise TypeError(f'expected {name} to be a string, Ern, or Resource')

def _conv_ern_list(name, val):
    if type(val) is list:
        return list([_conv_ern(name, v) for v in val])
    else:
        return _conv_ern(name, val)

def _create_dataset_query(adapter, query='*', scenario=None, experiment=None, model=None, variable=None, region=None, temporalFrequency=None, lat=None, lon=None, location=None,
  cordexVariable=None, cordexModelId=None, cordexDrivingModelId=None, cordexExperimentId=None, cordexFrequency=None, cordexDrivingModelEnsembleMember=None, cordexDomain=None):
    if variable is not None and cordexVariable is not None:
        raise Exception('variable and cordexVariable must not be specified together')
    if experiment is not None and cordexModelId is not None:
        raise Exception('solver and cordexModelId must not be specified together')
    if model is not None and cordexDrivingModelId is not None:
        raise Exception('model and cordexDrivingModelId must not be specified together')
    if scenario is not None and cordexExperimentId is not None:
        raise Exception('scenario and cordexExperimentId must not be specified together')
    if temporalFrequency is not None and cordexFrequency is not None:
        raise Exception('timePeriod and cordexFrequency must not be specified together')
    if region is not None and cordexDomain is not None:
        raise Exception('region and cordexDomain must not be specified together')
    if lat is not None and location is not None:
        raise Exception('lat or lon and location must not be specified together')
    props = {
        'query': query,
        'limit': 100,
        'type': 'ern:e-pn.io:schema:block'
    }
    if scenario is not None:
        props['fn[primary.scenario,eq]'] = _conv_ern_list('scenario', scenario)
    if experiment is not None:
        props['fn[primary.experiment,eq]'] = _conv_ern_list('experiment', experiment)
    if model is not None:
        props['fn[primary.model,eq]'] = _conv_ern_list('model', model)
    if variable is not None:
        props['fn[primary.variables.is,eq]'] = _conv_ern_list('variable', variable)
    if region is not None:
        props['fn[primary.region,eq]'] = _conv_ern_list('region', region)
    if temporalFrequency is not None:
        props['fn[primary.temporalFrequency,eq]'] = temporalFrequency
    if lat is not None and lon is not None:
        props['geom'] = 'POINT(%f %f)' % (lon, lat)
    if location is not None:
        if type(location) is str:
            try:
                if location[:4] == "ern:":
                    Ern(location)   # Validate ERN
                    props['geom'] = location
                else:
                    wkt.loads(location) # Validate WKT
                    props['geom'] = location
            except:
                raise ValueError('value inside location should be a valid resource ERN or WKT string')
        elif type(location) is Resource:
            if location.has_geo():
                props['geom'] = str(location.ern())
            else:
                raise Exception('the location input is a resource without a geometry, please add a geometry or enter a resource that contains one')
        elif isinstance(location, geometry):
            props['geom'] = wkt.dumps(location)
        else:
            raise TypeError('location should either be a resource, WKT string, or geometry')
    if cordexVariable is not None:
        props['fn[primary.climate.cordex.variable,eq]'] = cordexVariable
    if cordexModelId is not None:
        props['fn[primary.climate.cordex.modelId,eq]'] = cordexModelId
    if cordexDrivingModelId is not None:
        props['fn[primary.climate.cordex.drivingModelId,eq]'] = cordexDrivingModelId
    if cordexExperimentId is not None:
        props['fn[primary.climate.cordex.experimentId,eq]'] = cordexExperimentId
    if cordexFrequency is not None:
        props['fn[primary.climate.cordex.frequency,eq]'] = cordexFrequency
    if cordexDrivingModelEnsembleMember is not None:
        props['fn[primary.climate.cordex.drivingModelEnsembleMember,eq]'] = cordexDrivingModelEnsembleMember
    if cordexDomain is not None:
        props['fn[primary.climate.cordex.domain,eq]'] = cordexDomain
    return props

def list_dataset_blocks(adapter, query='*', scenario=None, experiment=None, model=None, variable=None, region=None, temporalFrequency=None, lat=None, lon=None, location=None,
  cordexVariable=None, cordexModelId=None, cordexDrivingModelId=None, cordexExperimentId=None, cordexFrequency=None, cordexDrivingModelEnsembleMember=None, cordexDomain=None):
    """
    Lists the available dataset blocks.

    list_dataset_blocks() returns a list of matching dataset block ERNs (can be empty) according to specific query parameters for a given adapter.

    Parameters
    ----------
    adapter : Adapter
        The Eratos adpater to query.
    query : str
        String to query. (Default value is '*')
    scenario : str
        A specific scenario to search on. (Default value is None)
    experiment : str
        A specific experiment to search on. (Default value is None)
    model : str
        A specific model to search on. (Default value is None)
    variable : str
        A specific variable to search on. (Default value is None)
    region : str
        A specific region to search within. (Default value is None)
    temporalFrequency : str
        A specific temporalFrequency to search on. (Default value is None)
    lat : str
        A specific latitude to search on. (Default value is None)
    lon : str
        A specific longitude to search on. (Default value is None)
    location : str
        A specific location to search within. (Default value is None)
    cordexVariable : str
        A specific CORDEX variable to search on. (Default value is None)
    cordexModelId : str
        A specific CORDEX model ID to search on. (Default value is None)
    cordexDrivingModelId : str
        A specific CORDEX driving model ID to search on. (Default value is None)
    cordexExperimentId : str
        A specific CORDEX experiment ID to search on. (Default value is None)
    cordexFrequency : str
        A specific CORDEX frequency to search on. (Default value is None)
    cordexDrivingModelEnsembleMember : str
        A specific CORDEX driving model ensemble member to search on. (Default value is None)
    cordexDomain : str
        A specific CORDEX domain to search on. (Default value is None)

    Returns
    -------
    arr
        An empty list or a list of unique Eratos Resource Name (ERN) strings of type Block, containing datasets.
    """
    props = _create_dataset_query(adapter, query, scenario, experiment, model, variable, region, temporalFrequency, lat, lon, location,
cordexVariable, cordexModelId, cordexDrivingModelId, cordexExperimentId, cordexFrequency, cordexDrivingModelEnsembleMember, cordexDomain)
    return adapter.search_resources(**props)

def list_dataset_block_facets(adapter, query='*', scenario=None, experiment=None, model=None, variable=None, region=None, temporalFrequency=None, lat=None, lon=None, location=None,
  cordexVariable=None, cordexModelId=None, cordexDrivingModelId=None, cordexExperimentId=None, cordexFrequency=None, cordexDrivingModelEnsembleMember=None, cordexDomain=None):
    """
    Lists the facets available.

    list_dataset_block_facets() returns a list of facets (can be empty) for a dataset block according to specific query parameters for a given adapter.

    Parameters
    ----------
    adapter : Adapter
        The Eratos adpater to query.
    query : str
        String to query. (Default value is '*')
    scenario : str
        A specific scenario to search on. (Default value is None)
    experiment : str
        A specific experiment to search on. (Default value is None)
    model : str
        A specific model to search on. (Default value is None)
    variable : str
        A specific variable to search on. (Default value is None)
    region : str
        A specific region to search within. (Default value is None)
    temporalFrequency : str
        A specific temporalFrequency to search on. (Default value is None)
    lat : str
        A specific latitude to search on. (Default value is None)
    lon : str
        A specific longitude to search on. (Default value is None)
    location : str
        A specific location to search within. (Default value is None)
    cordexVariable : str
        A specific CORDEX variable to search on. (Default value is None)
    cordexModelId : str
        A specific CORDEX model ID to search on. (Default value is None)
    cordexDrivingModelId : str
        A specific CORDEX driving model ID to search on. (Default value is None)
    cordexExperimentId : str
        A specific CORDEX experiment ID to search on. (Default value is None)
    cordexFrequency : str
        A specific CORDEX frequency to search on. (Default value is None)
    cordexDrivingModelEnsembleMember : str
        A specific CORDEX driving model ensemble member to search on. (Default value is None)
    cordexDomain : str
        A specific CORDEX domain to search on. (Default value is None)

    Returns
    -------
    arr
        An empty list or a list of facets.
    """
    props = _create_dataset_query(adapter, query, scenario, experiment, model, variable, region, temporalFrequency, lat, lon, location,
  cordexVariable, cordexModelId, cordexDrivingModelId, cordexExperimentId, cordexFrequency, cordexDrivingModelEnsembleMember, cordexDomain)

    props['limit'] = 1
    props['facets'] = ','.join([
        'primary.scenario',
        'primary.experiment',
        'primary.model',
        'primary.variables.is',
        'primary.region',
        'primary.temporalFrequency',
        'primary.climate.cordex.variable',
        'primary.climate.cordex.modelId',
        'primary.climate.cordex.drivingModelId',
        'primary.climate.cordex.experimentId',
        'primary.climate.cordex.frequency',
        'primary.climate.cordex.drivingModelEnsembleMember',
        'primary.climate.cordex.domain'
    ])

    sadpt = adapter.search_adapter(**props)
    return sadpt.facets()
    
def push_grid_timeseries_dataset(adapter, dsName, varName, lat, lon, times, data):
    """
    Pushes a gridded timeseries dataset for the Thin Plate Spine Interpolation (TPSI) model. (TBC)
    """
    lat = np.asarray(lat)
    lon = np.asarray(lon)
    times = np.asarray(times)
    data = np.asarray(data).reshape(times.shape[0], lat.shape[0], lon.shape[0])
    min_lat = lat[0]
    min_lon = lon[0]
    max_lat = lat[-1]
    max_lon = lon[-1]

    if varName not in ['max_temp', 'min_temp']:
        raise ValueError('varName should be one of max_temp/min_temp')

    #Create metadata
    geo_poly = f'POLYGON(({min_lon} {min_lat}, {max_lon} {min_lat},{max_lon} {max_lat}, {min_lon} {max_lat}, {min_lon} {min_lat}))'
    
    startDate = datetime.datetime.utcfromtimestamp(times[0]).strftime('%Y-%m-%d')
    endDate = datetime.datetime.utcfromtimestamp(times[-1]).strftime('%Y-%m-%d')

    varid = 'ern:e-pn.io:resource:eratos.variable.temperature'
    varUnits = 'ern:e-pn.io:resource:eratos.unit.celsius'

    if varName == 'max_temp':
        varLongName = 'maximum temperature'
        varaggregate = 'ern:e-pn.io:resource:eratos.aggregate.daily.max'
    else:
        varLongName = 'minimum temperature'
        varaggregate = 'ern:e-pn.io:resource:eratos.aggregate.daily.min'

    descr = f'90m {varLongName} data at the chosen location, bounded by Bottom Left Point({min_lon} {min_lat}) and Top Right Point({max_lon} {max_lat})'
    # Create the resource.
    dataset_res = adapter.Resource(content={
        '@type': 'ern:e-pn.io:schema:dataset',
        '@geo': geo_poly,
        'type': 'ern:e-pn.io:resource:eratos.dataset.type.gridded',
        'name': dsName,
        'description': descr,
        'variables': [{
            'key': varName,
            'name': varLongName,
            'is': varid,
            'unit': varUnits,
            'aggregate': varaggregate
        }], #UP TO HERE
        'updateSchedule': 'ern:e-pn.io:resource:eratos.schedule.noupdate',
        'temporalRange': {
            'start': startDate,
            'end': endDate
        },
        'temporalFrequency': 'Daily',
        'grid': {
            'type': 'Rectilinear',
            'dimensions':[
                {
                    'key': 'time',
                    'spacing': 'Uniform',
                    'is': 'ern:e-pn.io:resource:eratos.variable.time',
                    'unit': "ern:e-pn.io:resource:eratos.unit.utcseconds" ,    
                },
                {
                    'key': 'lat',
                    'spacing': 'Uniform',
                    'is': 'ern:e-pn.io:resource:eratos.variable.latitude',
                    'unit': 'ern:e-pn.io:resource:eratos.unit.degrees',
                },
                    {
                    'key': 'lon',
                    'spacing': 'Uniform',
                    'is': 'ern:e-pn.io:resource:eratos.variable.longitude',
                    'unit': 'ern:e-pn.io:resource:eratos.unit.degrees',
                }
            ],
            'geo':{
                'proj': "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs",
                'coords': ["lon", "lat"]
            }

        }
    })
    dataset_res.save()

    # Create the dataset.
    rd = dataset_res.data()
    fileName = 'obs-%s.nc' % varName
    filePath = os.path.join(tempfile.mkdtemp(), fileName)
    outputgrp = Dataset(filePath, 'w', format='NETCDF4')
    outputgrp.createDimension('lat', lat.shape[0])
    outputgrp.createDimension('lon', lon.shape[0])
    outputgrp.createDimension('time', None)
    inp_lat = outputgrp.createVariable('lat', 'f8', ('lat',))
    inp_lat.axis = 'Y'
    inp_lat.units = 'degrees_north'
    inp_lat.standard_name = 'latitude'
    inp_lat.long_name = 'latitude'
    inp_lat[:] = lat[:]
    inp_lon = outputgrp.createVariable('lon', 'f8', ('lon',))
    inp_lon.axis = 'X'
    inp_lon.units = 'degrees_east'
    inp_lon.standard_name = 'longitude'
    inp_lon.long_name = 'longitude'
    inp_lon[:] = lon[:]
    inp_times = outputgrp.createVariable('time', 'f8', ('time',))
    inp_times.axis = 'T'
    inp_times.units = 'seconds since 1970-01-01 00:00:00'
    inp_times.standard_name = 'time'
    inp_times.long_name = 'time'
    inp_times.calendar = 'gregorian'
    inp_times[:] = times[:]
    ch_size = max((8*1024*1024) // (4*lat.shape[0]*lon.shape[0]), 1)
    inp_val = outputgrp.createVariable(varName,'f4', ('time','lat','lon'), zlib=True, chunksizes=(ch_size, lat.shape[0], lon.shape[0]), complevel=8, fill_value=9.96921e+36)
    inp_val.units = varUnits
    inp_val.standard_name = varName
    inp_val.long_name = varLongName
    inp_val[:] = data[:]
    outputgrp.close()

    # Push objects, Mon
    rd.push_objects('ern::node:au-1.e-gn.io', { fileName: filePath }, connector='Objects:Gridded:v1', connectorProps={
        "dimensions": {
            "lat": {
                "data": "lat",
                "size": lat.shape[0]
            },
            "lon": {
                "data": "lon",
                "size": lon.shape[0]
            },
            "time": {
                "data": "time",
                "size": times.shape[0]
            }
        },
        "spaces": {
            "lat": {
                "dimensions": [
                    "lat"
                ],
                "type": "structured"
            },
            "lon": {
                "dimensions": [
                    "lon"
                ],
                "type": "structured"
            },
            "time": {
                "dimensions": [
                    "time"
                ],
                "type": "structured"
            },
            varName: {
                "dimensions": [
                    "time",
                    "lat",
                    "lon"
                ],
                "type": "structured"
            },
        },
        "variables": {
            "lat": {
                "dataType": "f8",
                "slices": {
                    fileName: {
                        "counts": [
                            lat.shape[0]
                        ],
                        "starts": [
                            0
                        ],
                        "varPath": "lat"
                    }
                },
                "space": "lat"
            },
            "lon": {
                "dataType": "f8",
                "slices": {
                    fileName: {
                        "counts": [
                            lon.shape[0]
                        ],
                        "starts": [
                            0
                        ],
                        "varPath": "lon"
                    }
                },
                "space": "lon"
            },
            "time": {
                "dataType": "f8",
                "slices": {
                    fileName: {
                        "counts": [
                            times.shape[0]
                        ],
                        "starts": [
                            0
                        ],
                        "varPath": "time"
                    }
                },
                "space": "time"
            },
            varName: {
                "dataType": "f4",
                "slices": {
                    fileName: {
                        "counts": [
                            times.shape[0],
                            lat.shape[0],
                            lon.shape[0]
                        ],
                        "starts": [
                            0,
                            0,
                            0
                        ],
                        "varPath": varName
                    }
                },
                "space": varName
            },
        },
    })

    os.remove(filePath)

    return dataset_res.ern()
