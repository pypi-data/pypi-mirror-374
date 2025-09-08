from typing import Union, Set
from shapely.geometry import box, Polygon, MultiPolygon, LineString, MultiLineString
import platform
from vgrid.conversion.dggscompact.isea4tcompact import isea4t_compact
from vgrid.utils.geometry import check_predicate

MultiPolyOrPoly = Union[Polygon, MultiPolygon]
MultiLineOrLine = Union[LineString, MultiLineString]

if platform.system() == "Windows":
    from vgrid.dggs.eaggr.enums.shape_string_format import ShapeStringFormat
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.enums.model import Model
    from vgrid.generator.isea4tgrid import get_isea4t_children_cells_within_bbox
    from vgrid.utils.geometry import (
        isea4t_cell_to_polygon,
        fix_isea4t_antimeridian_cells,
    )
    from vgrid.utils.io import validate_isea4t_resolution
    from vgrid.utils.constants import ISEA4T_RES_ACCURACY_DICT

    isea4t_dggs = Eaggr(Model.ISEA4T)


def poly2isea4t(
    geometry: MultiPolyOrPoly,
    resolution: int,
    predicate: str = None,
    compact: bool = False,
) -> Set[str]:
    """
    Convert polygon geometries (Polygon, MultiPolygon) to isea4t grid cells.

    Args:
        resolution (int): ISEA4T resolution level [0..28]
        geometry (shapely.geometry.Polygon or shapely.geometry.MultiPolygon): Polygon geometry to convert
        predicate (str, optional): Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')

    Returns:
        list: List of isea4t ids intersecting the polygon

    Example:
        >>> from shapely.geometry import Polygon
        >>> poly = Polygon([(-122.5, 37.7), (-122.3, 37.7), (-122.3, 37.9), (-122.5, 37.9)])
        >>> cells = poly2isea4t(poly, 10, predicate="intersect", compact=True)
        >>> len(cells) > 0
        True
    """
    if platform.system() == "Windows":
        resolution = validate_isea4t_resolution(resolution)
        isea4t_ids = []
        if isinstance(geometry, (Polygon, LineString)):
            polys = [geometry]
        elif isinstance(geometry, (MultiPolygon, MultiLineString)):
            polys = list(geometry.geoms)
        else:
            return []

        for poly in polys:
            accuracy = ISEA4T_RES_ACCURACY_DICT.get(resolution)
            bounding_box = box(*poly.bounds)
            bounding_box_wkt = bounding_box.wkt
            shapes = isea4t_dggs.convert_shape_string_to_dggs_shapes(
                bounding_box_wkt, ShapeStringFormat.WKT, accuracy
            )
            shape = shapes[0]
            bbox_cells = shape.get_shape().get_outer_ring().get_cells()
            bounding_cell = isea4t_dggs.get_bounding_dggs_cell(bbox_cells)
            bounding_child_cells = get_isea4t_children_cells_within_bbox(
                bounding_cell.get_cell_id(), bounding_box, resolution
            )
            if compact:
                bounding_child_cells = isea4t_compact(bounding_child_cells)
            for child in bounding_child_cells:
                isea4t_cell = DggsCell(child)
                cell_polygon = isea4t_cell_to_polygon(isea4t_cell)
                isea4t_id = isea4t_cell.get_cell_id()
                if isea4t_id.startswith(("00", "09", "14", "04", "19")):
                    cell_polygon = fix_isea4t_antimeridian_cells(cell_polygon)
                if check_predicate(cell_polygon, poly, predicate):
                    isea4t_ids.append(isea4t_id)
        return isea4t_ids


def polyfill(
    geometry: MultiPolyOrPoly,
    resolution: int,
    predicate: str = None,
    compact: bool = False,
) -> Set[str]:
    """isea4t.polyfill accepting a shapely (Multi)Polygon or (Multi)LineString

    Parameters
    ----------
    geometry : Polygon or Multipolygon
        Polygon to fill
    resolution : int
        isea4t resolution of the filling cells

    Returns
    -------
    Set of isea4t ids

    Raises
    ------
    TypeError if geometry is not a Polygon or MultiPolygon
    """
    if isinstance(geometry, (Polygon, MultiPolygon)):
        return set(poly2isea4t(geometry, resolution, predicate, compact))
    elif isinstance(geometry, (LineString, MultiLineString)):
        return set(
            poly2isea4t(geometry, resolution, predicate="intersect", compact=False)
        )
    else:
        raise TypeError(f"Unknown type {type(geometry)}")
