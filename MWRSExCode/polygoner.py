import geopandas as gpd
from shapely.geometry import mapping
import os
from pathlib import Path
import shutil


def get_polygon_by_id(
    target_id: any,
    id_column: str = "ID",
) -> int:

    USER = os.getcwd().split('/')[2]
    at_shapefile_path: str = os.path.join(
        f'/home/{USER}/shared/120.030-2023W/groups/PracticalExGr_3/eo_processing/clc/CLC18_AT_clip.shp'
    )

    if not os.path.isfile(at_shapefile_path):
        raise FileNotFoundError(
            f'The specified shapefile {at_shapefile_path} does not exist.')
    else:
        print(f'Specified Austria Shape File exists and will be loaded...')

    testareas_dir_path = str(Path(at_shapefile_path).resolve().parent)

    if os.path.exists(os.path.join(testareas_dir_path, target_id)):
        # user_confirm = input(f'Shp file already exists! Overwrite? [y/n]').lower()

        if 1 == 2:  # user_confirm == 'y':
            shutil.rmtree(os.path.join(testareas_dir_path, target_id))
        else:
            print(
                f'Found previously extracted data for ID {target_id}: {os.path.join(testareas_dir_path, target_id, target_id + ".shp")}'
            )
            extent = gpd.read_file(
                os.path.join(testareas_dir_path, target_id,
                             target_id + ".shp"))

            if extent.geometry.iloc[0] is None:
                raise ValueError('Invalid geometry')
            else:
                return mapping(extent.geometry.iloc[0])

    print(f'Extracting data for ID {target_id}...')
    # Make a new directory for extracted polygons
    os.mkdir(os.path.join(testareas_dir_path, target_id))

    testareas_dir_path = os.path.join(testareas_dir_path, target_id)
    gdf = gpd.read_file(at_shapefile_path)

    if id_column not in gdf.columns:
        raise ValueError(f"{id_column} not found in GeoDataFrame.")

    # Select row with corresponding id
    selected_polygon = gdf[gdf[id_column] == target_id].to_crs("EPSG:4326")

    if selected_polygon.empty:
        raise ValueError(f"No polygon with {id_column} == {target_id}.")

    geom = mapping(selected_polygon.geometry.iloc[0])

    if selected_polygon.empty:
        raise ValueError(
            f"No polygon found with {id_column} equal to {target_id}.")

    file = os.path.join(testareas_dir_path, target_id + '.shp')
    print(f'All data extracted! Created new shp file in path: \n {file}')
    selected_polygon.to_file(file)

    return geom
