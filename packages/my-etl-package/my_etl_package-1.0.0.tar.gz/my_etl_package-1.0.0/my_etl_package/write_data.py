from pathlib import Path
import pandas as pd


def write_csv(df: pd.DataFrame, output_path: Path) -> None:
    """
    Write a pandas DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame to save.
        output_path (str): Path to save the CSV file.

    Example:
        >>> from pathlib import Path
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        >>> test_dir = Path().absolute().parent.parent/'data/test'
        >>> test_dir.mkdir(parents=True, exist_ok=True)
        >>> write_csv(df, test_dir/'output.csv')
        >>> (test_dir/'output.csv').exists()
        True
    """
    df.to_csv(output_path, index=False)
