from typing import List
import pandas as pd


def transform_data(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Concatenate a list of pandas DataFrames into a single DataFrame,
    and clean the data by removing any NaN values and duplicate rows.

    Args:
        dfs (list[pd.DataFrame]): List of DataFrames to concatenate.

    Returns:
        pd.DataFrame: Combined DataFrame, with NaN values and duplicates dropped.

    Example:
        >>> import numpy as np
        >>> import pandas as pd
        >>> df1 = pd.DataFrame([[1, 2, np.nan], [2, 3, np.nan], [np.nan, np.nan, np.nan]])
        >>> df2 = pd.DataFrame([[2, 3, np.nan], [3, 4, np.nan], [4, np.nan, np.nan]])
        >>> transformed = transform_data([df1, df2])
        >>> transformed.shape
        (4, 2)
        >>> int(transformed.isna().all(axis=1).sum())  # Total rows with all NaN values
        0
        >>> int(transformed.isna().all().sum())  # Total index (columns) with all NaN values
        0
        >>> int(transformed.duplicated().sum())  # Total duplicates
        0
    """
    # Concatenate the DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)

    # Drop NaN values if the whole row is empty
    combined_df.dropna(how="all", inplace=True)

    # Drop NaN values if the whole column is empty
    combined_df.dropna(how="all", axis=1, inplace=True)

    # Drop duplicate rows
    combined_df.drop_duplicates(inplace=True)

    return combined_df
