import pandas as pd
import numpy as np

def clean_data(df):
    df_clean = df.copy()

    # 1. Rename columns (trim, lowercase, replace spaces/symbols)
    df_clean.columns = [col.strip().lower().replace(" ", "_").replace("-", "_") for col in df_clean.columns]

    # 2. Remove duplicates
    df_clean = df_clean.drop_duplicates()

    # 3. Drop columns with >50% missing
    df_clean = df_clean.dropna(thresh=0.5 * len(df_clean), axis=1)

    # 4. Detect column types
    for col in df_clean.columns:
        if pd.api.types.is_numeric_dtype(df_clean[col]):
            # Fill numeric NaNs with median
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        elif pd.api.types.is_datetime64_any_dtype(df_clean[col]):
            # Fill dates with earliest valid date
            df_clean[col] = df_clean[col].fillna(df_clean[col].min())
        else:
            # Fill categorical with mode
            if df_clean[col].dtype == "object":
                df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0])

    return df_clean
