# My ETL Package

This package implements a simple **Extract–Transform–Load (ETL)** pipeline using Python.  
It processes CSV files from an input directory, transforms and integrate them into a single dataset, saves the results to an output directory, and loads the final dataset into a PostgreSQL database.

---


## 🔑 Pre-requisites

1. **Working Python environment**  
   Make sure you have a working Python environment set up, either locally or in Jupyter.  
   If you haven’t already, follow this guide:  
   [Setting up a Basic Python Development Environment](https://medium.com/@khhaledahmaad/setting-up-a-basic-python-development-environment-fd67e749825e)

2. **PostgreSQL database**  
   Ensure you have a PostgreSQL database installed and configured.  
   If you don’t have one already, download and install both PostgreSQL and PgAdmin from the official sources below, then use PgAdmin to create your first database:

   - [Download PostgreSQL](https://www.postgresql.org/download/)  
   - [Download PgAdmin](https://www.pgadmin.org/download/)  

   Once installed, you can follow this step-by-step guide to create a new database in PgAdmin:  
   [Creating a Database using PgAdmin](https://www.tutorialsteacher.com/postgresql/create-database)

---

## 📦 Installation

Install directly from **PyPI**:

```bash
pip install my-etl-package
````

Set up your environment variables in a `.env` file (required for PostgreSQL connection):

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
```

---

## ⚙️ Package Contents

After installation, you can inspect the available functions:

```python
import my_etl_package
help(my_etl_package)
```

Typical contents:

```
NAME
    my_etl_package

PACKAGE CONTENTS
    utils

FUNCTIONS
    read_csv(file_path: pathlib.Path) -> pandas.DataFrame
    transform_data(dfs: List[pandas.DataFrame]) -> pandas.DataFrame
    write_csv(df: pandas.DataFrame, output_path: pathlib.Path) -> None
    load_to_db(df: pd.DataFrame, table_name: str, engine: sqlalchemy.engine.Engine) -> None
```

Utilities inside `my_etl_package.utils`:

```
FUNCTIONS
    list_csv_files(directory_path: pathlib.Path) -> List[pathlib.Path]
    PostgresConnector().get_db_connection() -> sqlalchemy.engine.Engine
```

---

## 📂 Data Directory Structure (Recommended but not Mandatory)

When running locally, organize your data as follows (relative to your **current working directory**):

```
pwd/
├── .env              # Environment variables (PostgreSQL credentials)
└── data/
    ├── raw/          # Place input CSV files here
    └── processed/    # Processed output CSVs will be written here
```

---

## 🛠️ Usage

### 1. Use Methods Individually

#### 1.1. List all CSV files in a directory


```python
from pathlib import Path
from my_etl_package.utils import list_csv_files

input_directory = Path().absolute() / "data/raw"
files = list_csv_files(input_directory)
print(files)
```

    [WindowsPath('C:/Users/khhal/Documents/data/raw/103_semester_2_week_1_raw.csv'), WindowsPath('C:/Users/khhal/Documents/data/raw/104_semester_2_week_2_raw.csv')]
    

#### 1.2. Read a CSV file


```python
from my_etl_package import read_csv

df1 = read_csv(files[0])
df1
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>from</th>
      <th>message</th>
      <th>status</th>
      <th>date_sent</th>
      <th>student_id</th>
      <th>course_code</th>
      <th>student_name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>447440049121</td>
      <td>3821656</td>
      <td>received</td>
      <td>2023-01-25 13:22:10+00:00</td>
      <td>3821656</td>
      <td>NaN</td>
      <td>Khaled Ahmed</td>
    </tr>
    <tr>
      <th>1</th>
      <td>447440049121</td>
      <td>3821656 103</td>
      <td>received</td>
      <td>2023-01-25 12:26:28+00:00</td>
      <td>3821656</td>
      <td>103.0</td>
      <td>Khaled Ahmed</td>
    </tr>
  </tbody>
</table>
</div>




```python
from my_etl_package import read_csv

df2 = read_csv(files[1])
df2
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>from</th>
      <th>message</th>
      <th>status</th>
      <th>date_sent</th>
      <th>student_id</th>
      <th>course_code</th>
      <th>student_name</th>
      <th>session</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>4.474400e+11</td>
      <td>3821656 104</td>
      <td>received</td>
      <td>2023-02-02 13:24:02+00:00</td>
      <td>3821656.0</td>
      <td>104.0</td>
      <td>Khaled Ahmed</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



#### 1.3. Transform multiple CSVs


```python
from my_etl_package import transform_data

combined_df = transform_data([df1, df2])
combined_df
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>from</th>
      <th>message</th>
      <th>status</th>
      <th>date_sent</th>
      <th>student_id</th>
      <th>course_code</th>
      <th>student_name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>4.474400e+11</td>
      <td>3821656</td>
      <td>received</td>
      <td>2023-01-25 13:22:10+00:00</td>
      <td>3821656.0</td>
      <td>NaN</td>
      <td>Khaled Ahmed</td>
    </tr>
    <tr>
      <th>1</th>
      <td>4.474400e+11</td>
      <td>3821656 103</td>
      <td>received</td>
      <td>2023-01-25 12:26:28+00:00</td>
      <td>3821656.0</td>
      <td>103.0</td>
      <td>Khaled Ahmed</td>
    </tr>
    <tr>
      <th>2</th>
      <td>4.474400e+11</td>
      <td>3821656 104</td>
      <td>received</td>
      <td>2023-02-02 13:24:02+00:00</td>
      <td>3821656.0</td>
      <td>104.0</td>
      <td>Khaled Ahmed</td>
    </tr>
  </tbody>
</table>
</div>



#### 1.4. Write processed DataFrame to CSV


```python
from pathlib import Path
from my_etl_package import write_csv

output_path = Path().absolute() / "data/processed"
output_path.mkdir(exist_ok=True)
output_file = output_path / "processed.csv"
write_csv(combined_df, output_file)
```

#### 1.5. Load DataFrame into PostgreSQL


```python
from dotenv import load_dotenv
from my_etl_package.utils import PostgresConnector
from my_etl_package import load_to_db


# Load environment variables
load_dotenv()

# If .env is in a different location, specify the path:
# load_dotenv('./some_other_location/.env')

table_name = "etl_pipeline_processed"
load_to_db(combined_df, table_name)
```

    INFO:my_etl_package.utils.connect_db:PostgresConnector initialized with loaded credentials.
    INFO:my_etl_package.utils.connect_db:Database engine generated for: postgresql://postgres:Khal8891@localhost:5434/postgres.
    

### 2. Run the Full ETL Pipeline

Here’s an end-to-end pipeline script:

In `etl_pipeline.py` (name as you wish) in the current working directory ->


```python
import logging
from pathlib import Path
from dotenv import load_dotenv
from my_etl_package.utils import list_csv_files, PostgresConnector
from my_etl_package import read_csv, transform_data, write_csv, load_to_db

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables
load_dotenv()
logging.info("Environment variables loaded.")

# Set up workspace
base = Path().absolute() / "data"
input_directory = base / "raw"
output_directory = base / "processed"
output_filename = "etl_pipeline_processed.csv"
output_path = output_directory / output_filename

# Create output directory if it doesn't exist
output_directory.mkdir(exist_ok=True)
logging.info(f"Output directory set to: {output_directory}")


def main():
    logging.info("Starting ETL pipeline...")

    # Configuration
    table_name = "etl_pipeline_processed"
    logging.info(f"Using table: {table_name}")

    # Extract
    logging.info(f"Looking for CSV files in: {input_directory}")
    file_paths = list_csv_files(input_directory)
    logging.info(f"Found {len(file_paths)} CSV files.")

    # Read
    dfs = (read_csv(f) for f in file_paths)

    # Transform
    logging.info("Transforming data...")
    combined_df = transform_data(dfs)
    logging.info("Data transformation complete.")

    # Load - write to CSV
    logging.info("Writing processed data to CSV...")
    write_csv(combined_df, output_path)
    logging.info("Data written to CSV.")

    # Load - load into Postgres
    logging.info("Loading data into PostgreSQL...")
    load_to_db(combined_df, table_name)
    logging.info("Data successfully loaded into PostgreSQL.")

    logging.info("ETL pipeline finished.")

main()
```

    INFO:root:Environment variables loaded.
    INFO:root:Output directory set to: C:\Users\khhal\Documents\data\processed
    INFO:root:Starting ETL pipeline...
    INFO:root:Using table: etl_pipeline_processed
    INFO:root:Looking for CSV files in: C:\Users\khhal\Documents\data\raw
    INFO:root:Found 2 CSV files.
    INFO:root:Transforming data...
    INFO:root:Data transformation complete.
    INFO:root:Writing processed data to CSV...
    INFO:root:Data written to CSV.
    INFO:root:Loading data into PostgreSQL...
    INFO:my_etl_package.utils.connect_db:PostgresConnector initialized with loaded credentials.
    INFO:my_etl_package.utils.connect_db:Database engine generated for: postgresql://postgres:Khal8891@localhost:5434/postgres.
    INFO:root:Data successfully loaded into PostgreSQL.
    INFO:root:ETL pipeline finished.
    

Run it:

```bash
python etl_pipeline.py
```

---

## ✅ Features

* 🔎 Automatically detects all CSV files in `data/raw/`
* 🛠️ Cleans and transforms raw datasets
* 💾 Stores processed results in `data/processed/`
* 🗄️ Loads final output into a PostgreSQL table

---

## 📝 Notes

* Ensure PostgreSQL is running and accessible with the credentials in your `.env` file.
* Place your input CSV files in the same input directory before running the pipeline.

---
