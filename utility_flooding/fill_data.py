import pandas as pd
import numpy as np
from typing import List
from numpy.linalg import norm

def collaborative_filtering(df_to_fill: pd.DataFrame) -> pd.DataFrame:
    """Fill the matrix with collaborative filtering
    
    :param df_to_fill: the matrix to fill
    :returns: dataframe whose null are filled with collaborative filtering"""
    return_df = df_to_fill.copy()
    centered_df = item_centering_filling(df_to_fill.copy())
    
    for i in range(len(df_to_fill)):
        for j in range(len(df_to_fill.columns)):
            if pd.isna(df_to_fill.iloc[i,j]):
                col_similarities = cosine_similarity(centered_df[centered_df.columns[j]], centered_df)
                col_similarities = list(np.delete(col_similarities, j)) #remove the similarity with itself
                col_means = list(df_to_fill.mean())
                col_means.pop(j) #remove the mean of the column to fill

                #print(f"end value in cell {i} {j} = {np.dot(col_similarities, col_means)/sum(col_similarities)}")
                return_df.iloc[i,j] = np.dot(col_similarities, col_means)/sum(col_similarities)
    return return_df

def item_centering_filling(df: pd.DataFrame) -> pd.DataFrame:
    """centers the matrix and fill null values

    to each column is subtracted the mean of the column and if the value is null, it is filled with the column mean

    :param df: the matrix to center
    :returns: centered matrix with null values filled with column mean
    
    """
    df = df - df.mean()
    return (df.fillna(df.mean())) #fill with column mean


def cosine_similarity(v1: pd.DataFrame, v2: List) -> List[float]:
    """Calculate the cosine similarity of the vector in the dataframe
    
    :param v1: dataframe of reference
    :param v2: vector to compare
    :returns: A list of cosine similarities"""
    v1 = np.array(v1)
    v2 = v2.to_numpy()
    return np.dot(v1,v2)/(norm(v2, axis=0)*norm(v1))