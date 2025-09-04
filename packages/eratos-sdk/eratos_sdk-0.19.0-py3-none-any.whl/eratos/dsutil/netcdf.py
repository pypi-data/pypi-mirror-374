import logging
import os
import numpy as np
from contextlib import contextmanager
from functools import reduce
from typing import Optional

from netCDF4 import Dataset, num2date

_logger = logging.getLogger(__name__)

_DEFAULT_FILL = {
    "f4": float(np.finfo(np.float32).min),
    "f8": float(np.finfo(np.float64).min),
    "i1": np.iinfo(np.int8).min,
    "i2": np.iinfo(np.int16).min,
    "i4": np.iinfo(np.int32).min,
    "i8": np.iinfo(np.int32).min,
    "u1": np.iinfo(np.uint8).max,
    "u2": np.iinfo(np.uint16).max,
    "u4": np.iinfo(np.uint32).max,
    "u8": np.iinfo(np.uint32).max,
    "c4": float(np.finfo(np.complex64).min),
    "c8": float(np.finfo(np.complex128).min),
}
_MAX_FLOAT64_PRECISION = 2**53 - 1

@contextmanager
def managed_netcdf(*args, **kwds):
    # Code to acquire resource, e.g.:
    dataset = Dataset(*args, **kwds)
    try:
        yield dataset
    finally:
        dataset.close()


def get_netcdf_variable_data(path, varname):
    with managed_netcdf(path, 'r') as nc:
        return nc[varname][:]


def pipe_netcdf_attrs(dstPath, srcPath, excludeDims=[]):
    with managed_netcdf(srcPath, 'r') as src:
        if not os.path.exists(dstPath):
            with managed_netcdf(dstPath, 'w', format='NETCDF4') as dst:
                _pipe_netcdf_attrs(dst, src, excludeDims=excludeDims)
        else:
            with managed_netcdf(dstPath, 'a', format='NETCDF4') as dst:
                _pipe_netcdf_attrs(dst, src, excludeDims=excludeDims)


def pipe_netcdf_var_attr(dstPath, srcPath, vars, **kwargs):
    with managed_netcdf(srcPath, 'r') as src:
        if not os.path.exists(dstPath):
            with managed_netcdf(dstPath, 'w', format='NETCDF4') as dst:
                _pipe_netcdf_var_attr(dst, src, vars, **kwargs)
        else:
            with managed_netcdf(dstPath, 'a', format='NETCDF4') as dst:
                _pipe_netcdf_var_attr(dst, src, vars, **kwargs)


def pipe_netcdf_vars(dstPath, srcPath, vars, **kwargs):
    with managed_netcdf(srcPath, 'r') as src:
        if not os.path.exists(dstPath):
            with managed_netcdf(dstPath, 'w', format='NETCDF4') as dst:
                _pipe_netcdf_vars(dst, src, vars, **kwargs)
        else:
            with managed_netcdf(dstPath, 'a', format='NETCDF4') as dst:
                _pipe_netcdf_vars(dst, src, vars, **kwargs)


def _pipe_netcdf_attrs(dst, src, excludeDims=[]):
    for name in src.ncattrs():
        dst.setncattr(name, getattr(src, name))
    for k in src.dimensions:
        if k in dst.dimensions or k in excludeDims:
            continue
        dst.createDimension(k, size=src.dimensions[k].size)


def get_netcdf_var_fill_val(srcPath, varName):
    with managed_netcdf(srcPath, 'r') as nc:
        return nc[varName]._FillValue


def _add_variable_attr(args, var, key, srcKey=None):
    try:
        if srcKey is None:
            args[key] = var.getncattr(key)
        else:
            args[key] = var.getncattr(srcKey)
        return args
    except AttributeError as e:
        return args


def _calc_num_chunks(size, chunkSize):
    cnt = size // chunkSize
    if size % chunkSize != 0:
        cnt += 1
    return cnt


def _calc_strides(arr):
    return list([reduce(lambda a, b: a * b, arr[i + 1:], 1) for i in range(len(arr))])


