import subprocess
import sys

import pandas as pd


def install_packages(packages: list[str]) -> str:
    """
    Install packages using pip
    """
    ret = subprocess.run([sys.executable, "-m", "pip", "install", *packages])
    if ret.returncode != 0:
        return f"Failed to install {packages}"
    else:
        return f"Installed {packages} successfully"


def dataset_glance(dataset: pd.DataFrame) -> str:
    """
    Get a glance of a dataset with data type and sample data
    """
    analysis = {}
    for col in dataset.columns:
        col_data = dataset[col]
        analysis[col] = {
            "top_5_unique_values": col_data.value_counts().head(5).to_dict(),
        }
        if pd.api.types.is_numeric_dtype(col_data):
            analysis[col].update(
                {
                    "min": col_data.min(),
                    "max": col_data.max(),
                    "25%": col_data.quantile(0.25),
                    "50%": col_data.quantile(0.50),
                    "75%": col_data.quantile(0.75),
                }
            )
        analysis[col].update(
            {
                "unique_count": col_data.nunique(),
            }
        )
    info = {
        "dtypes": dataset.dtypes,
        "sample": dataset.head(3).to_dict(orient="records"),
        "analysis": analysis,
    }
    return str(info)


def column_analysis(df: pd.DataFrame, columns: list[str]) -> str:
    """
    Analyze specified columns in a dataframe

    Args:
        df: pandas DataFrame to analyze
        columns: list of column names to analyze

    Returns:
        dict containing analysis results for each column
    """
    results = {}
    for col in columns:
        if col not in df.columns:
            results[col] = f"Column {col} not found in dataframe"
            continue

        col_data = df[col]
        analysis = {
            "max": col_data.max() if pd.api.types.is_numeric_dtype(col_data) else None,
            "min": col_data.min() if pd.api.types.is_numeric_dtype(col_data) else None,
            "unique_count": col_data.nunique(),
            "top_5_values": col_data.value_counts().head(5).to_dict(),
            "dtype": str(col_data.dtype),
            "missing_count": col_data.isnull().sum(),
            "missing_percentage": col_data.isnull().mean(),
        }
    results[col] = analysis

    return str(results)
