from typing import List
from pathlib import Path


def list_csv_files(directory_path: Path) -> List[Path]:
    """
    List all CSV files in a given directory.

    Args:
        directory_path (str): Path to the directory.

    Returns:
        list: List of CSV file paths.

    Example:
        >>> top_dir = Path().absolute().parent.parent
        >>> Path(top_dir/'data/test').mkdir(parents=True, exist_ok=True)
        >>> open(top_dir/'data/test/sample.csv', 'w').close()
        >>> files = list_csv_files(top_dir/'data/test')
        >>> 'sample.csv' in [file.name for file in files]
        True
        >>> len(files) >= 1
        True
    """
    return list(Path(directory_path).glob("**/*.csv"))
