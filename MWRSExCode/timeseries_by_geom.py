from typing_extensions import deprecated
from geopathfinder.naming_conventions.sgrt_naming import SgrtFilename
from yeoda.products.base import ProductDataCube
from equi7grid.equi7grid import Equi7Grid
import osr
import warnings
import os
from geopathfinder.folder_naming import build_smarttree
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
from tqdm import trange
from shapely.geometry import Polygon
import xarray as xr

from testarea import TestArea


@dataclass
class TemporalWindow:
    """
    Class to represent a temporal window for the datacube.
    """
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.start > self.end:
            raise ValueError(
                "Start of temporal window must be before end of temporal window"
            )

    def __contains__(self, item: datetime):
        return self.start <= item <= self.end


class DataCubeLoader:

    def __init__(self,
                 resolution: int = 10,
                 lonlatsys: int = 4326,
                 dimensions: List[str] = [
                     "time", "var_name", "tile_name", "pol"
                 ],
                 scale_factor: int = 100) -> None:

        self.USER = os.getcwd().split('/')[
            2]  #This command should automatically get your username

        self.sref = osr.SpatialReference()
        self.lonlatsys = lonlatsys
        self.sref.ImportFromEPSG(
            self.lonlatsys)  # LonLat spatial reference system

        self.resolution = resolution
        self.subgrid = Equi7Grid(self.resolution).EU

        self.root_path = f"/home/{self.USER}/shared/datasets/fe/data/sentinel1/preprocessed/EU{self.resolution:03}M"
        self.folder_hierarchy = ["tile_name", "var_name"]

        self.tree = build_smarttree(self.root_path,
                                    self.folder_hierarchy,
                                    register_file_pattern="^[^Q].*.tif$")
        self.dimensions = dimensions
        self.scale_factor = scale_factor  # with yeoda v0.3.0, the scale factor still needs to be defined by the user

    @property
    def datacube(self):
        _datacube = ProductDataCube(filepaths=self.tree.file_register,
                                    dimensions=self.dimensions,
                                    filename_class=SgrtFilename,
                                    grid=self.subgrid,
                                    scale_factor=self.scale_factor)

        _datacube.rename_dimensions({'tile_name': 'tile'}, inplace=True)
        return _datacube


# class TimeSeriesByGeom():

#     def __init__(self,
#                  testarea: TestArea,
#                  loaded_datacube: DataCubeLoader) -> None:

#         self.testarea = testarea
#         self.datacube = loaded_datacube.datacube

#     @deprecated('not yet fully operational')
#     def temporal_slicer(self,
#                         temporal_slice: TemporalWindow,
#                         split_monthly=True) -> Dict[str, ProductDataCube]:
#         """
#         Function to slice out a sub-datacube for the specifeid time range, out of a complete datacube.

#         Parameters
#         ----------

#         datacube: ProductDataCube
#             The datacube to be sliced
#         temporal_slice: TemporalWindow
#             The temporal window to slice out of the datacube

#         Returns
#         -------

#         Dict[str, ProductDataCube]
#         """
#         datacube = self.datacube

#         if split_monthly:
#             months = [
#                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
#                 'Oct', 'Nov', 'Dec'
#             ]
#             return {
#                 month: monthly_cube
#                 for month, monthly_cube in zip(
#                     months,
#                     datacube.filter_by_dimension([(
#                         temporal_slice.start, temporal_slice.end)], [('>=',
#                                                                       '<')],
#                                                  name='time').split_monthly())
#             }
#         else:
#             return {
#                 'custom':
#                 datacube.filter_by_dimension(
#                     [(temporal_slice.start, temporal_slice.end)],
#                     [('>=', '<')],
#                     name='time')
#             }

#     @deprecated('not yet fully operational')
#     def spatial_slicer(self, datacube: ProductDataCube,
#                        mask: list) -> ProductDataCube:
#         """
#         Function to slice out a sub-datacube for the specifeid spatial range, out of a complete datacube.

#         Parameters
#         ----------

#         datacube: ProductDataCube
#             The datacube to be sliced
#         mask: TestArea.mask (= list of coordinates)
#             The spatial range to be sliced out (= the test area)

