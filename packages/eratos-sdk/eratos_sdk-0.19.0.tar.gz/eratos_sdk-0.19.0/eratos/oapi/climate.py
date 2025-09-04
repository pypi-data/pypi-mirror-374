import tempfile
import os

from shapely import wkt
from shapely.geometry import Point

import numpy as np
from netCDF4 import Dataset

from .search import SearchAdapter

def list_variables(adapter, query='*', cordexVariable=None):
    props = {
        'Query': query,
        'Count': 500,
        'Type': 'https://schemas.eratos.ai/json/variable',
        'Functions': {}
    }
    if cordexVariable is not None:
        props['Functions']['fn[cordexVariable,eq]'] = cordexVariable
    lv = []
    for v in adapter.search_resources(props=props):
        lv += [[v.id(), v.content['name']]]
    return lv

def list_models(adapter, query='*', cordexDrivingModelId=None):
    props = {
        'Query': query,
        'Count': 500,
        'Type': 'https://schemas.eratos.ai/json/model',
        'Functions': {}
    }
    if cordexDrivingModelId is not None:
        props['Functions']['fn[cordexDrivingModelId,eq]'] = cordexDrivingModelId
    lv = []
    for v in adapter.search_resources(props=props):
        lv += [[v.id(), v.content['name']]]
    return lv

def list_scenarios(adapter, query='*', cordexExperimentId=None):
    props = {
        'Query': query,
        'Count': 500,
        'Type': 'https://schemas.eratos.ai/json/scenario',
        'Functions': {}
    }
    if cordexExperimentId is not None:
        props['Functions']['fn[cordexExperimentId,eq]'] = cordexExperimentId
    lv = []
    for v in adapter.search_resources(props=props):
        lv += [[v.id(), v.content['name']]]
    return lv

def list_coverages(adapter, query='*', key=None):
    props = {
        'Query': query,
        'Count': 500,
        'Type': 'https://schemas.eratos.ai/json/coverage',
        'Functions': {}
    }
    if key is not None:
        props['Functions']['fn[key,eq]'] = key
    lv = []
    for v in adapter.search_resources(props=props):
        lv += [[v.id(), v.content['name']]]
    return lv

def list_solvers(adapter, query='*', cordexModelId=None):
    props = {
        'Query': query,
        'Count': 500,
        'Type': 'https://schemas.eratos.ai/json/solver',
        'Functions': {}
    }
    if cordexModelId is not None:
        props['Functions']['fn[cordexModelId,eq]'] = cordexModelId
    lv = []
    for v in adapter.search_resources(props=props):
        lv += [[v.id(), v.content['name']]]
    return lv

def list_time_periods(adapter, query='*', cordexFrequency=None):
    props = {
        'Query': query,
        'Count': 500,
        'Type': 'https://schemas.eratos.ai/json/timerange',
        'Functions': {}
    }
    if cordexFrequency is not None:
        props['Functions']['fn[cordexFrequency,eq]'] = cordexFrequency
    lv = []
    for v in adapter.search_resources(props=props):
        lv += [[v.id(), v.content['name']]]
    return lv

