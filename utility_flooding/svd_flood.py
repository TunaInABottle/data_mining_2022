import pandas as pd
from typing import List, Tuple
import statistics

def density(df:pd.DataFrame) -> "pd.Series[float]":
    if len(df) == 0:
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



def pick_best_query_set(utility_matrix: pd.DataFrame, queries: pd.DataFrame, possible_query_cont: pd.DataFrame, candidate = ["", 0], eval_func = density):
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
    candidate = pick_best_by_query_key(utility_matrix, queries, possible_query_cont, candidate, eval_func)

    print(candidate)
    return(candidate[0])

def pick_best_by_query_key(utility_matrix: pd.DataFrame, queries: pd.DataFrame, possible_query_cont: pd.DataFrame, candidate: Tuple[dict, float], eval_func = density):
    """@TODO verify and finish this description

    :param utility_matrix: the utility matrix from which calculate the density
    :param queries: full description of the queries
    :param possible_query_cont: a table containing all keys and values a query can have
    :param candidate: the current best key and its density
    :param eval_func: the function to evaluate the subset of queries
    :returns: the best key and its density
    """
    # @TODO needed for string to dict conversion
    # remove the already selected queries
    #unused_query_keys = possible_query_cont.drop(columns = candidate[0].keys()).columns

    new_candidate: Tuple[dict, float] = candidate

    # iterate query keys
    for query_key in possible_query_cont.columns:
        query_set_value = calculate_queries_set_value(utility_matrix, queries, query_key, eval_func = eval_func)
        if query_set_value > new_candidate[1]:
            #new_query_set = candidate[0].copy()
            #new_query_set[query_key] = possible_query_cont[query_key]
            #new_candidate = [new_query_set, query_set_value]
            new_candidate = [query_key, query_set_value]
    return(new_candidate)


def calculate_queries_set_value(utility_matrix: pd.DataFrame, queries: pd.DataFrame, col_names: List[str], eval_func = density) -> float:
    """Calculate the specified metric over a specified subset of queries

    :param utility_matrix: the utility matrix from which calculate the function
    :param queries: a table containing all keys and values a query can have
    :param col_names: the elements over which filter
    :param eval_func: the function to evaluate the subset of queries
    :returns: the density of the subset of columns
    """
    filtered_queries_ids = queries.iloc[[col_names in q for q in queries["content"]]]["id"]
    return eval_func(utility_matrix[filtered_queries_ids])

def get_query_values(queries: pd.DataFrame, query_key: str) -> List[str]:
    """Get the values of a query

    :param queries: a table containing all keys and values a query can have
    :param query_keys: the name of the query key
    :returns: the values of the query for a specified key
    """
    return queries[query_key].values()


# remove None values from list
# list(filter(lambda item: item is not None, test_list))