#         Returns
#         -------

#         datacube_slice: ProductDataCube
#             The sliced datacube
#         """

#         datacube = self.datacube

#         with warnings.catch_warnings():
#             warnings.simplefilter("ignore")
#             return datacube.filter_spatially_by_geom(
#                 mask, sref=self.sref).load_by_geom(mask,
#                                                    sref=self.sref,
#                                                    apply_mask=False,
#                                                    dtype="numpy")

#     def masked_array(self,
#                      datacube: ProductDataCube,
#                      apply_mask: Optional[bool] = False,
#                      dtype: str = 'xarray') -> np.ndarray:
#         with warnings.catch_warnings():
#             warnings.simplefilter("ignore")
#             # masked_xarray = jan_vv.load_by_geom(polygon,
#             #                                     sref=sref,
#             #                                     apply_mask=False,
#             #                                     dtype="numpy")

#             if isinstance(self.testarea.mask, Polygon):
#                 polygon = self.testarea.mask.exterior.coords.xy
#             elif isinstance(self.testarea.mask, list):
#                 polygon = self.testarea.mask

#             _masked_xarray = datacube.load_by_geom(polygon,
#                                                    sref=datacube.sref,
#                                                    apply_mask=apply_mask,
#                                                    dtype=dtype)
#             _masked_xarray = _masked_xarray.rename({'1': 'data'})
#             return _masked_xarray

#     def get_timeseries_xr(self, masked_xarray, to_file=False):
#         # Create an empty dataset
#         combined_dataset = xr.Dataset()
#         coords = []
#         for x in trange(len(masked_xarray.x), desc='x'):
#             x_val = masked_xarray.x.values[x]
#             for y in range(len(masked_xarray.y)):
#                 y_val = masked_xarray.y.values[y]
#                 data_list = []
#                 for t in range(len(masked_xarray.time)):
#                     data = float(masked_xarray.data[t, y, x].values)
#                     data_list.append(data)

#                 key = (x_val, y_val)

#                 # Create a DataArray for the current x, y pair
#                 data_array = xr.DataArray(data_list,
#                                           dims='time',
#                                           coords={'time': masked_xarray.time})

#                 # Create a dataset for the current iteration
#                 dataset = xr.Dataset(data_vars={'data': data_array})
#                 # dataset['data'].attrs['lat'] = key[0]
#                 # dataset['data'].attrs['lon'] = key[1]

#                 # Append the dataset for this iteration to the combined dataset
#                 combined_dataset = xr.concat([combined_dataset, dataset],
#                                              dim='pixel')

#                 coords.append((x_val, y_val))
#         combined_dataset['coords'] = xr.DataArray(coords, dims=['None', '(x,y)'])

#         if to_file:
#             combined_dataset.to_netcdf('output.nc')
#             print(f'Saved to file "output.nc" in {os.getcwd()}')

#         return combined_dataset