def list_datasets(adapter, query='*', coverage=None, scenario=None, solver=None, model=None, variable=None, timePeriod=None, lat=None, lon=None,
  cordexVariable=None, cordexModelId=None, cordexDrivingModelId=None, cordexExperimentId=None, cordexFrequency=None, cordexDrivingModelEnsembleMember=None):
    if variable is not None and cordexVariable is not None:
        raise Exception('variable and cordexVariable must not be specified together')
    if solver is not None and cordexModelId is not None:
        raise Exception('solver and cordexModelId must not be specified together')
    if model is not None and cordexDrivingModelId is not None:
        raise Exception('model and cordexDrivingModelId must not be specified together')
    if scenario is not None and cordexExperimentId is not None:
        raise Exception('scenario and cordexExperimentId must not be specified together')
    if timePeriod is not None and cordexFrequency is not None:
        raise Exception('timePeriod and cordexFrequency must not be specified together')
    props = {
        'Query': query,
        'Count': 500,
        'Type': 'https://schemas.eratos.ai/json/dataset',
        'Functions': {}
    }
    if coverage is not None:
        props['Functions']['fn[coverage,eq]'] = coverage
    if scenario is not None:
        props['Functions']['fn[scenario,eq]'] = scenario
    if solver is not None:
        props['Functions']['fn[solver,eq]'] = solver
    if model is not None:
        props['Functions']['fn[resultOf,eq]'] = model
    if variable is not None:
        props['Functions']['fn[resultIs,eq]'] = variable
    if timePeriod is not None:
        props['Functions']['fn[aggregatePeriod,eq]'] = timePeriod
    if lat is not None and lon is not None:
        props['Lat'] = lat
        props['Lon'] = lon
    if cordexVariable is not None:
        props['Functions']['fn[cordexVariable,eq]'] = cordexVariable
    if cordexModelId is not None:
        props['Functions']['fn[cordexModelId,eq]'] = cordexModelId
    if cordexDrivingModelId is not None:
        props['Functions']['fn[cordexDrivingModelId,eq]'] = cordexDrivingModelId
    if cordexExperimentId is not None:
        props['Functions']['fn[cordexExperimentId,eq]'] = cordexExperimentId
    if cordexFrequency is not None:
        props['Functions']['fn[cordexFrequency,eq]'] = cordexFrequency
    if cordexDrivingModelEnsembleMember is not None:
        props['Functions']['fn[cordexDrivingModelEnsembleMember,eq]'] = cordexDrivingModelEnsembleMember
    lv = []
    for v in adapter.search_resources(props=props):
        lv += [[v.id(), v.content['name']]]
    return lv

def list_dataset_facets(adapter, query='*', coverage=None, scenario=None, solver=None, model=None, variable=None, timePeriod=None,
  cordexVariable=None, cordexModelId=None, cordexDrivingModelId=None, cordexExperimentId=None, cordexFrequency=None, cordexDrivingModelEnsembleMember=None):
    if variable is not None and cordexVariable is not None:
        raise Exception('variable and cordexVariable must not be specified together')
    if solver is not None and cordexModelId is not None:
        raise Exception('solver and cordexModelId must not be specified together')
    if model is not None and cordexDrivingModelId is not None:
        raise Exception('model and cordexDrivingModelId must not be specified together')
    if scenario is not None and cordexExperimentId is not None:
        raise Exception('scenario and cordexExperimentId must not be specified together')
    if timePeriod is not None and cordexFrequency is not None:
        raise Exception('timePeriod and cordexFrequency must not be specified together')
    props = {
        'Query': query,
        'Count': 1,
        'Type': 'https://schemas.eratos.ai/json/dataset',
        'Functions': {}
    }
    if coverage is not None:
        props['Functions']['fn[coverage,eq]'] = coverage
    if scenario is not None:
        props['Functions']['fn[scenario,eq]'] = scenario
    if solver is not None:
        props['Functions']['fn[solver,eq]'] = solver
    if model is not None:
        props['Functions']['fn[resultOf,eq]'] = model
    if variable is not None:
        props['Functions']['fn[resultIs,eq]'] = variable
    if timePeriod is not None:
        props['Functions']['fn[aggregatePeriod,eq]'] = timePeriod
    if cordexVariable is not None:
        props['Functions']['fn[cordexVariable,eq]'] = cordexVariable
    if cordexModelId is not None:
        props['Functions']['fn[cordexModelId,eq]'] = cordexModelId
    if cordexDrivingModelId is not None:
        props['Functions']['fn[cordexDrivingModelId,eq]'] = cordexDrivingModelId
    if cordexExperimentId is not None:
        props['Functions']['fn[cordexExperimentId,eq]'] = cordexExperimentId
    if cordexFrequency is not None:
        props['Functions']['fn[cordexFrequency,eq]'] = cordexFrequency
    if cordexDrivingModelEnsembleMember is not None:
        props['Functions']['fn[cordexDrivingModelEnsembleMember,eq]'] = cordexDrivingModelEnsembleMember
    adp = SearchAdapter(adapter, props=props)
    adp.perform_request()
    return adp.facets

