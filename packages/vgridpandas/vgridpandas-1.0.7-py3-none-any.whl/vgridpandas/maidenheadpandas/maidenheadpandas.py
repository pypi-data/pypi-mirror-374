from typing import Union, Callable, Any
from collections import Counter
import pandas as pd
import geopandas as gpd
from vgrid.conversion.latlon2dggs import latlon2maidenhead as latlon_to_maidenhead
from pandas.core.frame import DataFrame
from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Polygon, MultiPolygon

from vgridpandas.utils.functools import wrapped_partial
from vgridpandas.utils.decorator import catch_invalid_dggs_id
from vgrid.conversion.dggs2geo.maidenhead2geo import maidenhead2geo as maidenhead_to_geo

AnyDataFrame = Union[DataFrame, GeoDataFrame]


@pd.api.extensions.register_dataframe_accessor("maidenhead")
class MaidenheadPandas:
    def __init__(self, df: DataFrame):
        self._df = df

    # maidenhead API
    # These methods simply mirror the Vgrid maidenhead API and apply maidenhead functions to all rows

    def latlon2maidenhead(
        self,
        resolution: int,
        lat_col: str = "lat",
        lon_col: str = "lon",
        set_index: bool = False,
    ) -> AnyDataFrame:
        """Adds maidenhead ID to (Geo)DataFrame.

        pd.DataFrame: uses `lat_col` and `lon_col` (default `lat` and `lon`)
        gpd.GeoDataFrame: uses `geometry`

        Assumes coordinates in epsg=4326.

        Parameters
        ----------
        resolution : int
            maidenhead resolution
        lat_col : str
            Name of the latitude column (if used), default 'lat'
        lon_col : str
            Name of the longitude column (if used), default 'lon'
        set_index : bool
            If True, the columns with maidenhead ID is set as index, default 'True'

        Returns
        -------
        (Geo)DataFrame with maidenhead IDs added
        """

        if not isinstance(resolution, int) or resolution not in range(1, 5):
            raise ValueError("Resolution must be an integer in range [1, 4]")

        if isinstance(self._df, gpd.GeoDataFrame):
            lons = self._df.geometry.x
            lats = self._df.geometry.y
        else:
            lons = self._df[lon_col]
            lats = self._df[lat_col]

        maidenhead_ids = [
            latlon_to_maidenhead(lat, lon, resolution) for lat, lon in zip(lats, lons)
        ]

        # maidenhead_column = self._format_resolution(resolution)
        maidenhead_column = "maidenhead"
        assign_arg = {maidenhead_column: maidenhead_ids, "maidenhead_res": resolution}
        df = self._df.assign(**assign_arg)
        if set_index:
            return df.set_index(maidenhead_column)
        return df

    def maidenhead2geo(self, maidenhead_column: str = None) -> GeoDataFrame:
        """Add geometry with Maidenhead geometry to the DataFrame. Assumes Maidenhead ID.

        Parameters
        ----------
        maidenhead_column : str, optional
            Name of the column containing Maidenhead IDs. If None, first checks for 'maidenhead' column,
            then assumes Maidenhead IDs are in the index.

        Returns
        -------
        GeoDataFrame with Maidenhead geometry

        Raises
        ------
        ValueError
            When an invalid Maidenhead ID is encountered
        """

        if maidenhead_column is not None:
            # maidenhead maidenhead_ids are in the specified column
            if maidenhead_column not in self._df.columns:
                raise ValueError(f"Column '{maidenhead_column}' not found in DataFrame")
            maidenhead_ids = self._df[maidenhead_column]

            # Handle both single maidenhead_ids and lists of maidenhead_ids
            geometries = self._maidenhead_ids_to_geometries(maidenhead_ids)

            result_df = self._df.copy()
            result_df["geometry"] = geometries
            return gpd.GeoDataFrame(result_df, crs="epsg:4326")

        else:
            # Check if 'maidenhead' column exists first
            if "maidenhead" in self._df.columns:
                # Maidenhead IDs are in the 'maidenhead' column
                maidenhead_ids = self._df["maidenhead"]

                # Handle both single maidenhead_ids and lists of maidenhead_ids
                geometries = self._maidenhead_ids_to_geometries(maidenhead_ids)

                result_df = self._df.copy()
                result_df["geometry"] = geometries
                return gpd.GeoDataFrame(result_df, crs="epsg:4326")
            else:
                # Maidenhead IDs are in the index
                return self._apply_index_assign(
                    wrapped_partial(maidenhead_to_geo),
                    "geometry",
                    finalizer=lambda x: gpd.GeoDataFrame(x, crs="epsg:4326"),
                )

    def maidenheadbin(
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
        Bin points into maidenhead cells and compute statistics, optionally grouped by a category column.

        Supports both GeoDataFrame (with point geometry) and DataFrame (with lat/lon columns).

        Parameters
        ----------
        resolution : int
            maidenhead resolution
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
            If True, return a GeoDataFrame with maidenhead cell geometry
        """
        # Validate inputs and prepare data
        # maidenhead_column = self._format_resolution(resolution)
        maidenhead_column = "maidenhead"
        df = self.latlon2maidenhead(resolution, lat_col, lon_col, False)

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
        group_cols = [maidenhead_column]
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
                    df.groupby([maidenhead_column, category_column])
                    .apply(cat_agg_func, include_groups=False)
                    .reset_index(name=stats)
                )
                result = result.pivot(
                    index=maidenhead_column, columns=category_column, values=stats
                )
                result = result.reindex(
                    columns=all_categories, fill_value=0 if stats == "variety" else None
                )
                result = result.reset_index()
                result.columns = [maidenhead_column] + [
                    f"{cat}_{stats}" for cat in all_categories
                ]
            else:
                # Handle categorical aggregation without category grouping
                result = (
                    df.groupby([maidenhead_column])
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
                result = pd.DataFrame(
                    columns=[maidenhead_column, category_column, stats]
                )
            else:
                try:
                    # Pivot categories to columns
                    result = result.pivot(
                        index=maidenhead_column, columns=category_column, values=stats
                    )
                    # Fill NaN values but avoid geometry columns to prevent GeoPandas warning
                    numeric_cols = result.select_dtypes(include=["number"]).columns
                    result[numeric_cols] = result[numeric_cols].fillna(0)
                    result = result.reset_index()

                    # Rename columns with category prefixes
                    new_columns = [maidenhead_column]
                    for col in sorted(result.columns[1:]):
                        if col == "NaN_category":
                            new_columns.append(f"NaN_{stats}")
                        else:
                            new_columns.append(f"{col}_{stats}")
                    result.columns = new_columns
                except Exception:
                    # Fallback to simple count if pivot fails
                    result = (
                        df.groupby(maidenhead_column).size().reset_index(name=stats)
                    )

        # Add geometry if requested
        result = result.set_index(maidenhead_column)
        if return_geometry:
            result = result.maidenhead.maidenhead2geo()
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
        result = [processor(func(maidenhead_id)) for maidenhead_id in self._df.index]
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
                {
                    maidenhead_id: processor(func(maidenhead_id))
                    for maidenhead_id in self._df.index
                },
                orient="index",
            )
            .stack()
            .to_frame(column_name)
            .reset_index(level=1, drop=True)
        )
        result = self._df.join(result)
        return finalizer(result)

    def _maidenhead_ids_to_geometries(self, maidenhead_ids) -> list:
        """Helper method to process maidenhead IDs into geometries.

        Parameters
        ----------
        maidenhead_ids : pandas.Series or list
            Maidenhead IDs to process

        Returns
        -------
        list
            List of geometries (Polygon or MultiPolygon objects)
        """
        geometries = []
        for mdh_ids in maidenhead_ids:
            try:
                if pd.isna(mdh_ids):
                    # Handle NaN values - create empty geometry
                    geometries.append(Polygon())
                elif isinstance(mdh_ids, list):
                    # Handle list of maidenhead_ids - create a MultiPolygon
                    if len(mdh_ids) == 0:
                        # Handle empty list - create empty geometry
                        geometries.append(Polygon())
                    else:
                        cell_geometries = [
                            maidenhead_to_geo(mdh_id) for mdh_id in mdh_ids
                        ]
                        geometries.append(MultiPolygon(cell_geometries))
                else:
                    # Handle single maidenhead_id
                    geometries.append(maidenhead_to_geo(mdh_ids))
            except (ValueError, TypeError):
                if isinstance(mdh_ids, list):
                    if len(mdh_ids) == 0:
                        geometries.append(Polygon())
                    else:
                        cell_geometries = [
                            maidenhead_to_geo(mdh_id) for mdh_id in mdh_ids
                        ]
                        geometries.append(MultiPolygon(cell_geometries))
                else:
                    # Try to handle as single maidenhead_id
                    try:
                        geometries.append(maidenhead_to_geo(mdh_ids))
                    except Exception:
                        # If all else fails, create empty geometry
                        geometries.append(Polygon())
        return geometries

    @staticmethod
    def _format_resolution(resolution: int) -> str:
        return f"maidenhead_{str(resolution).zfill(2)}"
