import pandas as pd
from typing import List, Tuple
import statistics

def density(df:pd.DataFrame) -> "pd.Series[float]":
    if len(df) == 0 or len(df.columns) == 0:
        return None
    return statistics.mean(df.isna().sum()/(len(df)))

#print( densities ) 
#print( "density 1 = " + str(densities[1])) 
# to go further https://www.tutorialspoint.com/how-to-get-the-index-and-values-of-series-in-pandas

############################

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



def pick_best_query_set(utility_matrix: pd.DataFrame, queries: pd.DataFrame, possible_query_cont: pd.DataFrame, candidate = {}, eval_func = density):
    """Pick the best set of queriesv based on a metric of choice

    :param utility_matrix: the utility matrix from which calculate the density
    :param queries: full description of the queries
    :param possible_query_cont: a table containing all keys and values a query can have
    :param candidate: the current best key and its density
    :param eval_func: the function to evaluate the subset of queries
    :returns: the best key and its density
    """
    # @TODO make candidate as dict
    
    # iterate query keys
    candidate = add_best_query_key(candidate, utility_matrix, queries, possible_query_cont, eval_func)

    print(candidate)
    return(candidate)

def add_best_query_key(candidate: dict, utility_matrix: pd.DataFrame, queries: pd.DataFrame, possible_query_cont: pd.DataFrame, eval_func = density):
    """Add the best query key to the current candidate

    :param utility_matrix: the utility matrix from which calculate the density
    :param queries: full description of the queries
    :param possible_query_cont: a table containing all keys and values a query can have
    :param candidate: the current best key and its density
    :param eval_func: the function to evaluate the subset of queries
    :returns: the best key and its density
    """
    # define the starting value of the candidate
    starting_value: float = calculate_queries_set_value(utility_matrix, queries, candidate, eval_func = eval_func)
    new_candidate: Tuple[dict, float] = [candidate, starting_value]

    # remove the already selected queries
    unused_query_keys: List[str] = possible_query_cont.drop(columns = list(candidate.keys())).columns

    # iterate existing non-chosen keys
    for query_key in unused_query_keys:
        new_query_dict: dict = candidate.copy()
        new_query_dict[query_key] = None
        query_set_value:float = calculate_queries_set_value(utility_matrix, queries, new_query_dict, eval_func = eval_func)
        if query_set_value is not None and query_set_value > new_candidate[1]:
            # proclaim it as the new best
            new_candidate = [new_query_dict, query_set_value]
    return(new_candidate[0])

def calculate_queries_set_value(utility_matrix: pd.DataFrame, queries: pd.DataFrame, query_subset: List[str], eval_func = density) -> float:
    """Calculate the specified metric over a specified subset of queries

    :param utility_matrix: the utility matrix from which calculate the function
    :param queries: a table containing all keys and values a query can have
    :param col_names: the elements over which filter
    :param eval_func: the function to evaluate the subset of queries
    :returns: the density of the subset of columns
    """
    if query_subset == {}:
        return 0

    filtered_queries_ids = select_queries_subset(query_subset, queries)["id"]
    return eval_func(utility_matrix[filtered_queries_ids])

def select_queries_subset(query_dict: dict, query_data: pd.DataFrame):
    """Makes a subset of the queries that match 'query_dict'

    :param query_dict: which elements are going to be filtered
    :param query_data: the query dataset
    :returns the filtered query dataset
    """
    query_elms = list(query_dict.keys()) + list(filter(lambda item: item is not None, query_dict.values()))
    fits_criteria = [all(elm in query for elm in query_elms ) for query in query_data["content"]]
    return query_data.iloc[fits_criteria]