def list_datasets_for_locs(adapter, locs, query='*', scenario=None, solver=None, model=None, variable=None, timePeriod=None,
  cordexVariable=None, cordexModelId=None, cordexDrivingModelId=None, cordexExperimentId=None, cordexFrequency=None, cordexDrivingModelEnsembleMember=None):
    # Get the possible coverages.
    fcts = list_dataset_facets(adapter, query, scenario=scenario, solver=solver, model=model, variable=variable, timePeriod=timePeriod,
            cordexVariable=cordexVariable, cordexModelId=cordexModelId, cordexDrivingModelId=cordexDrivingModelId, cordexExperimentId=cordexExperimentId,
            cordexFrequency=cordexFrequency, cordexDrivingModelEnsembleMember=cordexDrivingModelEnsembleMember)
    scns = list(fcts['scenario'].keys())
    scns_res = {}
    for did in scns:
        scns_res[did] = adapter.Resource(id=did)
    mdls = list(fcts['resultOf'].keys())
    mdls_res = {}
    for did in mdls:
        mdls_res[did] = adapter.Resource(id=did)
    cvgs = list(fcts['coverage'].keys())
    cvgs_res = {}
    cvgs_geo = {}
    for did in cvgs:
        cvgs_res[did] = adapter.Resource(id=did)
        cvgs_geo[did] = cvgs_res[did].get_geo()
    # Sort the locs into coverage areas.
    valid_coverages = []
    cov_pmap = [None for i in range(len(locs))]
    for j in range(len(locs)):
        lpt = Point(locs[j][0], locs[j][1])
        n = None
        br = 1.0e38
        for cvid in cvgs:
            rk = cvgs_res[cvid].content['key']
            rsplt = rk.split('-')
            if cvgs_geo[cvid].contains(lpt):
                brn = float(rsplt[1])
                if brn < br:
                    n = cvid
                    br = brn
        cov_pmap[j] = n
        if n is not None and n not in valid_coverages:
            valid_coverages += [n]
    first_dataset = None
    datasets = {}
    for cov in valid_coverages:
        if cov not in datasets:
            datasets[cov] = {}
        for scn in scns:
            if scn not in datasets[cov]:
                datasets[cov][scn] = {}
            for mdl in mdls:
                dsets = list_datasets(adapter, query, coverage=cov, scenario=scn, solver=solver, model=mdl, variable=variable, timePeriod=timePeriod,
                                        cordexVariable=cordexVariable, cordexModelId=cordexModelId, cordexDrivingModelId=cordexDrivingModelId, cordexExperimentId=cordexExperimentId,
                                        cordexFrequency=cordexFrequency, cordexDrivingModelEnsembleMember=cordexDrivingModelEnsembleMember)
                if len(dsets) > 1:
                    raise Exception('multiple datasets for coverage, model, and scenario found')
                elif len(dsets) == 1:
                    datasets[cov][scn][mdl] = dsets[0][0]
                    if first_dataset is None:
                        first_dataset = dsets[0][0]
                else:
                    datasets[cov][scn][mdl] = None
    return {
        'coverages': list([cvgs_res[id] for id in valid_coverages]),
        'scenarios': list([scns_res[id] for id in scns]),
        'models': list([mdls_res[id] for id in mdls]),
        'datasets': datasets,
        'first_dataset': first_dataset,
        'cov_pmap': cov_pmap
    }

def fetch_res_data(adapter, cvg_loc, did):
    res = adapter.Resource(id=did[0])
    print(res.content['name'])
    res_gapi = res.data().gapi()
    return res_gapi.get_point_slices(res.content['resultKey'], 'SPP', cvg_loc, starts=[0], ends=[-1], strides=[1])