def _pipe_netcdf_var_data(dst, src, var, chunkSize):
    if dst[var].ndim != src[var].ndim:
        raise ValueError('dst dimensions does not match src dimensions')
    if dst[var].ndim != len(chunkSize):
        raise ValueError('dst dimensions does not match chunkSize dimensions')
    for i in range(dst[var].ndim):
        if dst[var].shape[i] != src[var].shape[i]:
            raise ValueError('dst dimensions does not match src dimensions')
    numChunks = list([_calc_num_chunks(dst[var].shape[i], chunkSize[i]) for i in range(dst[var].ndim)])
    chunkStrides = _calc_strides(numChunks)
    totalChunks = reduce(lambda a, b: a * b, numChunks, 1)
    for i in range(totalChunks):
        chunkIndex = list([(i // chunkStrides[n]) % numChunks[n] for n in range(dst[var].ndim)])
        dimStarts = list([chunkSize[n] * chunkIndex[n] for n in range(dst[var].ndim)])
        dimEnds = list([min(chunkSize[n] * (chunkIndex[n] + 1), dst[var].shape[n]) for n in range(dst[var].ndim)])
        dataSlice = tuple([slice(dimStarts[n], dimEnds[n], None) for n in range(dst[var].ndim)])
        data = src[var][dataSlice]
        dst[var][dataSlice] = data


def _pipe_netcdf_var_attr(dst, src, vars, **kwargs):
    for vname in vars:
        vdef = src.variables[vname]
        for aname in vdef.ncattrs():
            if aname in ['_FillValue', 'compression', 'zlib']:
                continue
            dst.variables[vname].setncattr(aname, getattr(vdef, aname))


def _pipe_netcdf_vars(dst, src, vars, **kwargs):
    for vname in vars:
        vdef = src.variables[vname]
        chunkszs = []
        if 'chunksizes' in kwargs:
            for i in range(len(kwargs['chunksizes'])):
                if kwargs['chunksizes'][i] is None:
                    chunkszs += [vdef.shape[i]]
                else:
                    chunkszs += [kwargs['chunksizes'][i]]
        if vname not in dst.variables:
            vargs = {}
            vargs = _add_variable_attr(vargs, vdef, 'compression')
            vargs = _add_variable_attr(vargs, vdef, 'zlib')
            vargs = _add_variable_attr(vargs, vdef, 'shuffle')
            vargs = _add_variable_attr(vargs, vdef, 'szip_coding')
            vargs = _add_variable_attr(vargs, vdef, 'szip_pixels_per_block')
            vargs = _add_variable_attr(vargs, vdef, 'blosc_shuffle')
            vargs = _add_variable_attr(vargs, vdef, 'fletcher32')
            vargs = _add_variable_attr(vargs, vdef, 'contiguous')
            vargs = _add_variable_attr(vargs, vdef, 'chunksizes')
            vargs = _add_variable_attr(vargs, vdef, 'endian')
            vargs = _add_variable_attr(vargs, vdef, 'least_significant_digit')
            vargs = _add_variable_attr(vargs, vdef, 'fill_value', srcKey='_FillValue')
            vargs = _add_variable_attr(vargs, vdef, 'chunk_cache')
            for k in kwargs.keys():
                vargs[k] = kwargs[k]
            if 'chunksizes' in kwargs:
                vargs['chunksizes'] = tuple(chunkszs)
            dst.createVariable(vname, vdef.datatype, dimensions=vdef.dimensions, **vargs)
        for aname in vdef.ncattrs():
            if aname in ['_FillValue', 'compression', 'zlib']:
                continue
            dst.variables[vname].setncattr(aname, getattr(vdef, aname))
        if 'chunksizes' not in kwargs:
            dst[vname][:] = src[vname][:]
        else:
            _pipe_netcdf_var_data(dst, src, vname, chunkSize=chunkszs)
    try:
        for vname in dst.varaibles.keys():
            if vname not in vars:
                raise Exception(f'unknown variable in dst {vname}')
    except AttributeError as e:
        pass


def calculate_netcdf_cf_units_scaling(units):

    # NOTE: the CF convention units

    # udunitDate     = period SINCE reference_date
    # period         = "millisec" | "msec" | "second" | "sec" | "s" | "minute" | "min" | "hour" | "hr" | "day" |
    #                  "week" | "month" | "mon" | "year" | "yr"
    # period         = period + "s" (plural form)
    # reference_date = iso8601 formatted date as described below
    # SINCE          = literal (case insensitive)
    # where
    #
    # msec = millisec = seconds / 1000
    # UDUNITS defines the periods as fixed multiples of seconds. The non-obvious ones are:
    #
    # day = 86400.0 seconds
    # week = 7 days = 604800.0 seconds
    # year = 3.15569259747E7 seconds (365 days of length 86400.0 seconds)
    # month = year/12 = 2629743.831225 seconds

    # http://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html

    # https://docs.unidata.ucar.edu/netcdf-java/current/userguide/cdm_calendar_date_time_ref.html
    iso_8601_calendar = "proleptic_gregorian"
    unix_epoch_units = 'seconds since 1970-01-01 00:00:00Z'

    # the cftime datetime of the unix epoch.
    unix_epoch = num2date(0, units=unix_epoch_units, calendar=iso_8601_calendar, only_use_cftime_datetimes=True, has_year_zero=True)

    # the datetime representing the iso8601 datetime contained in the units using the proleptic_gregorian calendar
    units_epoch = num2date(0, units=units, calendar=iso_8601_calendar, only_use_cftime_datetimes=True, has_year_zero=True)

    # 1 unit in the future (proleptic_gregorian calendar)
    units_epoch_time_step = num2date(1, units=units, calendar=iso_8601_calendar, only_use_cftime_datetimes=True, has_year_zero=True)

    unix_timestamp_scale = (units_epoch_time_step - units_epoch).total_seconds()

    unix_timestamp_offset = (units_epoch - unix_epoch).total_seconds()

    return unix_timestamp_scale, unix_timestamp_offset


def varfn_time_netcdf_from_units(vname, file, timeKey='time'):
    if vname != timeKey:
        return {}

    with managed_netcdf(file, 'r') as ds:
        scale, offset = calculate_netcdf_cf_units_scaling(ds[vname].units)
    return {
        'valueScale': scale,
        'valueOffset': offset,
    }


class GriddedConnectorPropertiesBuilder:
    ALLOWED_DATA_TYPES = ["i1", "u1", "i2", "u2", "i4", "u4", "i8", "u8", "f4", "f8"]

    def __init__(self, unlimited_dimension='time', existing_properties=None):
        self._dimensions = {}
        self._spaces = {}
        self._variables = {}
        self.unlimited_dimension = unlimited_dimension

        if existing_properties:
            self.merge(existing_properties)

    def build(self):
        return {
            "dimensions": self._dimensions,
            "spaces": self._spaces,
            "variables": self._variables
        }

    def merge(self, props):
        for d in props['dimensions']:
            self.add_dimension(d)

        for s in props['spaces']:
            self.add_space(s, **props['spaces'][s])

        for v in props['variables']:
            variable = props['variables'][v]
            slices = variable['slices']

            self.add_variable(v, variable['dataType'], variable['returnType'] if 'returnType' in variable else None)

            for s in slices:
                self.add_slice(
                    variable=v,
                    file=s,
                    counts=slices[s]['counts'],
                    valueScale=slices[s]['valueScale'] if 'valueScale' in slices[s] else None,
                    valueOffset=slices[s]['valueOffset'] if 'valueOffset' in slices[s] else None
                )

    def add_dimension(self, name):
        if name in self._dimensions.keys():
            raise KeyError(f"dimension {name} already exists")

        self._dimensions[name] = {"size": 0, "data": name}

    def add_space(self, name, dimensions):
        if name in self._spaces.keys():
            raise KeyError(f"space {name} already exists")

        if not dimensions:
            raise ValueError("dimensions list must be provided for space")

        for d in dimensions:
            if d not in self._dimensions.keys():
                raise KeyError(f"unknown dimension {d} not found in dimension list {self._dimensions.keys()}")

        self._spaces[name] = {"dimensions": dimensions}

    def add_variable(self, name, dataType, returnType=None, returnFillValue: Optional[float | int] = None):
        if name in self._variables.keys():
            raise KeyError(f"variable {name} already exists")

        if dataType not in self.ALLOWED_DATA_TYPES:
            _logger.warning(f"Warning: {dataType} not found in known datatypes {self.ALLOWED_DATA_TYPES}")

        if returnType and returnType not in self.ALLOWED_DATA_TYPES:
            _logger.warning(f"Warning: {returnType} not found in known datatypes {self.ALLOWED_DATA_TYPES}")

        if name not in self._spaces.keys():
            raise KeyError(f"unknown space {name} for variable {name}")

        self._variables[name] = {
            "dataType": dataType,
            "space": name,
            "slices": {}
        }

        if returnType:
            self._variables[name]["returnType"] = returnType
        if returnFillValue:
            self._variables[name]["returnFillValue"] = returnFillValue

    def add_slice(
        self,
        variable: str,
        file: str,
        counts: list[int],
        valueScale: Optional[float] = None,
        valueOffset: Optional[float] = None,
        amend_slice: bool = False,
        fillValue : Optional[float | int] = None,
    ):
        if variable not in self._variables.keys():
            raise KeyError(f"variable {variable} not found")

        space = self._variables[variable]['space']
        space_dims = self._spaces[space]['dimensions']

        if len(space_dims) != len(counts):
            raise ValueError(f"space dimensions {space_dims} and counts {counts} must be of equal length")

        if self.unlimited_dimension not in space_dims and len(self._variables[variable]['slices'].keys()) == 1:
            # the connector properties only requires a single slice to defined if the variable does not include the
            # unlimited dimension. The first file/slice will be used to represent the shape for all other files/slices
            # associated with this variable.
            _logger.info(f"ignoring adding space, already satisfied for non unlimited dimension {variable}, {file}, {counts}, {valueScale}, {valueOffset}")
            return

        starts = [0 for _ in space_dims]

        for sd in space_dims:
            dim_idx = self._get_space_dimension_index(space, sd)
            if sd == self.unlimited_dimension:
                if file in self._variables[variable]["slices"]:
                    # this is a rewrite of an existing slice and we need to prevent changes to the size.
                    # we also want to make sure the slice counts haven't change since last update
                    existingSlice = self._variables[variable]["slices"][file]
                    key_indices = [
                        i for i in self._variables[variable]["slices"].keys()
                    ]
                    lastSlice = self._variables[variable]["slices"][key_indices[-1]]

                    if existingSlice["counts"] != counts:
                        if amend_slice:
                            if existingSlice["starts"] != lastSlice["starts"]:
                                # This allows for the case where lastSlice is the first slice
                                raise ValueError(
                                    f"the {file} already exists in the connector properties for variable "
                                    f"{variable}, only the last file can be replaced."
                                )
                        else:
                            raise ValueError(
                                f"the {file} already exists in the connector properties for variable "
                                f"{variable} and the counts have changed {existingSlice['counts']} != {counts}"
                            )

                    # maintain the original start and update time dimension size in props
                    existing_start = existingSlice["starts"][dim_idx]
                    starts[dim_idx] = existing_start
                    self._dimensions[self.unlimited_dimension]["size"] = (
                        existingSlice["starts"][dim_idx] + counts[dim_idx]
                    )
                else:
                    # update the dimension size...
                    starts[dim_idx] = self._get_next_start(variable, dim_idx)
                    self._dimensions[sd]["size"] = starts[dim_idx] + counts[dim_idx]
            else:
                current_size = self._dimensions[sd]['size']
                new_size = counts[dim_idx]
                if current_size == 0:
                    self._dimensions[sd]['size'] = new_size
                elif current_size != new_size:
                    raise ValueError(f"'{sd}' dimension cannot change shape between files slices. Only the unlimited dimension '{self.unlimited_dimension}' is allowed to change.")

        sl = {'starts': starts, 'counts': counts, 'varPath': variable}

        if valueScale is not None:
            sl['valueScale'] = valueScale

        if valueOffset is not None:
            sl['valueOffset'] = valueOffset

        if fillValue is not None:
            sl['fillValue'] = fillValue
        # add the slice
        # print(f"adding slice {variable} {file} {sl}")
        self._variables[variable]['slices'][file] = sl

    def get_variable_missing_or_fillvalue(self, variable):
        fillValue = variable.getncattr('_FillValue').item() if '_FillValue' in variable.ncattrs() else None
        missing_value = variable.getncattr('missing_value').item() if 'missing_value' in variable.ncattrs() else None

        fill = fillValue if fillValue else missing_value
        if isinstance(fill, float) and np.isnan(fill):
            fill = None
        
        if isinstance(fillValue, int):
            if abs(fillValue) > _MAX_FLOAT64_PRECISION:
                raise ValueError("Integer fill values cannot be larger in magnitude than 2^53 - 1")

        return fill

    def parse_netcdf_props(
        self,
        fileKey,
        filePath,
        skip_dimensions=None,
        skip_variables=None,
        time_dim_name="time",
        cf_time_units_conversion_fn=calculate_netcdf_cf_units_scaling,
        amend_slice=False,
        returnFills: Optional[dict[str, float | int]] = None
    ):
        if skip_dimensions and isinstance(skip_dimensions, str):
            skip_dimensions = [skip_dimensions]

        if skip_variables and isinstance(skip_variables, str):
            skip_variables = [skip_variables]

        if returnFills:
            if not isinstance(returnFills, dict):
                raise ValueError(f"returnFills must be a dictionary mapping variables to fill values")

        with managed_netcdf(filePath, 'r') as ds:
            dimensions = set(skip_dimensions).symmetric_difference(set(ds.dimensions.keys())) if skip_dimensions else set(ds.dimensions.keys())

            for d in dimensions:
                if d not in self._dimensions.keys():
                    self.add_dimension(d)

            for vname, variable in ds.variables.items():
                if skip_dimensions and any(d in skip_dimensions for d in ds[vname].dimensions):
                    _logger.info("skipping variable %s as it contains a dimension that has been marked as ignored." % (vname, ))
                    continue

                if skip_variables and vname in skip_variables:
                    _logger.info("skipping variable %s as has been marked as ignored." % (vname, ))
                    continue

                if vname not in self._spaces.keys():
                    self.add_space(vname, ds[vname].dimensions)

                scale = variable.getncattr('scale_factor').item() if 'scale_factor' in variable.ncattrs() else None
                offset = variable.getncattr('add_offset').item() if 'add_offset' in variable.ncattrs() else None
                # TODO: Add Fill value attrs here
                fillValue = self.get_variable_missing_or_fillvalue(variable)

                dataType = ds[vname].dtype.str.strip('|<>=')
                returnType = None
                # If returnType isn't time or has scale/offset values then return None, platform then infers dataType as the returnType
                if len(ds[vname].dimensions) == 1 and time_dim_name in ds[vname].dimensions:
                    returnType = 'f8'
                elif scale is not None or offset is not None:
                    returnType = 'f8'
                rfill = None
                if returnFills is not None:
                    rfill = returnFills.get(vname)
                else: 
                    rfill = _DEFAULT_FILL[returnType if returnType else dataType]
                if vname not in self._variables.keys():
                    self.add_variable(vname, dataType, returnType, returnFillValue=rfill)
                else:
                    # provide return fill value to object if does not exist
                    if fillValue:
                        self._variables[vname]["returnFillValue"] = rfill 

                if cf_time_units_conversion_fn and vname == time_dim_name:
                    scale, offset = cf_time_units_conversion_fn(ds[vname].units)

                self.add_slice(
                    vname,
                    fileKey,
                    list(ds[vname].shape),
                    valueScale=scale,
                    valueOffset=offset,
                    amend_slice=amend_slice,
                    fillValue=fillValue
                )

                

    def _get_space_dimension_index(self, space, dim):
        if dim in self._spaces[space]['dimensions']:
            return self._spaces[space]['dimensions'].index(dim)
        else:
            return None

    def _get_next_start(self, variable, dim_idx):
        slices = self._variables[variable]['slices']

        if not slices:
            return 0

        last = list(slices.keys())[-1]
        return slices[last]['starts'][dim_idx] + slices[last]['counts'][dim_idx]


def gridded_geotime_netcdf_props(
    fileMap,
    skipDimensions=None,
    skipVars=None,
    existingProps=None,
    cf_time_units_conversion_fn=calculate_netcdf_cf_units_scaling,
    amend_slice=False,
):
    """
    @param fileMap: dict - file mappings e.g {'file.txt': './files/file.txt', ...}
    @param skipDimensions: list[str] - dimensions to exclude from the results. All spaces and variables dependent on these dimensions will also be dropped.
    @param existingProps: dict - Optional existing connector properties to merge. Should be used when appending new objects to an existing connector definition
    @param cf_time_units_conversion_fn: (units: str) -> tuple(valueScale, valueOffset) - Callback fn for manipulating variables during processing
    @param amend_slice: bool - If True, will allow for the amendment of the last slice from a GriddedConnectorPropertiesBuilder object.
    @return: dict - connector properties in the form {"dimensions": {}, "spaces": {}, "variables": {}}
    """

    builder = GriddedConnectorPropertiesBuilder(existing_properties=existingProps)

    for fileKey, filePath in fileMap.items():
        builder.parse_netcdf_props(
            fileKey,
            filePath,
            skip_dimensions=skipDimensions,
            skip_variables=skipVars,
            cf_time_units_conversion_fn=cf_time_units_conversion_fn,
            amend_slice=amend_slice
        )
    return builder.build()
