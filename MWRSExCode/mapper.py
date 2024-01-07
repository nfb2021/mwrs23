import plotly.express as px
import plotly.graph_objects as go
from dataclasses import dataclass
import os
from typing import List
import pandas as pd
from shapely.geometry import Polygon, Point
from typing import Optional

from testarea import TestArea, coords_from_google_maps


@dataclass
class MapboxMap:
    token: str
    style_url: str


class Map:

    def __init__(self,
                 testarea: TestArea,
                 zoom=10,
                 custom_map: MapboxMap = None):
        self.testarea = testarea
        self.lon, self.lat = testarea.mask.exterior.coords.xy
        self.lon, self.lat = list(self.lon), list(self.lat)
        self.coord_pairs = [[lon, lat] for lon, lat in zip(self.lon, self.lat)]
        self.zoom = zoom

        if custom_map:
            self.token = custom_map.token
            self.style_url = custom_map.style_url
        else:
            self.token = None
            self.style_url = 'open-street-map'

    @property
    def center(self):
        return [(max(self.lon) + min(self.lon)) / 2,
                (max(self.lat) + min(self.lat)) / 2]

    def get_polygon_geojson(self):
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates":
                [self.coord_pairs]  # Wrap coordinates in an extra list
            },
            "properties": {}
        }

    def get_polygon_dimensions(self):
        return [(max(self.lon) - min(self.lon)),
                (max(self.lat) - min(self.lat))]

    def get_text_anchor(self):
        return self.center[
            0], self.center[1] + 0.6 * self.get_polygon_dimensions()[1]

    def get_map(self, save=False, format='html'):

        custom_style_url = self.style_url
        textcolor = 'black'
        polygon_color = "rgba(0, 0, 0, 1)"

        if self.token:
            px.set_mapbox_access_token(self.token)
            textcolor = 'white'
            polygon_color = "rgba(255, 255, 255, 1)"

        polygon_geojson = self.get_polygon_geojson()
        print(polygon_geojson)

        fig = px.scatter_mapbox(
            lat=[y for y in self.lat[:-1]],
            lon=[x for x in self.lon[:-1]],
            zoom=self.zoom,
        )

        fig.update_layout(
            mapbox_style=custom_style_url,
            mapbox_layers=[{
                "sourcetype": "geojson",
                "source": polygon_geojson,
                "type": "line",
                "color": polygon_color,
                "line": {
                    "width": 2
                }
            }],
            mapbox=dict(zoom=self.zoom,
                        center=dict(lat=self.center[1], lon=self.center[0])),
        )

        fig.add_trace(
            go.Scattermapbox(
                mode="text",
                lat=[self.get_text_anchor()[1]],
                lon=[self.get_text_anchor()[0]],
                text=[self.testarea.name],
                textfont=dict(size=15, color=textcolor),
                showlegend=False,
            ))

        print(os.getcwd())
        if save and format != 'html':
            fig.write_image(f"map.{format}")
        elif save and format == 'html':
            fig.write_html(f"map.{format}")

        return fig


class MapOverview:

    def __init__(self,
                 maps: List[Map],
                 zoom: int,
                 custom_map: MapboxMap = None):
        self.maps = maps
        print(self.maps)
        self.zoom = zoom

        if custom_map:
            self.token = custom_map.token
            self.style_url = custom_map.style_url
        else:
            self.token = None
            self.style_url = 'open-street-map'

    def get_df(self):
        maps_dict = {
            'name': [map.testarea.name for map in self.maps],
            'forest_type': [map.testarea.forest_type for map in self.maps],
            'lat': [map.lat for map in self.maps],
            'lon': [map.lon for map in self.maps],
            'info': [map.testarea.info for map in self.maps]
        }

        return pd.DataFrame(
            maps_dict, columns=['name', 'forest_type', 'lat', 'lon', 'info'])

    def get_polygons(self):
        return [{
            'name': map.testarea.name,
            'forest_type': map.testarea.forest_type,
            'info': map.testarea.info,
            'testarea_lon': map.lon,
            'testarea_lat': map.lat,
            'center': map.center
        } for map in self.maps]

    def get_super_center(self):
        return [
            sum([map.center[0] for map in self.maps]) / len(self.maps),
            sum([map.center[1] for map in self.maps]) / len(self.maps)
        ]

    def get_map(self, save=False, format='html'):
        custom_style_url = self.style_url
        if self.token:
            px.set_mapbox_access_token(self.token)

        fig = go.Figure()  # Create an empty figure

        # Add each polygon to the plot with its specified color
        for poly in self.get_polygons():
            fig.add_trace(
                go.Scattermapbox(
                    mode="lines",
                    lat=poly['testarea_lat'],
                    lon=poly['testarea_lon'],
                    name=poly['name'],
                    hoverinfo='text',  # Set hoverinfo to display text on hover
                    text=
                    f"Forest type: {poly['forest_type']}<br>Info: {poly['info']}<br>",
                ))

        # Update layout with custom Mapbox map
        fig.update_layout(
            mapbox=dict(style=custom_style_url,
                        accesstoken=self.token,
                        zoom=self.zoom,
                        center=dict(lat=self.get_super_center()[1],
                                    lon=self.get_super_center()[0])))

        fig.show()

        # Display or save the figure
        if save and format != 'html':
            fig.write_image(f"map.{format}")
        elif save and format == 'html':
            fig.write_html(f"map.{format}")

        return fig


if __name__ == "__main__":
    test_area_1 = TestArea(name='Test Area 1',
                           forest_type='coniferous',
                           mask=Polygon(
                               coords_from_google_maps([
                                   (48.365325929665225, 16.491747734015267),
                                   (48.45160471550519, 16.491747734015267),
                                   (48.45160471550519, 16.63199879296561),
                                   (48.365325929665225, 16.63199879296561),
                                   (48.365325929665225, 16.491747734015267)
                               ])),
                           info='predominantly oak forest')

    test_area_2 = TestArea(name='Test Area 2',
                           forest_type='mixed',
                           mask=Polygon(
                               coords_from_google_maps([
                                   (48.59247728447388, 15.476589833711538),
                                   (48.650658311724776, 15.476589833711538),
                                   (48.650658311724776, 15.564157713339654),
                                   (48.59247728447388, 15.564157713339654),
                                   (48.59247728447388, 15.476589833711538)
                               ])),
                           info='mixed forest')

    map_austria = MapboxMap(
        token=
        'pk.eyJ1IjoibmJhZGVyIiwiYSI6ImNsaXZydDN5cDI5eG8zZG9jdXR1azEya2cifQ.uO6L5HVoLx_Ou_bBaEbGsw',
        style_url='mapbox://styles/nbader/clqwfsk7u010a01qud6d7hsjs')

    map = Map(
        test_area_1,
        zoom=10,
        custom_map=map_austria,
    )

    # fig = map.get_map(save=True)
    # fig.show()

    map2 = Map(
        test_area_2,
        zoom=10,
        custom_map=map_austria,
    )

    testarea_list = [map, map2]

    overview = MapOverview(testarea_list, zoom=7, custom_map=map_austria)
    overview.get_map()