def fetch_datasets_for_locs(adapter, locs, query='*', scenario=None, solver=None, model=None, variable=None, timePeriod=None,
  cordexVariable=None, cordexModelId=None, cordexDrivingModelId=None, cordexExperimentId=None, cordexFrequency=None, cordexDrivingModelEnsembleMember=None):
    # Convert locs if req.
    for i in range(len(locs)):
        if type(locs[i]) is str:
            pt = wkt.loads(locs[i])
            locs[i] = [pt.x, pt.y]
    sl = list_datasets_for_locs(adapter, locs, query=query, scenario=scenario, solver=solver, model=model, variable=variable, timePeriod=timePeriod,
            cordexVariable=cordexVariable, cordexModelId=cordexModelId, cordexDrivingModelId=cordexDrivingModelId, cordexExperimentId=cordexExperimentId,
            cordexFrequency=cordexFrequency, cordexDrivingModelEnsembleMember=cordexDrivingModelEnsembleMember)
    # if 'VIC-05' in sl['@dss']:
    #     n = -1
    #     for i in range(len(sl['@dss']['VIC-05'])):
    #         if sl['@dss']['VIC-05'][i][0] == 'https://e-pn.io/resources/e6lvcqn6cvyjblukxkbyobzr':
    #             n = i
    #             break
    #     if n >= 0:
    #         del sl['@dss']['VIC-05'][n]
    # Get the times
    tres = adapter.Resource(id=sl['first_dataset'])
    ts_gapi = tres.data().gapi()
    time = ts_gapi.get_subset_as_array('time', starts=[0], ends=[-1], strides=[1])
    # Fetch the data, in parallel.
    data_cvg = np.empty((len(locs), len(sl['scenarios']), len(sl['models']), time.shape[0]))
    for cov, i in zip(sl['coverages'], range(len(sl['coverages']))):
        # Skip any coverages we don't have points in.
        loc_p = []
        cvg_loc = []
        for j in range(len(sl['cov_pmap'])):
            if sl['cov_pmap'][j] == cov.id():
                loc_p += [j]
                cvg_loc += [[locs[j][1], locs[j][0]]]
        for scn, j in zip(sl['scenarios'], range(len(sl['scenarios']))):
            for mdl, k in zip(sl['models'], range(len(sl['models']))):
                ds = sl['datasets'][cov.id()][scn.id()][mdl.id()]
                if ds is None:
                    continue
                res = adapter.Resource(id=ds)
                print(res.content['name'])
                ds_gapi = res.data().gapi()
                data = ds_gapi.get_point_slices(res.content['resultKey'], 'SPP', cvg_loc, starts=[0], ends=[-1], strides=[1])
                for p in range(len(loc_p)):
                    data_cvg[loc_p[p],j,k,:] = data[p,:]
    return data_cvg, list(r.content['name'] for r in sl['scenarios']), list(r.content['name'] for r in sl['models']), time


