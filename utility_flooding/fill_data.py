import pandas as pd

def collaborative_filtering(matrix_to_fill: pd.DataFrame):
    """Fill the matrix with collaborative filtering

    :param matrix_to_fill: the matrix to fill
    :returns: the filled matrix

    """
    return matrix_to_fill.fillna(2)