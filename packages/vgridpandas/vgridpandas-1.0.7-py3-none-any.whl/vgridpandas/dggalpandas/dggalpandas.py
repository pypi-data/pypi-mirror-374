"""S2Pandas module for S2 cell operations on pandas DataFrames and GeoDataFrames."""

from collections import Counter
from typing import Union, Any, Callable
from shapely.geometry import MultiPolygon, Polygon
import pandas as pd
import geopandas as gpd
from pandas.core.frame import DataFrame
from geopandas.geodataframe import GeoDataFrame
from vgrid.conversion.latlon2dggs import latlon2dggal as latlon_to_dggal
from vgridpandas.utils.decorator import catch_invalid_dggs_id
from vgridpandas.utils.functools import wrapped_partial
from vgridpandas.dggalpandas.dggalgeom import polyfill
from vgrid.conversion.dggs2geo.dggal2geo import dggal2geo as dggal_to_geo
from vgrid.utils.constants import DGGAL_TYPES
from dggal import *

AnyDataFrame = Union[DataFrame, GeoDataFrame]


@pd.api.extensions.register_dataframe_accessor("dggal")
class DGGALPandas:
    def __init__(self, df: DataFrame):
        self._df = df

    def latlon2dggal(
        self,
        dggs_type: str,
        resolution: int,
        lat_col: str = "lat",
        lon_col: str = "lon",
        set_index: bool = False,
    ) -> AnyDataFrame:
        """Adds DGGAL id to (Geo)DataFrame.

        pd.DataFrame: uses `lat_col` and `lon_col` (default `lat` and `lon`)
        gpd.GeoDataFrame: uses `geometry`

        Assumes coordinates in epsg=4326.

        Parameters
        ----------
        dggs_type : str
            DGGAL type
        resolution : int
            DGGAL resolution
        lat_col : str
            Name of the latitude column (if used), default 'lat'
        lon_col : str
            Name of the longitude column (if used), default 'lon'
        set_index : bool
            If True, the columns with DGGAL id is set as index, default 'True'

        Returns
        -------
        (Geo)DataFrame with DGGAL ids added

        """

        if isinstance(self._df, gpd.GeoDataFrame):
            lons = self._df.geometry.x
            lats = self._df.geometry.y
        else:
            lons = self._df[lon_col]
            lats = self._df[lat_col]

        dggal_ids = [
            latlon_to_dggal(dggs_type, lat, lon, resolution)
            for lat, lon in zip(lats, lons)
        ]

        dggal_column = f"dggal_{dggs_type}"
        assign_arg = {dggal_column: dggal_ids, f"{dggal_column}_res": resolution}
        df = self._df.assign(**assign_arg)
        if set_index:
            return df.set_index(dggal_column)
        return df

    def dggal2geo(self, dggs_type: str, dggal_column: str = None) -> GeoDataFrame:
        """Add geometry with DGGAL geometry to the DataFrame. Assumes DGGAL id.

        Parameters
        ----------
        dggal_column : str, optional
            Name of the column containing DGGAL ids. If None, assumes DGGAL ids are in the index.

        Returns
        -------
        GeoDataFrame with DGGAL geometry ids

        Raises
        ------
        ValueError
            When an invalid DGGAL id is encountered
        """

        if dggal_column is not None:
            # DGGAL ids are in the specified column
            dggs_class_name = DGGAL_TYPES[dggs_type]["class_name"]
            dggrs = globals()[dggs_class_name]()
            if dggal_column not in self._df.columns:
                raise ValueError(f"Column '{dggal_column}' not found in DataFrame")
            dggal_ids = self._df[dggal_column]

            # Handle both single dggal_ids and lists of dggal_ids
            geometries = self._dggal_ids_to_geometries(dggs_type, dggal_ids)    

            result_df = self._df.copy()
            result_df["geometry"] = geometries
            return gpd.GeoDataFrame(result_df, crs="epsg:4326")

        else:
            if f"dggal_{dggs_type}" in self._df.columns:
                # A5 hexes are in the 'a5' column
                dggal_ids = self._df[f"dggal_{dggs_type}"]

                # Handle both single hexes and lists of hexes
                geometries = self._dggal_ids_to_geometries(dggs_type, dggal_ids)

                result_df = self._df.copy()
                result_df["geometry"] = geometries
                return gpd.GeoDataFrame(result_df, crs="epsg:4326")
            else:
                # DGGAL ids are in the index
                return self._apply_index_assign(
                    wrapped_partial(dggal_to_geo, dggs_type),
                    "geometry",
                    finalizer=lambda x: gpd.GeoDataFrame(x, crs="epsg:4326"),
                )

    def polyfill(
        self,
        dggs_type: str,
        resolution: int,
        predicate: str = None,
        compact: bool = False,
        explode: bool = False,
    ) -> AnyDataFrame:
        """
        Parameters
        ----------
        resolution : int
            DGGAL resolution
        predicate : str, optional
            Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact : bool, optional
            Whether to compact the DGGAL ids
        explode : bool
            If True, will explode the resulting list vertically.
            All other columns' values are copied.
            Default: False
        """

        def func(row):
            return list(
                polyfill(dggs_type, row.geometry, resolution, predicate, compact)
            )

        result = self._df.apply(func, axis=1)

        if not explode:
            assign_args = {f"dggal_{dggs_type}": result}
            return self._df.assign(**assign_args)

        result = result.explode().to_frame(f"dggal_{dggs_type}")

        return self._df.join(result)

    def dggalbin(
        self,
        dggs_type: str,
        resolution: int,
        stats: str = "count",
        numeric_column: str = None,
        category_column: str = None,
        lat_col: str = "lat",
        lon_col: str = "lon",
        return_geometry: bool = True,
    ) -> DataFrame:
        """
        Bin points into DGGAL cells and compute statistics, optionally grouped by a category column.

        Supports both GeoDataFrame (with point geometry) and DataFrame (with lat/lon columns).

        Parameters
        ----------
        resolution : int
            DGGAL resolution
        stats : str
            Statistic to compute: count, sum, min, max, mean, median, std, var, range, minority, majority, variety
        numeric_column : str, optional
            Name of the numeric column to aggregate (for sum, min, max, etc.) or the value column for minority/majority/variety stats
        category_column : str, optional
            Name of the category column to group by. Required for minority, majority, and variety stats when grouping by category.
        lat_col : str, optional
            Name of the latitude column (only used for DataFrame input, ignored for GeoDataFrame)
        lon_col : str, optional
            Name of the longitude column (only used for DataFrame input, ignored for GeoDataFrame)
        return_geometry : bool
            If True, return a GeoDataFrame with DGGAL cell geometry
        """
        # Validate inputs and prepare data
        dggal_column = f"dggal_{dggs_type}"
        df = self.latlon2dggal(dggs_type, resolution, lat_col, lon_col, False)

        # Validate column existence
        if category_column is not None and category_column not in df.columns:
            raise ValueError(
                f"Category column '{category_column}' not found in DataFrame"
            )
        if numeric_column is not None and numeric_column not in df.columns:
            raise ValueError(
                f"Numeric column '{numeric_column}' not found in DataFrame"
            )

        # Prepare grouping columns
        group_cols = [dggal_column]
        if category_column:
            df[category_column] = df[category_column].fillna("NaN_category")
            group_cols.append(category_column)

        # Perform aggregation based on stats type
        if stats == "count":
            result = df.groupby(group_cols).size().reset_index(name=stats)

        elif stats in ["sum", "min", "max", "mean", "median", "std", "var"]:
            if not numeric_column:
                raise ValueError(f"numeric_column must be provided for stats='{stats}'")
            result = df.groupby(group_cols)[numeric_column].agg(stats).reset_index()

        elif stats == "range":
            if not numeric_column:
                raise ValueError(f"numeric_column must be provided for stats='{stats}'")
            result = (
                df.groupby(group_cols)[numeric_column].agg(["min", "max"]).reset_index()
            )
            result[stats] = result["max"] - result["min"]
            result = result.drop(["min", "max"], axis=1)

        elif stats in ["minority", "majority", "variety"]:
            if not numeric_column:
                raise ValueError(f"numeric_column must be provided for stats='{stats}'")

            # Define categorical aggregation function
            def cat_agg_func(x):
                values = x[numeric_column].dropna()
                freq = Counter(values)
                if not freq:
                    return None
                if stats == "minority":
                    return min(freq.items(), key=lambda y: y[1])[0]
                elif stats == "majority":
                    return max(freq.items(), key=lambda y: y[1])[0]
                elif stats == "variety":
                    return values.nunique()

            if category_column:
                # Handle categorical aggregation with category grouping
                all_categories = sorted(
                    [str(cat) for cat in df[category_column].unique()]
                )
                result = (
                    df.groupby([dggal_column, category_column])
                    .apply(cat_agg_func, include_groups=False)
                    .reset_index(name=stats)
                )
                result = result.pivot(
                    index=dggal_column, columns=category_column, values=stats
                )
                result = result.reindex(
                    columns=all_categories, fill_value=0 if stats == "variety" else None
                )
                result = result.reset_index()
                result.columns = [dggal_column] + [
                    f"{cat}_{stats}" for cat in all_categories
                ]
            else:
                # Handle categorical aggregation without category grouping
                result = (
                    df.groupby([dggal_column])
                    .apply(cat_agg_func, include_groups=False)
                    .reset_index(name=stats)
                )
        else:
            raise ValueError(f"Unknown stats: {stats}")

        # Handle column renaming for non-categorical stats
        if len(result.columns) > len(group_cols) and not (
            category_column and stats in ["minority", "majority", "variety"]
        ):
            result = result.rename(columns={result.columns[-1]: stats})

        # Handle category pivoting for non-categorical stats
        if category_column and stats not in ["minority", "majority", "variety"]:
            if len(result) == 0:
                result = pd.DataFrame(columns=[dggal_column, category_column, stats])
            else:
                try:
                    # Pivot categories to columns
                    result = result.pivot(
                        index=dggal_column, columns=category_column, values=stats
                    )
                    # Fill NaN values but avoid geometry columns to prevent GeoPandas warning
                    numeric_cols = result.select_dtypes(include=["number"]).columns
                    result[numeric_cols] = result[numeric_cols].fillna(0)
                    result = result.reset_index()

                    # Rename columns with category prefixes
                    new_columns = [dggal_column]
                    for col in sorted(result.columns[1:]):
                        if col == "NaN_category":
                            new_columns.append(f"NaN_{stats}")
                        else:
                            new_columns.append(f"{col}_{stats}")
                    result.columns = new_columns
                except Exception:
                    # Fallback to simple count if pivot fails
                    result = df.groupby(dggal_column).size().reset_index(name=stats)

        # Add geometry if requested
        result = result.set_index(dggal_column)
        if return_geometry:
            result = result.dggal.dggal2geo(dggs_type)
        return result.reset_index()

    def _dggal_ids_to_geometries(self, dggs_type, dggal_ids) -> list:
        """Helper method to process dggal IDs into geometries.

        Parameters
        ----------
        dggal_ids : pandas.Series or list
            DGGAL IDs to process
        dggs_type : str
            DGGAL type for geometry conversion

        Returns
        -------
        list
            List of geometries (Polygon or MultiPolygon objects)
        """
        geometries = []
        for ids in dggal_ids:
            try:
                if pd.isna(ids):
                    # Handle NaN values - create empty geometry
                    geometries.append(Polygon())
                elif isinstance(ids, list):
                    # Handle list of dggal_ids - create a MultiPolygon
                    if len(ids) == 0:
                        # Handle empty list - create empty geometry
                        geometries.append(Polygon())
                    else:
                        cell_geometries = [dggal_to_geo(dggs_type, id) for id in ids]
                        geometries.append(MultiPolygon(cell_geometries))
                else:
                    # Handle single dggal_id
                    geometries.append(dggal_to_geo(dggs_type, ids))
            except (ValueError, TypeError):
                if isinstance(ids, list):
                    if len(ids) == 0:
                        geometries.append(Polygon())
                    else:
                        cell_geometries = [dggal_to_geo(dggs_type, id) for id in ids]
                        geometries.append(MultiPolygon(cell_geometries))
                else:
                    # Try to handle as single dggal_id
                    try:
                        geometries.append(dggal_to_geo(dggs_type, ids))
                    except Exception:
                        # If all else fails, create empty geometry
                        geometries.append(Polygon())
        return geometries

    # # Private methods
    def _apply_index_assign(
        self,
        func: Callable,
        column_name: str,
        processor: Callable = lambda x: x,
        finalizer: Callable = lambda x: x,
    ) -> Any:
        """Helper method. Applies `func` to index and assigns the result to `column`.

        Parameters
        ----------
        func : Callable
            single-argument function to be applied to each DGGAL ID
        column_name : str
            name of the resulting column
        processor : Callable
            (Optional) further processes the result of func. Default: identity
        finalizer : Callable
            (Optional) further processes the resulting dataframe. Default: identity

        Returns
        -------
        Dataframe with column `column` containing the result of `func`.
        If using `finalizer`, can return anything the `finalizer` returns.
        """
        func = catch_invalid_dggs_id(func)
        result = [processor(func(dggal_id)) for dggal_id in self._df.index]
        assign_args = {column_name: result}
        return finalizer(self._df.assign(**assign_args))

    def _apply_index_explode(
        self,
        func: Callable,
        column_name: str,
        processor: Callable = lambda x: x,
        finalizer: Callable = lambda x: x,
    ) -> Any:
        """Helper method. Applies a list-making `func` to index and performs
        a vertical explode.
        Any additional values are simply copied to all the rows.

        Parameters
        ----------
        func : Callable
            single-argument function to be applied to each DGGAL ID
        column_name : str
            name of the resulting column
        processor : Callable
            (Optional) further processes the result of func. Default: identity
        finalizer : Callable
            (Optional) further processes the resulting dataframe. Default: identity

        Returns
        -------
        Dataframe with column `column` containing the result of `func`.
        If using `finalizer`, can return anything the `finalizer` returns.
        """
        func = catch_invalid_dggs_id(func)
        result = (
            pd.DataFrame.from_dict(
                {dggal_id: processor(func(dggal_id)) for dggal_id in self._df.index},
                orient="index",
            )
            .stack()
            .to_frame(column_name)
            .reset_index(level=1, drop=True)
        )
        result = self._df.join(result)
        return finalizer(result)
