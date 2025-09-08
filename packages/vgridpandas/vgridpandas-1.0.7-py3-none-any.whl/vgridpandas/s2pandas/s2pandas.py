"""S2Pandas module for S2 cell operations on pandas DataFrames and GeoDataFrames."""

from collections import Counter
from typing import Union, Any, Callable
from shapely.geometry import MultiPolygon, Polygon
import pandas as pd
import geopandas as gpd
from pandas.core.frame import DataFrame
from geopandas.geodataframe import GeoDataFrame
from vgrid.conversion.latlon2dggs import latlon2s2 as latlon_to_s2
from vgridpandas.utils.decorator import catch_invalid_dggs_id, doc_standard
from vgridpandas.utils.functools import wrapped_partial
from vgridpandas.s2pandas.s2geom import polyfill
from vgrid.conversion.dggs2geo.s22geo import s22geo as s2_to_geo
from vgridpandas.utils.const import COLUMN_S2_POLYFILL

AnyDataFrame = Union[DataFrame, GeoDataFrame]


@pd.api.extensions.register_dataframe_accessor("s2")
class S2Pandas:
    def __init__(self, df: DataFrame):
        self._df = df

    def latlon2s2(
        self,
        resolution: int,
        lat_col: str = "lat",
        lon_col: str = "lon",
        set_index: bool = False,
    ) -> AnyDataFrame:
        """Adds S2 token to (Geo)DataFrame.

        pd.DataFrame: uses `lat_col` and `lon_col` (default `lat` and `lon`)
        gpd.GeoDataFrame: uses `geometry`

        Assumes coordinates in epsg=4326.

        Parameters
        ----------
        resolution : int
            S2 resolution
        lat_col : str
            Name of the latitude column (if used), default 'lat'
        lon_col : str
            Name of the longitude column (if used), default 'lon'
        set_index : bool
            If True, the columns with S2 token is set as index, default 'True'

        Returns
        -------
        (Geo)DataFrame with S2 IDs added

        """

        if isinstance(self._df, gpd.GeoDataFrame):
            lons = self._df.geometry.x
            lats = self._df.geometry.y
        else:
            lons = self._df[lon_col]
            lats = self._df[lat_col]

        s2_tokens = [latlon_to_s2(lat, lon, resolution) for lat, lon in zip(lats, lons)]

        # s2_column = self._format_resolution(resolution)
        s2_column = "s2"
        assign_arg = {s2_column: s2_tokens, "s2_res": resolution}
        df = self._df.assign(**assign_arg)
        if set_index:
            return df.set_index(s2_column)
        return df

    def s22geo(self, s2_column: str = None) -> GeoDataFrame:
        """Add geometry with S2 geometry to the DataFrame. Assumes S2 token.

        Parameters
        ----------
        s2_column : str, optional
            Name of the column containing S2 tokens. If None, first checks for 's2' column,
            then assumes S2 tokens are in the index.

        Returns
        -------
        GeoDataFrame with S2 geometry

        Raises
        ------
        ValueError
            When an invalid S2 token is encountered
        """

        if s2_column is not None:
            # S2 tokens are in the specified column
            if s2_column not in self._df.columns:
                raise ValueError(f"Column '{s2_column}' not found in DataFrame")
            s2_tokens = self._df[s2_column]

            # Handle both single tokens and lists of tokens
            geometries = self._s2_tokens_to_geometries(s2_tokens)

            result_df = self._df.copy()
            result_df["geometry"] = geometries
            return gpd.GeoDataFrame(result_df, crs="epsg:4326")

        else:
            # Check if 's2' column exists first
            if "s2" in self._df.columns:
                # S2 tokens are in the 's2' column
                s2_tokens = self._df["s2"]

                # Handle both single tokens and lists of tokens
                geometries = self._s2_tokens_to_geometries(s2_tokens)

                result_df = self._df.copy()
                result_df["geometry"] = geometries
                return gpd.GeoDataFrame(result_df, crs="epsg:4326")
            else:
                # S2 tokens are in the index
                return self._apply_index_assign(
                    wrapped_partial(s2_to_geo),
                    "geometry",
                    finalizer=lambda x: gpd.GeoDataFrame(x, crs="epsg:4326"),
                )

    @doc_standard(
        COLUMN_S2_POLYFILL,
        "containing a list S2 ID whose centroid falls into the Polygon",
    )
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
            S2 resolution
        predicate : str, optional
            Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact : bool, optional
            Whether to compact the S2 tokens
        explode : bool
            If True, will explode the resulting list vertically.
            All other columns' values are copied.
            Default: False
        """

        def func(row):
            return list(polyfill(row.geometry, resolution, predicate, compact))

        result = self._df.apply(func, axis=1)

        if not explode:
            assign_args = {COLUMN_S2_POLYFILL: result}
            return self._df.assign(**assign_args)

        result = result.explode().to_frame(COLUMN_S2_POLYFILL)

        return self._df.join(result)

    def s2bin(
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
        Bin points into S2 cells and compute statistics, optionally grouped by a category column.

        Supports both GeoDataFrame (with point geometry) and DataFrame (with lat/lon columns).

        Parameters
        ----------
        resolution : int
            S2 resolution
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
            If True, return a GeoDataFrame with S2 cell geometry
        """
        # Validate inputs and prepare data
        # s2_column = self._format_resolution(resolution)
        s2_column = "s2"
        df = self.latlon2s2(resolution, lat_col, lon_col, False)

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
        group_cols = [s2_column]
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
                    df.groupby([s2_column, category_column])
                    .apply(cat_agg_func, include_groups=False)
                    .reset_index(name=stats)
                )
                result = result.pivot(
                    index=s2_column, columns=category_column, values=stats
                )
                result = result.reindex(
                    columns=all_categories, fill_value=0 if stats == "variety" else None
                )
                result = result.reset_index()
                result.columns = [s2_column] + [
                    f"{cat}_{stats}" for cat in all_categories
                ]
            else:
                # Handle categorical aggregation without category grouping
                result = (
                    df.groupby([s2_column])
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
                result = pd.DataFrame(columns=[s2_column, category_column, stats])
            else:
                try:
                    # Pivot categories to columns
                    result = result.pivot(
                        index=s2_column, columns=category_column, values=stats
                    )
                    # Fill NaN values but avoid geometry columns to prevent GeoPandas warning
                    numeric_cols = result.select_dtypes(include=["number"]).columns
                    result[numeric_cols] = result[numeric_cols].fillna(0)
                    result = result.reset_index()

                    # Rename columns with category prefixes
                    new_columns = [s2_column]
                    for col in sorted(result.columns[1:]):
                        if col == "NaN_category":
                            new_columns.append(f"NaN_{stats}")
                        else:
                            new_columns.append(f"{col}_{stats}")
                    result.columns = new_columns
                except Exception:
                    # Fallback to simple count if pivot fails
                    result = df.groupby(s2_column).size().reset_index(name=stats)

        # Add geometry if requested
        result = result.set_index(s2_column)
        if return_geometry:
            result = result.s2.s22geo()
        return result.reset_index()

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
            single-argument function to be applied to each H3 id
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
        result = [processor(func(s2id)) for s2id in self._df.index]
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
                {s2_id: processor(func(s2_id)) for s2_id in self._df.index},
                orient="index",
            )
            .stack()
            .to_frame(column_name)
            .reset_index(level=1, drop=True)
        )
        result = self._df.join(result)
        return finalizer(result)

    def _s2_tokens_to_geometries(self, s2_tokens) -> list:
        """Helper method to process S2 tokens into geometries.

        Parameters
        ----------
        s2_tokens : pandas.Series or list
            S2 tokens to process

        Returns
        -------
        list
            List of geometries (Polygon or MultiPolygon objects)
        """
        geometries = []
        for tokens in s2_tokens:
            try:
                if pd.isna(tokens):
                    # Handle NaN values - create empty geometry
                    geometries.append(Polygon())
                elif isinstance(tokens, list):
                    # Handle list of tokens - create a MultiPolygon
                    if len(tokens) == 0:
                        # Handle empty list - create empty geometry
                        geometries.append(Polygon())
                    else:
                        cell_geometries = [s2_to_geo(token) for token in tokens]
                        geometries.append(MultiPolygon(cell_geometries))
                else:
                    # Handle single token
                    geometries.append(s2_to_geo(tokens))
            except (ValueError, TypeError):
                if isinstance(tokens, list):
                    if len(tokens) == 0:
                        geometries.append(Polygon())
                    else:
                        cell_geometries = [s2_to_geo(token) for token in tokens]
                        geometries.append(MultiPolygon(cell_geometries))
                else:
                    # Try to handle as single token
                    try:
                        geometries.append(s2_to_geo(tokens))
                    except Exception:
                        # If all else fails, create empty geometry
                        geometries.append(Polygon())
        return geometries

    @staticmethod
    def _format_resolution(resolution: int) -> str:
        return f"s2_{str(resolution).zfill(2)}"
