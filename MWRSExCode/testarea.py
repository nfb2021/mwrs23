from dataclasses import dataclass
from typing import List
from typing import Optional
from shapely.geometry import shape, Polygon


@dataclass
class TestAreaNico:
    '''Class for storing test area information

    Parameters
    ----------

    name: str
        Name of the test area
    forest_type: str
        Type of forest in the test area
    mask: `shapely.geometry.Polygon`
        Polygon of the test area
    info: Optional[str]
        Additional information about the test area. Default: None
    '''
    name: str
    forest_type: str
    mask: Polygon
    info: Optional[str] = None


class TestAreaNils:

    def __init__(self, geom):
        self.geom = [(x, y) for x, y in shape(geom).exterior.coords]
        self.bbox = [
            tuple(shape(geom).bounds[:2]),
            tuple(shape(geom).bounds[2:])
        ]


@dataclass
class TestArea:  # Combination of Nils' and Nico's TestArea classes
    '''Class for storing test area information

    Parameters
    ----------

    name: str
        Name of the test area
    forest_type: str
        Type of forest in the test area
    _geom: dict
        Output of the `polygoner.get_polygon_by_id()` function
    info: Optional[str]
        Additional information about the test area. Default: None
    _mask: `shapely.geometry.Polygon`
        Polygon of the test area. Default: None. Don't use this parameter.
    '''
    name: str
    forest_type: str
    _geom: dict
    info: Optional[str] = None
    _mask: Optional[Polygon] = None

    @property
    def geom(self):
        return [(x, y) for x, y in shape(self._geom).exterior.coords]

    @property
    def bbox(self):
        return [
            tuple(shape(self._geom).bounds[:2]),
            tuple(shape(self._geom).bounds[2:])
        ]

    @property
    def mask(self):
        if not self._mask:
            return self.geom


def coords_from_google_maps(mask):
    '''Function to transform coordinates from google maps to a polygon (=switch lat and lon)'''
    return [[coord[1], coord[0]] for coord in mask]
