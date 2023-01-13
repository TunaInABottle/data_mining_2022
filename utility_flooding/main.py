# sources: 
# type hinting with dataframes https://stackoverflow.com/questions/54503964/type-hint-for-numpy-ndarray-dtype/63446142#63446142
# hint series https://stackoverflow.com/a/73699746
import pandas as pd
from typing import List
import statistics
#from pandera.typing import Series

data_source = "size_30" # which folder in data has the reference data



def col_density(df:pd.DataFrame) -> "pd.Series[float]":
    return statistics.mean(df.isna().sum()/(len(df)))

#print( densities ) 
#print( "density 1 = " + str(densities[1])) 
# to go further https://www.tutorialspoint.com/how-to-get-the-index-and-values-of-series-in-pandas

################################à


def query_dict(query_string:str, query_id:str) -> dict:
    """change a query written as string to a dictionary

    :param query_string: the query written as "key1=value1 AND key2=value2 AND ..."
    :param query_id: the query id
    :returns: a dict with the query id and the query string as key value pairs

    """
    temp = query_string.split(" AND ")
    pairs = [x.split("=") for x in temp]
    pairs_dict = dict(pairs)
    pairs_dict["id"] = query_id
    return pairs_dict

def get_query_dict(queries:pd.DataFrame) -> List[dict]:
    return [query_dict(queries.iloc[i]["content"], queries.iloc[i]["id"]) for i in range(len(queries))]



def main():
    utility_matrix: pd.DataFrame = pd.read_csv("../data/" + data_source + "/utility_matrix.csv")
    possible_query_cont: pd.DataFrame = pd.read_csv("../data/" + data_source + "/query_content.csv")
    queries_raw: List[dict] = pd.read_csv("../data/" + data_source + "/queries.csv")

    densities = col_density(utility_matrix)
    queries = get_query_dict(queries_raw)

    print(possible_query_cont.columns)

    best_queries_candidates(utility_matrix, queries_raw, possible_query_cont)


def best_queries_candidates(utility_matrix: pd.DataFrame, queries: pd.DataFrame, possible_query_cont: pd.DataFrame):
    """Pick the best keys based on the density of the queries

    :param utility_matrix: the utility matrix from which calculate the density
    :param queries: full description of the queries
    :param possible_query_cont: the possible query content
    :returns: the best key and its density
    """
    best_queries_set = ["", 0]
    for query_key in possible_query_cont.columns:
        queries_set_density = get_queries_set_density(utility_matrix, queries, query_key)
        if queries_set_density > best_queries_set[1]:
            best_queries_set = [query_key, queries_set_density]
    print(best_queries_set)
    return(best_queries_set)


def get_queries_set_density(utility_matrix: pd.DataFrame, queries: pd.DataFrame, col_name: str) -> float:
    """Calculate density of a specified subset of columns

    :param utility_matrix: the utility matrix from which calculate the density
    :param queries: full description of the queries
    :param col_name: the name of the column to filter the queries
    :returns: the density of the subset of columns
    """
    filtered_queries_ids = queries.iloc[[col_name in x for x in queries["content"]]]["id"]
    return col_density(utility_matrix[filtered_queries_ids])

if __name__ == "__main__":
    main()