def push_timeseries_dataset(adapter, extId, varName, lat, lon, locId, times, data):
    times = np.asarray(times)
    data = np.asarray(data)

    if varName not in ['max_temp', 'min_temp']:
        raise ValueError('varName should be one of max_temp/min_temp')

    varUnits = 'degrees'
    if varName == 'max_temp':
        varLongName = 'maximum temperature'
    else:
        varLongName = 'minimum temperature'

    # Create the resource.
    dd = adapter.search('*', ext_source=extId)
    if len(dd['resources']) > 0:
        res = adapter.Resource(id=dd['resources'][0]['@id'])
    else:
        res = adapter.Resource(content={
            '@type': 'https://schemas.eratos.ai/json/dataset.timeseries',
            '@externalSources': [extId],
            'name': '%s at %.6f, %.6f' % (varLongName.title(), lon, lat), 
            'location': locId,
            'resultKey': 'varName',
            'resultIs': 'https://e-pn.io/resources/dhuir4hce7uaamotwhohvlmq',
            'valueRange': [np.min(data), np.max(data)],
            'aggregateFunction': 'https://e-pn.io/resources/yoxkydcksdf67j2iiyznxo2r',
            'aggregatePeriod': 'https://e-pn.io/resources/lo75bhkh6yjx2dpom52wpgw5',
            'timeKey': 'unix'
        })
        res.save()

    # Create the dataset.
    rd = res.data()
    if not rd.is_valid():
        fileName = 'obs-%s.nc' % varName
        filePath = os.path.join(tempfile.mkdtemp(), fileName)
        outputgrp = Dataset(filePath, 'w', format='NETCDF4')
        outputgrp.createDimension('time', None)
        inp_times = outputgrp.createVariable('time','f8',('time',))
        inp_times.axis = 'T'
        inp_times.units = 'seconds since 1970-01-01 00:00:00'
        inp_times.standard_name = 'time'
        inp_times.long_name = 'time'
        inp_times.calendar = 'gregorian'
        inp_times[:] = times[:]
        inp_val = outputgrp.createVariable(varName,'f4', ('time',), zlib=True, complevel=8, fill_value=9.96921e+36)
        inp_val.units = varUnits
        inp_val.standard_name = varName
        inp_val.long_name = varLongName
        inp_val.latitude = lat
        inp_val.longitude = lon
        inp_val[:] = data[:]
        outputgrp.close()

        rd.push_files([filePath], 'au-1.e-gn.io', geom={
            "dimensions": {
                "time": {
                    "data": "time",
                    "size": times.shape[0]
                }
            },
            "spaces": {
                "time": {
                    "dimensions": [
                        "time"
                    ],
                    "type": "structured"
                },
            },
            "variables": {
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
                                times.shape[0]
                            ],
                            "starts": [
                                0
                            ],
                            "varPath": varName
                        }
                    },
                    "space": "time"
                },
            },
        })

        os.remove(filePath)

    return res.id()

def push_grid_timeseries_dataset(adapter, extId, dsName, varName, lat, lon, times, data):
    lat = np.asarray(lat)
    lon = np.asarray(lon)
    times = np.asarray(times)
    data = np.asarray(data).reshape(times.shape[0], lat.shape[0], lon.shape[0])

    if varName not in ['max_temp', 'min_temp']:
        raise ValueError('varName should be one of max_temp/min_temp')

    varUnits = 'degrees'
    if varName == 'max_temp':
        varLongName = 'maximum temperature'
    else:
        varLongName = 'minimum temperature'

    # Create the resource.
    dd = adapter.search('*', ext_source=extId)
    if len(dd['resources']) > 0:
        res = adapter.Resource(id=dd['resources'][0]['@id'])
    else:
        res = adapter.Resource(content={
            '@type': 'https://schemas.eratos.ai/json/dataset',
            'name': dsName,
            'resultIs': 'https://e-pn.io/resources/gmbgflmfirf2ezx7uufjmwlm',
            'aggregateFunction': 'https://e-pn.io/resources/cookjlnngnhvoo27rzpszdc4' if varName == 'max_temp' else 'https://e-pn.io/resources/2rzhu4wo4zfwwngr3znv77p6',
            'aggregatePeriod': 'https://e-pn.io/resources/lo75bhkh6yjx2dpom52wpgw5',
            'resultKey': varName,
            'sourceDescription': 'These datasets were generated by Eratos.',
            'sourceLinks': {
                'License': 'https://creativecommons.org/licenses/by/4.0/'
            },
            'valueRange': [np.min(data), np.max(data)],
            'timeKey': 'unix',
            'sourceCite': 'Eratos'
        })
        res.save()

    # Create the dataset.
    rd = res.data()
    if not rd.is_valid():
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

        rd.push_files([filePath], 'au-1.e-gn.io', geom={
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

    return res.id()
