import pandas as pd
from typing import List, Tuple, Dict, Callable
import statistics
from eval_func import density, below_cap

def or_elementwise(list1: List[bool], list2: List[bool]) -> List[bool]:
    """Elementwise or of two lists of booleans

    :param list1: first list of booleans
    :param list2: second list of booleans
    :returns: list of booleans

    """
    return [list1[i] or list2[i] for i in range(len(list1))]

def query_dict(query_string:str, query_id:str) -> dict:
    """change a query written as string to a dictionary

    :param query_string: the query written as "key1=value1 AND key2=value2 AND ..."
    :param query_id: the query id
    :returns: a dict with the query id and the query string as key value pairs

    """
    pairs = [x.split("=") for x in query_string.split(" AND ")]
    pairs_dict = dict(pairs)
    pairs_dict["id"] = query_id
    return pairs_dict

def get_query_dict(asked_queries:pd.DataFrame) -> List[dict]:
    """@TODO
    """
    return [query_dict(asked_queries.iloc[i]["content"], asked_queries.iloc[i]["id"]) for i in range(len(asked_queries))]



def pick_best_query_set(utility_matrix: pd.DataFrame, asked_queries: pd.DataFrame, query_combinations: pd.DataFrame, candidate = {}, min_cols = 3, func: Callable[[pd.DataFrame], "pd.Series[float]"] = density) -> List[dict]:
    """Pick the best set of queries based on a metric of choice

    :param utility_matrix: the utility matrix from which calculate the density
    :param asked_queries: full description of the queries
    :param query_combinations: a table containing all keys and values a query can have
    :param candidate: the current best key and its density
    :param func: the function to evaluate the subset of queries
    :returns: the best subset of queries that maximises 'eval_func'
    """
    blacklist: List[Dict[str, str]] = []
    subset_maximiser: List[Dict[str, str]] = []

    while len(select_queries_subset(subset_maximiser, asked_queries)["id"]) < min_cols:
        # greedily add key/values to the dict that maximise eval_func
        new_candidate = greedy_best_query_subset(utility_matrix, asked_queries, query_combinations, blacklist, func)
        subset_maximiser.append(new_candidate)
        blacklist.append(new_candidate)

    print(f"picking best: {subset_maximiser}")
    return(subset_maximiser)

def greedy_best_query_subset(utility_matrix: pd.DataFrame, asked_queries: pd.DataFrame, query_combinations: pd.DataFrame, blacklist: List[Dict[str, str]], func: Callable[[pd.DataFrame], "pd.Series[float]"]) -> Dict[str, str]:
    """@TODO
    """
    parent = add_best_query_key({}, utility_matrix, asked_queries, query_combinations, blacklist, func)

    trace = parent
    child = [{}, 0]
    
    while parent[0] != child[0]:
        parent = child
        candidate_by_val = add_best_query_value(parent[0], utility_matrix, asked_queries, query_combinations, blacklist, func)
        # prioritize adding a value
        if (candidate_by_val[1] > parent[1]):
            child = candidate_by_val
            trace = parent
            continue
        candidate_by_key = add_best_query_key(parent[0], utility_matrix, asked_queries, query_combinations, blacklist, func)
        if (candidate_by_key[1] > parent[1]):
            child = candidate_by_key
            trace = parent

    print(f"trace: {trace}")
    print(f"child: {child}")
    
    return child[0]

def add_best_query_value(candidate: dict, utility_matrix: pd.DataFrame, asked_queries: pd.DataFrame, query_combinations: pd.DataFrame, blacklist: List[Dict[str, str]], eval_func: Callable[[pd.DataFrame], "pd.Series[float]"] = density):
    """@TODO
    """
    # define the starting value of the candidate
    starting_value: float = calc_queries_set_value(utility_matrix, asked_queries, candidate, eval_func = eval_func)
    new_candidate: Tuple[dict, float] = [candidate, starting_value]

    # find all keys that have None value
    empty_keys = [key for key, value in candidate.items() if value is None]
    
    for key in empty_keys:
        all_values = query_combinations[key]
        for value in all_values:
            new_query_dict: dict = candidate.copy()
            new_query_dict[key] = value
            query_set_value:float = calc_queries_set_value(utility_matrix, asked_queries, new_query_dict, eval_func = eval_func)
            if query_set_value is not None and query_set_value > new_candidate[1] and below_cap(eval_func, query_set_value) and new_query_dict not in blacklist:
                # proclaim it as the new best
                new_candidate = [new_query_dict, query_set_value]
    return(new_candidate)

def add_best_query_key(candidate: dict, utility_matrix: pd.DataFrame, asked_queries: pd.DataFrame, query_combinations: pd.DataFrame, blacklist: List[Dict], eval_func: Callable[[pd.DataFrame], "pd.Series[float]"] = density):
    """Add the best query key to the current candidate
    @TODO add blacklist

    :param utility_matrix: the utility matrix from which calculate the density
    :param asked_queries: full description of the queries
    :param query_combinations: a table containing all keys and values a query can have
    :param candidate: the current best key and its density
    :param eval_func: the function to evaluate the subset of queries
    :returns: the best key and its density
    """
    # define the starting value of the candidate
    starting_value: float = calc_queries_set_value(utility_matrix, asked_queries, candidate, eval_func = eval_func)
    new_candidate: Tuple[dict, float] = [candidate, starting_value]

    # remove the already selected queries
    unused_query_keys: List[str] = query_combinations.drop(columns = list(candidate.keys())).columns

    # iterate existing non-chosen keys
    for query_key in unused_query_keys:
        new_query_dict: dict = candidate.copy()
        new_query_dict[query_key] = None
        query_set_value:float = calc_queries_set_value(utility_matrix, asked_queries, new_query_dict, eval_func = eval_func)
        if query_set_value is not None and query_set_value > new_candidate[1] and below_cap(eval_func, query_set_value) and new_query_dict not in blacklist:
            # proclaim it as the new best
            new_candidate = [new_query_dict, query_set_value]
    return(new_candidate)

def calc_queries_set_value(utility_matrix: pd.DataFrame, asked_queries: pd.DataFrame, query_subset: List[str], eval_func: Callable[[pd.DataFrame], "pd.Series[float]"] = density) -> float:
    """Calculate the specified metric over a specified subset of queries

    :param utility_matrix: the utility matrix from which calculate the function
    :param asked_queries: a table containing all keys and values a query can have
    :param col_names: the elements over which filter
    :param eval_func: the function to evaluate the subset of queries
    :returns: the density of the subset of columns
    """
    if query_subset == {}:
        return 0

    filtered_queries_ids = select_queries_subset([query_subset], asked_queries)["id"]
    return eval_func(utility_matrix[filtered_queries_ids])

def select_queries_subset(queries_list: List[Dict[str, str]], asked_queries: pd.DataFrame):
    """Makes a subset of the queries that match 'query_dict'

    :param queries_list: @TODO #which elements are going to be filtered
    :param query_data: the query dataset
    :returns the filtered query dataset
    """
    fits_criteria = [False] * len(asked_queries)

    for query_dict in queries_list:
        # write the query as a string, None value is replaced by an empty string
        query_elms = [f"{pair[0]}={pair[1] if pair[1] is not None else str()}" for pair in list(query_dict.items())]

        # check if the query is in the asked queries, adds it to the fits criteria
        fits_criteria = or_elementwise(fits_criteria, [all(elm in query for elm in query_elms ) for query in asked_queries["content"]])
    return asked_queries.iloc[fits_criteria]