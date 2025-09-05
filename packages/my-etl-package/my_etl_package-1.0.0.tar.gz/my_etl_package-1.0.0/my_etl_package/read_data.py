from pathlib import Path
import pandas as pd


def read_csv(file_path: Path) -> pd.DataFrame:
    """
    Read a CSV file into a pandas DataFrame.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Data read from the CSV.

    Example:
        >>> test_dir = Path().absolute().parent.parent/'data/test'
        >>> test_dir.mkdir(parents=True, exist_ok=True)
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        >>> df.to_csv(test_dir/'example.csv')
        >>> df = read_csv(test_dir/'example.csv')
        >>> isinstance(df, pd.DataFrame)
        True
    """
    return pd.read_csv(file_path)
