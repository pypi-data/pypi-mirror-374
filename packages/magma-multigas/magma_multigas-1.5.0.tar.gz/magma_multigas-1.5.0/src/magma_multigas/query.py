import numpy as np
import pandas as pd

from pandas.api.types import is_numeric_dtype

from .validator import (
    validate_status,
    validate_column_name,
    validate_comparator,
    validate_datetime,
    validate_index_as_datetime,
)

from .utilities import (
    convert_to_direction,
    convert_to_quadrant,
)

from typing import (
    List,
    Dict,
    Any,
    Self,
    Tuple,
)


def intersection(list_one: List[Any], list_two: List[Any]) -> List[Any]:
    """Get intersection between two lists

    Args:
        list_one (List[Any]): First List
        list_two (List[Any]): Second List

    Returns:
        List[Any]
    """
    intersect_list: List[Any] = [value for value in list_one if value in list_two]
    return intersect_list


def unique(list_one: List[Any], list_two: List[Any]) -> List[Any]:
    """Get unique elements from two lists

    Args:
        list_one (List[Any]): First List
        list_two (List[Any]): Second List

    Returns:
        List[Any]: Unique elements
    """
    return list(set(list_one + list_two))


class Query:
    def __init__(self, df: pd.DataFrame, datetime_columns: str = None):
        """Query data

        Args:
            df (pd.DataFrame): data frame

        Attributes:
            df (pd.DataFrame): data frame
        """
        if datetime_columns is not None:
            df.set_index(datetime_columns, inplace=True)

        self.df_original: pd.DataFrame = df
        self.df: pd.DataFrame = df.copy(deep=True)
        self.columns: List[str] = self.df_original.columns.tolist()
        self.columns_selected: List[str] = []
        self.columns_numeric: List[str] = self.df.select_dtypes(include=np.number).keys().to_list()
        self.start_date, self.start_datetime = self._datetime(df)
        self.end_date, self.end_datetime = self._datetime(df, -1)

    @staticmethod
    def _datetime(df: pd.DataFrame, index: int = 0) -> Tuple[str, pd.Timestamp] | Tuple[str, Any]:
        pd_index = df.index[index]
        if isinstance(df.index, pd.DatetimeIndex):
            return pd_index.strftime('%Y-%m-%d'), pd.Timestamp(pd_index)

        return str(pd_index), pd_index

    def refresh(self) -> Self:
        """Refresh dataframe with the original one"""
        df = self.df_original.copy(deep=True)
        self.df = df
        self.columns_selected = []
        self.columns_numeric: List[str] = self.df.select_dtypes(include=np.number).keys().to_list()
        self.start_date, self.start_datetime = self._datetime(df)
        self.end_date, self.end_datetime = self._datetime(df, -1)
        return self

    def translate_comparator(self, column_name: str, comparator: str, value: Any) -> pd.DataFrame:
        """Translate comparator

        Args:
            column_name (str): column name
            comparator (str): comparator
            value (Any): value

        Returns:
            pd.DataFrame: data frame
        """
        validate_comparator(comparator)

        df = self.df.copy()

        column = df[column_name]
        if column_name == df.index.name:
            column = df.index

        if comparator in ['==', 'like', 'equal', 'eq', 'sama dengan']:
            return df[column == value]
        if comparator in ['!=', 'ne', 'not equal', 'tidak sama dengan']:
            return df[column != value]
        if comparator in ['>', 'gt', 'greater than', 'lebih besar', 'lebih besar dari']:
            return df[column > value]
        if comparator in ['<', 'lt', 'less than', 'kurang', 'kurang dari']:
            return df[column < value]
        if comparator in ['>=', 'gte', 'greater than equal', 'lebih besar sama dengan']:
            return df[column >= value]
        if comparator in ['<=', 'lte', 'less than equal', 'kurang dari sama dengan']:
            return df[column <= value]
        self.df = df
        return self.df

    def is_filtered(self) -> bool:
        """Check if data is filtered

        Returns:
            bool: True if data is filtered
        """
        return False if self.df_original.equals(self.df) else True

    def column_has_nan(self, column_name: str) -> bool:
        """Check if column has NULL or NaN value.

        Args:
            column_name (str): column name

        Returns:
            bool: True if column is empty
        """
        validate_column_name(column_name, self.columns)
        return True if (self.df[column_name].isnull().values.any()) else False

    def columns_have_nan(self, columns_name: str | List[str]) -> pd.Series:
        """Check if columns have NaN value."""
        empty_dict: Dict[str, bool] = {}

        if isinstance(columns_name, str):
            columns_name: List[str] = [columns_name]

        for column_name in columns_name:
            empty_dict[column_name]: bool = self.column_has_nan(column_name)

        return pd.Series(empty_dict)

    def column_is_empty(self, column_name: str) -> bool:
        """Check if column is empty.

        Args:
            column_name (str): column name

        Returns:
            bool: True if column is empty
        """
        validate_column_name(column_name, self.columns)
        return True if (self.df[column_name].sum() == 0) else False

    def columns_are_empty(self, columns_name: str | List[str] = None, empty_only: bool = False) -> pd.Series:
        """Returnn ALL empty columns

        Args:
            columns_name (str, List[str]): columns name
            empty_only (bool): show only empty columns

        Returns:
            Dict[str, bool]: all empty columns
        """
        empty_dict: Dict[str, bool] = {}
        all_empty_dict: Dict[str, bool] = {}

        columns_selected: int = len(self.columns_selected)

        if columns_name is None:
            columns_name = self.columns

        if columns_selected > 0:
            columns_name = self.columns_selected

        if isinstance(columns_name, str):
            columns_name: List[str] = [columns_name]

        columns_name = intersection(columns_name, self.columns_numeric)

        for column_name in columns_name:
            # Check column type and make sure it is numeric
            if is_numeric_dtype(self.df[column_name]) is False:
                continue
            is_empty: bool = self.column_is_empty(column_name)

            if empty_only is True and is_empty is True:
                all_empty_dict[column_name]: bool = self.column_is_empty(column_name)

            empty_dict[column_name]: bool = self.column_is_empty(column_name)

        if empty_only is True:
            return pd.Series(all_empty_dict)

        return pd.Series(empty_dict)

    def count(self) -> int:
        """Count number of data

        Returns:
            int: number of data
        """
        return len(self.get())

    def reset_columns(self) -> Self:
        """Reset selected columns

        Returns:
            Self: self
        """
        self.columns_selected: List[str] = []
        return self

    def select_columns(self, column_names: str | List[str] = None,
                       numeric_only: bool = False) -> Self:
        """Select columns

        Args:
            column_names (str | List(str)): column names
            numeric_only (bool): Select numeric columns only

        Returns:
            self (Self)
        """
        skip_validating: bool = False

        if (column_names is None) & (numeric_only is True):
            self.select_numeric_columns(column_names, skip_validating=True)
            return self

        if column_names is None:
            column_names = self.columns
            skip_validating = True

        if isinstance(column_names, str):
            column_names = [column_names]

        if skip_validating is False:
            for column_name in column_names:
                validate_column_name(column_name, self.columns)

        self.columns_selected: List[str] = column_names

        if numeric_only is True:
            self.select_numeric_columns(column_names, skip_validating=True)

        return self

    def select_numeric_columns(self, column_names: str | List[str] = None,
                               skip_validating: bool = False) -> Self:
        """Select only numeric columns from dataframe.

        Args:
            column_names (str | List[str]): column names
            skip_validating (bool): Skip validating column names

        Returns:
            self (Self)
        """
        numeric_columns: List[str] = self.columns_numeric

        if column_names is None:
            self.columns_selected = numeric_columns
            return self

        if isinstance(column_names, str):
            column_names = [column_names]

        if skip_validating is False:
            for column_name in column_names:
                validate_column_name(column_name, self.columns)

        numeric_columns = intersection(column_names, numeric_columns)

        if len(numeric_columns) == 0:
            print("⚠️ No numeric column(s) found in your selected columns: {}".format(column_names))

        self.columns_selected = numeric_columns
        return self

    def where(self, column_name: str, comparator: str, value: Any) -> Self:
        """Filter data based on column value

        Args:
            column_name (str): column name
            comparator (str): comparator
            value (Any): value

        Returns:
            self (Self)
        """
        if column_name == 'Status_Flag':
            self.where_status(value)

        column_list: List[str] = self.columns
        validate_column_name(column_name, column_list)

        self.df = self.translate_comparator(column_name, comparator, value)
        return self

    def where_status(self, value: Any) -> Self:
        """Filter status Flag

        Args:
            value (Any): Status value

        Returns:
            self (Self)
        """
        validate_status(int(value))
        self.df = self.translate_comparator('Status_Flag', '==', value)
        return self

    def where_date(self, date_str: str) -> Self:
        """Filter data based on date string

        Args:
            date_str (str): date string with format YYYY-MM-DD
        """
        self.df = self.df.loc[date_str]
        return self

    def where_values_between(self, column_name: str, start_value: int | float,
                             end_value: int | float) -> Self:
        """Filter data based on two values in specified column

        Args:
            column_name (str): column name
            start_value (int | float): start value
            end_value (int | float): end value

        Returns:
            self (Self)
        """
        column_list: List[str] = self.columns
        validate_column_name(column_name, column_list)

        df = self.df
        self.df = df[df[column_name].between(start_value, end_value)]
        return self

    def add_wind_direction(self, wind_direction_column_name: str, as_code: bool = False,
                           direction_to_use: int = 16) -> Self:
        """Add wind direction column.

        Args:
            wind_direction_column_name (str): column name
            as_code (bool): add wind direction column as code. Defaults to False
            direction_to_use (int): direction to use. Default is 16

        Returns:
            self (Self)
        """
        self.df['wind_direction'] = self.df.apply(
            lambda row: convert_to_direction(direction_degree=row[wind_direction_column_name],
                                             return_as_code=as_code, direction_to_use=direction_to_use), axis=1)

        print(f"✅ 'wind_direction' column has been added to dataframe.")
        return self

    def add_quadrant(self, wind_direction_column_name: str, as_code: bool = False,
                     quadrant_to_use: int = 8) -> Self:
        """Add quadrant column.

        Args:
            wind_direction_column_name (str): column name
            as_code (bool): add quadrant column as code. Default is False
            quadrant_to_use (int): quadrant direction. Default is 8

        Returns:
            self (Self)
        """
        self.df['quadrant'] = self.df.apply(
            lambda row: convert_to_quadrant(direction_degree=row[wind_direction_column_name],
                                            return_as_code=as_code, quadrant_to_use=quadrant_to_use), axis=1)
        return self

    def where_date_between(self, start_date: str, end_date: str) -> Self:
        """Filter data based on start and end date

        Args:
            start_date (str): start date. Date format yyyy-mm-dd or yyyy-mm-dd HH:MM:SS
            end_date (str): end date. Date format yyyy-mm-dd or yyyy-mm-dd HH:MM:SS

        Raises:
            ValueError: If start_date and end_date are not different

        Returns:
            self (Self)
        """
        validate_index_as_datetime(self.df)
        validate_datetime(start_date)
        validate_datetime(end_date)

        start_datetime: pd.Timestamp = pd.to_datetime(start_date)
        end_datetime: pd.Timestamp = pd.to_datetime(end_date)

        if (start_datetime > end_datetime) or (start_datetime == end_datetime):
            raise ValueError("⛔ end_date must be greater than start_date. "
                             "Also start_date and end_date must be different")

        self.start_date = start_datetime.strftime('%Y-%m-%d')
        self.end_date = end_datetime.strftime('%Y-%m-%d')

        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

        df = self.df
        self.df: pd.DataFrame = df[(df.index >= start_datetime) & (df.index <= end_datetime)]
        return self

    def get(self, inplace: bool = True) -> pd.DataFrame:
        """Get filtered data

        Returns:
            pd.DataFrame: filtered data
        """
        if inplace is False:
            df = self.df
            self.df = self.df_original.copy()
            return df

        if len(self.columns_selected) == 0:
            return self.df

        self.df = self.df[self.columns_selected]
        self.columns_numeric: List[str] = self.df.select_dtypes(include=np.number).keys().to_list()
        return self.df
