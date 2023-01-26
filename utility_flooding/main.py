# sources: 
# type hinting with dataframes https://stackoverflow.com/questions/54503964/type-hint-for-numpy-ndarray-dtype/63446142#63446142
# hint series https://stackoverflow.com/a/73699746
import pandas as pd
from typing import List
from svd_flood import controlled_flooding

data_source = "size_30_3" # which folder in data has the reference data

def main():
    utility_matrix: pd.DataFrame = pd.read_csv("../data/" + data_source + "/utility_matrix.csv")
    query_combinations: pd.DataFrame = pd.read_csv("../data/" + data_source + "/query_content.csv")
    asked_queries: List[dict] = pd.read_csv("../data/" + data_source + "/queries.csv")

    filled_utility = controlled_flooding(utility_matrix, asked_queries, query_combinations)
    filled_utility.to_csv("../data/" + data_source + "/utility_matrix_filled.csv", index = False)

if __name__ == "__main__":
    main()