import pandas as pd
import numpy as np
from typing import List
from numpy.linalg import norm

import warnings
warnings.filterwarnings("error")


def collaborative_filtering(df_to_fill: pd.DataFrame, allow_col_all_nan: bool = False) -> pd.DataFrame:
    """Fill the matrix with collaborative filtering
    
    TODO Handle case when a column has all NaN values (average is NaN) (not needed)
    
    :param df_to_fill: the matrix to fill
    :param allow_col_all_nan: If true, a passed dataframe can have all NaN (Default: false)
    :returns: dataframe whose null are filled with collaborative filtering"""

    if not allow_col_all_nan and any( df_to_fill.isna().sum() == df_to_fill.shape[0]):
        raise Exception(f"This dataframe has a column with all NaN values")

    return_df = df_to_fill.copy()
    centered_df, col_means = item_centering_filling(df_to_fill.copy())
    
    for i in range(len(df_to_fill)):
        for j in range(len(df_to_fill.columns)):
            if pd.isna(df_to_fill.iloc[i,j]):
                col_similarities = cosine_similarity(centered_df[centered_df.columns[j]], centered_df)
                col_similarities = list(np.delete(col_similarities, j)) #remove the similarity with itself
                
                user_rates = list(centered_df.iloc[i])
                user_rates.pop(j) #remove the rate of the column to fill

                cell_value = (np.dot(col_similarities, user_rates)/sum(col_similarities)) + col_means[df_to_fill.columns[j]]
                
                cell_value = min(max(int(cell_value), 0), 100) #round to the nearest integer and clamp between 0 and 100
                #print(f"end value in cell {i} {j} = cell_value")
                return_df.iloc[i,j] = cell_value
    return return_df

def item_centering_filling(df: pd.DataFrame, alpha = 0.0000001) -> pd.DataFrame:
    """centers the matrix and fill null values

    to each column is subtracted the mean of the column and if the value is null, it is filled with the column mean

    :param df: the matrix to center
    :param alpha: the value to fill null values with (default 0.0000001 - to prevent division by zero)
    :returns: centered matrix with null values filled with column mean
    
    """
    new_df = df - df.mean()
    col_means = df.mean().to_dict()
    return new_df.fillna(alpha), col_means #fill with column mean


def cosine_similarity(v1: pd.DataFrame, v2: List) -> List[float]:
    """Calculate the cosine similarity of the vector in the dataframe
    
    :param v1: dataframe of reference
    :param v2: vector to compare
    :returns: A list of cosine similarities of 'v1' in the ist of 'v2'"""
    v1 = np.array(v1)
    v2 = v2.to_numpy()
    res = np.nan
    try:
        res = np.dot(v1,v2)/(norm(v2, axis=0)*norm(v1))
    except RuntimeWarning:
        print(f"RuntimeWarning happened maybe you did 0/0?\nv1 = \n{v1}\nv2 = \n{v2}")
        raise RuntimeWarning
    return res