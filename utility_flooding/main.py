# sources: 
# type hinting with dataframes https://stackoverflow.com/questions/54503964/type-hint-for-numpy-ndarray-dtype/63446142#63446142
# hint series https://stackoverflow.com/a/73699746
import pandas as pd
from typing import List
#from pandera.typing import Series

data_source = "size_30" # which folder in data has the reference data

# reading the CSV file
utility_matrix = pd.read_csv("../data/" + data_source + "/utility_matrix.csv")

# displaying the contents of the CSV file
# print(csvFile)

def col_density(df:pd.DataFrame) -> "pd.Series[float]":
    return df.isna().sum()/len(df)


densities = col_density(utility_matrix)
print( densities ) 
print( "density 1 = " + str(densities[1])) 
# to go further https://www.tutorialspoint.com/how-to-get-the-index-and-values-of-series-in-pandas

################################à

queries = pd.read_csv("../data/" + data_source + "/queries.csv")


def query_dict(string:str) -> dict:
    temp = string.split(" AND ")
    pairs = [x.split("=") for x in temp]
    return dict(pairs)

print( query_dict(queries.iloc[0]["content"]) )

query_cont = pd.read_csv("../data/" + data_source + "/query_content.csv")

print( query_cont )