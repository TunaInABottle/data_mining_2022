# sources: 
# type hinting with dataframes https://stackoverflow.com/questions/54503964/type-hint-for-numpy-ndarray-dtype/63446142#63446142
# hint series https://stackoverflow.com/a/73699746
import pandas as pd
from typing import List
import statistics
from svd_flood import pick_best_query_set
#from pandera.typing import Series

data_source = "size_30" # which folder in data has the reference data



def main():
    utility_matrix: pd.DataFrame = pd.read_csv("../data/" + data_source + "/utility_matrix.csv")
    possible_query_cont: pd.DataFrame = pd.read_csv("../data/" + data_source + "/query_content.csv")
    queries_raw: List[dict] = pd.read_csv("../data/" + data_source + "/queries.csv")

    #print(possible_query_cont.columns)

    print("calc first")
    queries_to_fill = pick_best_query_set(utility_matrix, queries_raw, possible_query_cont)
    print("finish calc first, calc second")
    queries_to_fill = pick_best_query_set(utility_matrix, queries_raw, possible_query_cont, candidate=queries_to_fill)
    print("3")
    queries_to_fill = pick_best_query_set(utility_matrix, queries_raw, possible_query_cont, candidate=queries_to_fill)
    print("4")
    queries_to_fill = pick_best_query_set(utility_matrix, queries_raw, possible_query_cont, candidate=queries_to_fill)
    print("5")
    queries_to_fill = pick_best_query_set(utility_matrix, queries_raw, possible_query_cont, candidate=queries_to_fill)
    print("6")
    queries_to_fill = pick_best_query_set(utility_matrix, queries_raw, possible_query_cont, candidate=queries_to_fill)



if __name__ == "__main__":
    main()