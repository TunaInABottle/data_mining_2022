# sources: 
# type hinting with dataframes https://stackoverflow.com/questions/54503964/type-hint-for-numpy-ndarray-dtype/63446142#63446142
# hint series https://stackoverflow.com/a/73699746
import pandas as pd
from typing import List
from svd_flood import pick_best_query_set, select_queries_subset
from fill_data import collaborative_filtering

data_source = "size_30" # which folder in data has the reference data



def main():
    utility_matrix: pd.DataFrame = pd.read_csv("../data/" + data_source + "/utility_matrix.csv")
    query_combinations: pd.DataFrame = pd.read_csv("../data/" + data_source + "/query_content.csv")
    asked_queries: List[dict] = pd.read_csv("../data/" + data_source + "/queries.csv")



    queries_to_fill = pick_best_query_set(utility_matrix, asked_queries, query_combinations)
    query_ids = select_queries_subset(queries_to_fill, asked_queries)["id"]

    #print(utility_matrix[query_ids])

    utility_matrix[query_ids] = collaborative_filtering(utility_matrix[query_ids])


    print(utility_matrix[query_ids])

    
    






if __name__ == "__main__":
    main()