class TimeSeriesByGeom(DataCubeLoader):

    def __init__(self, testarea: TestArea,
                 loaded_datacube: DataCubeLoader) -> None:
        super().__init__()
        self.testarea = testarea
        # self.datacube = loaded_datacube.datacube
        # self.sref = self.datacube.sref  # Inherits sref from DataCubeLoader

    @deprecated('not yet fully operational')
    def temporal_slicer(self,
                        temporal_slice: TemporalWindow,
                        split_monthly=True) -> Dict[str, ProductDataCube]:
        """
        Function to slice out a sub-datacube for the specifeid time range, out of a complete datacube.

        Parameters
        ----------

        datacube: ProductDataCube
            The datacube to be sliced
        temporal_slice: TemporalWindow
            The temporal window to slice out of the datacube

        Returns
        -------

        Dict[str, ProductDataCube]
        """
        datacube = self.datacube

        if split_monthly:
            months = [
                'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
                'Oct', 'Nov', 'Dec'
            ]
            return {
                month: monthly_cube
                for month, monthly_cube in zip(
                    months,
                    datacube.filter_by_dimension([(
                        temporal_slice.start, temporal_slice.end)], [('>=',
                                                                      '<')],
                                                 name='time').split_monthly())
            }
        else:
            return {
                'custom':
                datacube.filter_by_dimension(
                    [(temporal_slice.start, temporal_slice.end)],
                    [('>=', '<')],
                    name='time')
            }

    @deprecated('not yet fully operational')
    def spatial_slicer(self, datacube: ProductDataCube,
                       mask: list) -> ProductDataCube:
        """
        Function to slice out a sub-datacube for the specifeid spatial range, out of a complete datacube.

        Parameters
        ----------

        datacube: ProductDataCube
            The datacube to be sliced
        mask: TestArea.mask (= list of coordinates)
            The spatial range to be sliced out (= the test area)

        Returns
        -------

        datacube_slice: ProductDataCube
            The sliced datacube
        """

        datacube = self.datacube

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return datacube.filter_spatially_by_geom(
                mask, sref=self.sref).load_by_geom(mask,
                                                   sref=self.sref,
                                                   apply_mask=False,
                                                   dtype="numpy")

    def masked_array(self,
                     datacube: ProductDataCube,
                     apply_mask: Optional[bool] = False,
                     dtype: str = 'xarray') -> np.ndarray:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # masked_xarray = jan_vv.load_by_geom(polygon,
            #                                     sref=sref,
            #                                     apply_mask=False,
            #                                     dtype="numpy")

            if isinstance(self.testarea.mask, Polygon):
                polygon = self.testarea.mask.exterior.coords.xy
            elif isinstance(self.testarea.mask, list):
                polygon = self.testarea.mask

            _masked_xarray = datacube.load_by_geom(polygon,
                                                   sref=self.sref,
                                                   apply_mask=apply_mask,
                                                   dtype=dtype)
            _masked_xarray = _masked_xarray.rename({'1': 'data'})
            return _masked_xarray

    # def get_timeseries_xr(self, masked_xarray, to_file=False):
    #     combined_dataset = xr.Dataset()
    #     coords = []
    #     for x in trange(len(masked_xarray.x), desc='x'):
    #         x_val = masked_xarray.x.values[x]
    #         for y in range(len(masked_xarray.y)):
    #             y_val = masked_xarray.y.values[y]
    #             data_list = []
    #             for t in range(len(masked_xarray.time)):
    #                 data = float(masked_xarray.data[t, y, x].values)
    #                 data_list.append(data)

    #             key = (x_val, y_val)

    #             data_array = xr.DataArray(data_list, dims='time', coords={'time': masked_xarray.time})
    #             dataset = xr.Dataset(data_vars={'data': data_array})
    #             combined_dataset = xr.concat([combined_dataset, dataset], dim='pixel')

    #             coords.append((x_val, y_val))
    #     combined_dataset['coordinates'] = xr.DataArray(coords, dims=['pixel', '(x,y)'])  # Change 'None' to 'pixel'

    #     if to_file:
    #         combined_dataset.to_netcdf('output.nc')
    #         print(f'Saved to file "output.nc" in {os.getcwd()}')

    #     return combined_dataset

    def get_timeseries_xr(self, masked_xarray, to_file=False):
        # Preallocate memory for the data and coordinates
        data_list = np.empty((len(masked_xarray.x), len(masked_xarray.y),
                              len(masked_xarray.time)))
        coords = [(x, y) for x in masked_xarray.x.values
                  for y in masked_xarray.y.values]

        # Fill data_list with the values from masked_xarray
        for x in range(len(masked_xarray.x)):
            for y in range(len(masked_xarray.y)):
                data_list[x, y] = masked_xarray.data[:, y,
                                                     x].values.astype(float)

        # Create a DataArray for the entire dataset
        data_array = xr.DataArray(data_list,
                                  dims=('x', 'y', 'time'),
                                  coords={
                                      'x': masked_xarray.x.values,
                                      'y': masked_xarray.y.values,
                                      'time': masked_xarray.time
                                  })

        # Create the combined dataset
        combined_dataset = xr.Dataset({'data': data_array})
        combined_dataset['coords'] = xr.DataArray(coords,
                                                  dims=['pixel', '(x,y)'])

        if to_file:
            combined_dataset.to_netcdf('output.nc')
            print(f'Saved to file "output.nc" in {os.getcwd()}')

        return combined_dataset
