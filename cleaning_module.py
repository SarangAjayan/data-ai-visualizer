import pandas as pd

def clean_data(df):
    df_clean = df.copy()
    df_clean = df_clean.dropna(thresh=0.5 * len(df_clean), axis=1)
    df_clean = df_clean.fillna(method='ffill')
    return df_clean
