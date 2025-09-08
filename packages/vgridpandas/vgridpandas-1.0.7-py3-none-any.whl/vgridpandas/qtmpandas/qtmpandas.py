from typing import Union, Callable, Any
from collections import Counter
from shapely.geometry import Polygon, MultiPolygon
import pandas as pd
import geopandas as gpd

from vgrid.conversion.latlon2dggs import latlon2qtm as latlon_to_qtm
from vgrid.conversion.dggs2geo.qtm2geo import qtm2geo as qtm_to_geo
from pandas.core.frame import DataFrame
from geopandas.geodataframe import GeoDataFrame

from vgridpandas.utils.functools import wrapped_partial
from vgridpandas.qtmpandas.qtmgeom import polyfill
from vgridpandas.utils.decorator import catch_invalid_dggs_id
from vgridpandas.utils.const import COLUMN_QTM_POLYFILL

AnyDataFrame = Union[DataFrame, GeoDataFrame]


@pd.api.extensions.register_dataframe_accessor("qtm")
class QTMPandas:
    def __init__(self, df: DataFrame):
        self._df = df

    # QTM API
    # These methods simply mirror the Vgrid qtm API and apply QTM functions to all rows

    def latlon2qtm(
        self,
        resolution: int,
        lat_col: str = "lat",
        lon_col: str = "lon",
        set_index: bool = False,
    ) -> AnyDataFrame:
        """Adds qtm ID to (Geo)DataFrame.

        pd.DataFrame: uses `lat_col` and `lon_col` (default `lat` and `lon`)
        gpd.GeoDataFrame: uses `geometry`

        Assumes coordinates in epsg=4326.

        Parameters
        ----------
        resolution : int
            QTM resolution
        lat_col : str
            Name of the latitude column (if used), default 'lat'
        lon_col : str
            Name of the longitude column (if used), default 'lon'
        set_index : bool
            If True, the columns with QTM ID is set as index, default 'True'

        Returns
        -------
        (Geo)DataFrame with QTM IDs added
        """

        if isinstance(self._df, gpd.GeoDataFrame):
            lons = self._df.geometry.x
            lats = self._df.geometry.y
        else:
            lons = self._df[lon_col]
            lats = self._df[lat_col]

        qtm_ids = [latlon_to_qtm(lat, lon, resolution) for lat, lon in zip(lats, lons)]

        # qtm_column = self._format_resolution(resolution)
        qtm_column = "qtm"
        assign_arg = {qtm_column: qtm_ids, "qtm_res": resolution}
        df = self._df.assign(**assign_arg)
        if set_index:
            return df.set_index(qtm_column)
        return df

    def qtm2geo(self, qtm_column: str = None) -> GeoDataFrame:
        """Add geometry with QTM geometry to the DataFrame. Assumes QTM ID.

        Parameters
        ----------
        qtm_column : str, optional
            Name of the column containing QTM IDs. If None, first checks for 'qtm' column,
            then assumes QTM IDs are in the index.

        Returns
        -------
        GeoDataFrame with QTM geometry

        Raises
        ------
        ValueError
            When an invalid QTM ID is encountered
        """

        if qtm_column is not None:
            # qtm qtm_ids are in the specified column
            if qtm_column not in self._df.columns:
                raise ValueError(f"Column '{qtm_column}' not found in DataFrame")
            qtm_ids = self._df[qtm_column]

            # Handle both single 1_ids and lists of 1_ids
            geometries = self._qtm_ids_to_geometries(qtm_ids)

            result_df = self._df.copy()
            result_df["geometry"] = geometries
            return gpd.GeoDataFrame(result_df, crs="epsg:4326")

        else:
            # Check if 'qtm' column exists first
            if "qtm" in self._df.columns:
                # QTM IDs are in the 'qtm' column
                qtm_ids = self._df["qtm"]

                # Handle both single 1_ids and lists of 1_ids
                geometries = self._qtm_ids_to_geometries(qtm_ids)

                result_df = self._df.copy()
                result_df["geometry"] = geometries
                return gpd.GeoDataFrame(result_df, crs="epsg:4326")
            else:
                # QTM IDs are in the index
                return self._apply_index_assign(
                    wrapped_partial(qtm_to_geo),
                    "geometry",
                    finalizer=lambda x: gpd.GeoDataFrame(x, crs="epsg:4326"),
                )

    def _qtm_ids_to_geometries(self, qtm_ids) -> list:
        """Helper method to process QTM IDs into geometries.

        Parameters
        ----------
        qtm_ids : pandas.Series or list
            QTM IDs to process

        Returns
        -------
        list
            List of geometries (Polygon or MultiPolygon objects)
        """
        geometries = []
        for q_ids in qtm_ids:
            try:
                if pd.isna(q_ids):
                    # Handle NaN values - create empty geometry
                    geometries.append(Polygon())
                elif isinstance(q_ids, list):
                    # Handle list of 1_ids - create a MultiPolygon
                    if len(q_ids) == 0:
                        # Handle empty list - create empty geometry
                        geometries.append(Polygon())
                    else:
                        cell_geometries = [qtm_to_geo(e_id) for e_id in q_ids]
                        geometries.append(MultiPolygon(cell_geometries))
                else:
                    # Handle single id
                    geometries.append(qtm_to_geo(q_ids))
            except (ValueError, TypeError):
                if isinstance(q_ids, list):
                    if len(q_ids) == 0:
                        geometries.append(Polygon())
                    else:
                        cell_geometries = [qtm_to_geo(q_id) for q_id in q_ids]
                        geometries.append(MultiPolygon(cell_geometries))
                else:
                    # Try to handle as single id
                    try:
                        geometries.append(qtm_to_geo(q_ids))
                    except Exception:
                        # If all else fails, create empty geometry
                        geometries.append(Polygon())
        return geometries

    def polyfill(
        self,
        resolution: int,
        predicate: str = None,
        compact: bool = False,
        explode: bool = False,
    ) -> AnyDataFrame:
        """
        Parameters
        ----------
        resolution : int
            QTM resolution
        predicate : str, optional
            Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact : bool, optional
            Whether to compact the QTM IDs
        explode : bool
            If True, will explode the resulting list vertically.
            All other columns' values are copied.
            Default: False
        """

        def func(row):
            return list(polyfill(row.geometry, resolution, predicate, compact))

        result = self._df.apply(func, axis=1)

        if not explode:
            assign_args = {COLUMN_QTM_POLYFILL: result}
            return self._df.assign(**assign_args)

        result = result.explode().to_frame(COLUMN_QTM_POLYFILL)

        return self._df.join(result)

    def qtmbin(
        self,
        resolution: int,
        stats: str = "count",
        numeric_column: str = None,
        category_column: str = None,
        lat_col: str = "lat",
        lon_col: str = "lon",
        return_geometry: bool = True,
    ) -> DataFrame:
        """
        Bin points into QTM cells and compute statistics, optionally grouped by a category column.

        Supports both GeoDataFrame (with point geometry) and DataFrame (with lat/lon columns).

        Parameters
        ----------
        resolution : int
            QTM resolution
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
            If True, return a GeoDataFrame with qtm cell geometry
        """
        # Validate inputs and prepare data
        # qtm_column = self._format_resolution(resolution)
        qtm_column = "qtm"
        df = self.latlon2qtm(resolution, lat_col, lon_col, False)
        # Filter to keep only QTM IDs at the requested resolution
        df = df[df[qtm_column].astype(str).str.len() == resolution]

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
        group_cols = [qtm_column]
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
                    df.groupby([qtm_column, category_column])
                    .apply(cat_agg_func, include_groups=False)
                    .reset_index(name=stats)
                )
                result = result.pivot(
                    index=qtm_column, columns=category_column, values=stats
                )
                result = result.reindex(
                    columns=all_categories, fill_value=0 if stats == "variety" else None
                )
                result = result.reset_index()
                result.columns = [qtm_column] + [
                    f"{cat}_{stats}" for cat in all_categories
                ]
            else:
                # Handle categorical aggregation without category grouping
                result = (
                    df.groupby([qtm_column])
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
                result = pd.DataFrame(columns=[qtm_column, category_column, stats])
            else:
                try:
                    # Pivot categories to columns
                    result = result.pivot(
                        index=qtm_column, columns=category_column, values=stats
                    )
                    # Fill NaN values but avoid geometry columns to prevent GeoPandas warning
                    numeric_cols = result.select_dtypes(include=["number"]).columns
                    result[numeric_cols] = result[numeric_cols].fillna(0)
                    result = result.reset_index()

                    # Rename columns with category prefixes
                    new_columns = [qtm_column]
                    for col in sorted(result.columns[1:]):
                        if col == "NaN_category":
                            new_columns.append(f"NaN_{stats}")
                        else:
                            new_columns.append(f"{col}_{stats}")
                    result.columns = new_columns
                except Exception:
                    # Fallback to simple count if pivot fails
                    result = df.groupby(qtm_column).size().reset_index(name=stats)

        # Add geometry if requested
        result = result.set_index(qtm_column)
        if return_geometry:
            result = result.qtm.qtm2geo()
        return result.reset_index()

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
            single-argument function to be applied to each S2 Token
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
        result = [processor(func(qtm_id)) for qtm_id in self._df.index]
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
            single-argument function to be applied to each S2 Token
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
                {qtm_id: processor(func(qtm_id)) for qtm_id in self._df.index},
                orient="index",
            )
            .stack()
            .to_frame(column_name)
            .reset_index(level=1, drop=True)
        )
        result = self._df.join(result)
        return finalizer(result)

    @staticmethod
    def _format_resolution(resolution: int) -> str:
        return f"qtm_{str(resolution).zfill(2)}"
