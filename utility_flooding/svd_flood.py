import pandas as pd
from typing import List, Tuple, Dict, Callable, NewType, Optional
from eval_func import density, below_cap
from random import randrange
from fill_data import collaborative_filtering

Query = NewType('Query', Dict[str, Optional[str]])

def elementwise_or(list1: List[bool], list2: List[bool]) -> List[bool]:
    """Elementwise or of two lists of booleans

    :param list1: first list of booleans
    :param list2: second list of booleans
    :returns: list of booleans

    """
    return [list1[i] or list2[i] for i in range(len(list1))]

###########

def controlled_flooding(utility_matrix: pd.DataFrame, asked_queries: pd.DataFrame, query_combinations: pd.DataFrame):
    """@TODO"""
    new_matrix = utility_matrix.copy()
    while density(new_matrix) != 1:
        print(f"New iteration... current density = {density(new_matrix)}")
        queries_to_fill = pick_best_query_set(new_matrix, asked_queries, query_combinations)
        query_ids = select_queries_subset(queries_to_fill, asked_queries)["id"]

        new_matrix[query_ids] = collaborative_filtering(new_matrix[query_ids])
        #print(new_matrix[query_ids])
    return new_matrix.apply(pd.to_numeric, downcast='integer', errors='ignore')

##############################

def query_dict(query_string:str, query_id:str) -> Query:
    """change a query written as string to a dictionary

    :param query_string: the query written as "key1=value1 AND key2=value2 AND ..."
    :param query_id: the query id
    :returns: a dict with the query id and the query string as key value pairs

    """
    pairs = [x.split("=") for x in query_string.split(" AND ")]
    pairs_dict = dict(pairs)
    #pairs_dict["id"] = query_id
    return pairs_dict

# def get_query_dict(asked_queries:pd.DataFrame) -> List[dict]:
#     """@TODO
#     """
#     return [query_dict(asked_queries.iloc[i]["content"], asked_queries.iloc[i]["id"]) for i in range(len(asked_queries))]



def pick_best_query_set(utility_matrix: pd.DataFrame, asked_queries: pd.DataFrame, query_combinations: pd.DataFrame, candidate = {}, min_cols = 3, func: Callable[[pd.DataFrame], Optional[float]] = density) -> List[Query]:
    """Pick the best set of queries based on a metric of choice

    :param utility_matrix: the utility matrix
    :param asked_queries: full description of the queries
    :param query_combinations: a table containing all keys and values a query can have
    :param candidate: the current best query
    :param min_cols: the minimum number of columns to return (default 3)
    :param func: the function to evaluate the subset of queries
    :returns: the best subset of queries that maximises 'eval_func' and has at least 'min_cols' columns in the utility matrix
    """
    blacklist: List[Query] = []
    subset_maximiser: List[Query] = []
    query_parent: Query = {}

    cap: bool = True #removes cap of func


    # add a query set as long as a minimum of column is picked and the result have a value for each query
    while len(select_queries_subset(subset_maximiser, asked_queries)["id"]) < min_cols or empty_row_in_subset(utility_matrix, asked_queries, subset_maximiser): 
        # greedily add key/values to the dict that maximise eval_func
        query_optimum, query_parent = greedy_pick_query_subset(utility_matrix, query_parent, asked_queries, query_combinations, blacklist, func, cap)

        subset_maximiser.append(query_optimum)
        blacklist.append(query_optimum)

        # pick a dense brother in the next iteration if no non-dense brother is available
        if query_optimum == query_parent:
            print("removing cap")
            cap = False
            continue
        # go back in the tree if there is no available brother
        if query_optimum == query_parent and not cap:
            print("going to the parent, re-adding cap")
            query_parent = get_a_grandparent(query_parent)
            cap = True
        if query_parent == {}:
            break


    print(f"picking best subset: {subset_maximiser}")
    return(subset_maximiser)

def get_a_grandparent(query_dict: Query) -> Query:
    """Remove a key or value from the query

    Prioritize removal of null keys

    :param query_dict: a representation of the query
    :returns: a query with one less element
    """
    empty_keys: List[str] = [key for key, value in query_dict.items() if value is None]
    if len(empty_keys) > 0:
        # @TODO assumes that there's only one empty value
        query_dict.pop(empty_keys[-1])
        return query_dict

    rnd_n: int = randrange(0, len(query_dict)-1)
    query_dict.pop(list(query_dict.keys())[rnd_n])
    return query_dict

def empty_row_in_subset(utility_matrix: pd.DataFrame, asked_queries: pd.DataFrame, queries: List[Query]) -> bool:
    tested_subset: pd.DataFrame = utility_matrix[select_queries_subset(queries, asked_queries)["id"]]
    if tested_subset.empty:
        return True
    #print(tested_subset)
    return max(nan_per_row(tested_subset)) == len(tested_subset.columns)

def nan_per_row(df: pd.DataFrame) -> List[int]:
    """@TODO"""
    return df.isnull().sum(axis=1).tolist()

def greedy_pick_query_subset(utility_matrix: pd.DataFrame, start_query: Query, asked_queries: pd.DataFrame, query_combinations: pd.DataFrame, blacklist: List[Query], func: Callable[[pd.DataFrame], Optional[float]], cap: bool = True) -> Query:
    """greedily select the query subset that maximises the eval_func
    
    :param utility_matrix: the utility matrix
    :param start_query: the query to start with
    :param asked_queries: full description of the queries
    :param query_combinations: a table containing all keys and values a query can have
    :param blacklist: list of queries that should not be considered
    :param func: the function used to evaluate the subset of queries
    :cap @TODO
    :returns: the best query that maximises 'eval_func'
    """
    child: Tuple[Query, float] = [{}, 0.0]
    parent: Tuple[Query, float] = [{}, 0.0]
    if start_query != {}:
        parent = [ start_query, calc_queries_set_value(utility_matrix, asked_queries, start_query, eval_func = func)]
    else:
        parent = add_best_query_key({}, utility_matrix, asked_queries, query_combinations, blacklist, func)

    trace: Tuple[Query, float] = parent
    
    while parent[0] != child[0]:
        parent = child
        candidate_by_val = add_best_query_value(parent[0], utility_matrix, asked_queries, query_combinations, blacklist, func, cap)
        # prioritize adding a value
        if (candidate_by_val[1] is not None and candidate_by_val[1] > parent[1]):
            child = candidate_by_val
            trace = parent
            continue
        candidate_by_key = add_best_query_key(parent[0], utility_matrix, asked_queries, query_combinations, blacklist, func, cap)
        if (candidate_by_key[1] > parent[1]):
            child = candidate_by_key
            trace = parent

    print(f"child: {child} - trace: {trace}")
    
    return child[0], trace[0]

def add_best_query_value(candidate: Query, utility_matrix: pd.DataFrame, asked_queries: pd.DataFrame, query_combinations: pd.DataFrame, blacklist: List[Query], eval_func: Callable[[pd.DataFrame], Optional[float]] = density, cap: bool = True) -> Tuple[Query, float]:
    """Adds to candidate the value to any empty key that maximises 'eval_func'

    :param candidate: a query to which is desired to add a value
    :param utility_matrix: the utility matrix
    :param asked_queries: full description of the queries
    :param query_combinations: a table containing all keys and values a query can have
    :param blacklist: list of queries that should not be considered
    :param eval_func: the function used to evaluate the subset of queries
    :returns: the best query that maximises 'eval_func' and the value of 'eval_func' for that query when a new value is defined
    """
    # define the starting value of the candidate
    starting_value: float = calc_queries_set_value(utility_matrix, asked_queries, candidate, eval_func = eval_func)
    new_candidate: Tuple[Query, float] = [candidate, starting_value]

    # find all keys that have None value
    empty_keys: List[str] = [key for key, value in candidate.items() if value is None]
    
    for key in empty_keys:
        all_values = query_combinations[key]
        for value in all_values:
            new_query_dict: Query = candidate.copy()
            new_query_dict[key] = value
            query_set_value:float = calc_queries_set_value(utility_matrix, asked_queries, new_query_dict, eval_func = eval_func)
            if query_set_value is not None and query_set_value > new_candidate[1] and new_query_dict not in blacklist:
                # assign new candidate only if it not reach the cap
                if cap and below_cap(eval_func, query_set_value):
                        new_candidate = [new_query_dict, query_set_value]
                elif not cap:
                    new_candidate = [new_query_dict, query_set_value]
    return(new_candidate)

def add_best_query_key(candidate: Query, utility_matrix: pd.DataFrame, asked_queries: pd.DataFrame, query_combinations: pd.DataFrame, blacklist: List[Query], eval_func: Callable[[pd.DataFrame], Optional[float]] = density, cap: bool = True) -> Tuple[Query, float]:
    """Adds to candidate the key that maximises 'eval_func'

    :param candidate: a query to which is desired to add a key
    :param utility_matrix: the utility matrix
    :param asked_queries: full description of the queries
    :param query_combinations: a table containing all keys and values a query can have
    :param blacklist: list of queries that should not be considered
    :param eval_func: the function used to evaluate the subset of queries
    :returns: the best query that maximises 'eval_func' and the value of 'eval_func' for that query when a new key is added
    """
    # define the starting value of the candidate
    starting_value: float = calc_queries_set_value(utility_matrix, asked_queries, candidate, eval_func = eval_func)
    new_candidate: Tuple[Query, float] = [candidate, starting_value]

    # remove the already selected queries
    unused_query_keys: List[str] = query_combinations.drop(columns = list(candidate.keys())).columns

    # iterate existing non-chosen keys
    for query_key in unused_query_keys:
        new_query_dict: Query = candidate.copy()
        new_query_dict[query_key] = None
        query_set_value:float = calc_queries_set_value(utility_matrix, asked_queries, new_query_dict, eval_func = eval_func)
        if query_set_value is not None and query_set_value > new_candidate[1] and new_query_dict not in blacklist:
            # assign new candidate only if it not reach the cap
            if cap and below_cap(eval_func, query_set_value):
                    new_candidate = [new_query_dict, query_set_value]
            elif not cap:
                new_candidate = [new_query_dict, query_set_value]
    return(new_candidate)

def calc_queries_set_value(utility_matrix: pd.DataFrame, asked_queries: pd.DataFrame, query_subset: Query, eval_func: Callable[[pd.DataFrame], Optional[float]] = density) -> float:
    """Calculate the specified metric over a specified subset of queries

    :param utility_matrix: the utility matrix from which calculate the function
    :param asked_queries: full description of the queries
    :param query_subset: the elements over which filter
    :param eval_func: the function to evaluate the subset of queries
    :returns: the density of the subset of columns, 0 if 'query_subset' is empty
    """
    if query_subset == {}:
        return 0

    filtered_queries_ids = select_queries_subset([query_subset], asked_queries)["id"]
    return eval_func(utility_matrix[filtered_queries_ids])

def select_queries_subset(queries_list: List[Query], asked_queries: pd.DataFrame) -> pd.DataFrame:
    """Subsets a dataframe based on a list of queries

    :param queries_list: list from which you want to make a subset
    :param asked_queries: full description of the queries
    :returns the filtered query dataset
    """
    fits_criteria: List[bool] = [False] * len(asked_queries)

    for query_dict in queries_list:
        # write the query as a string, None value is replaced by an empty string
        query_elms = [f"{pair[0]}={pair[1] if pair[1] is not None else str()}" for pair in list(query_dict.items())]

        # check if the query is in the asked queries, adds it to the fits criteria
        fits_criteria = elementwise_or(fits_criteria, [all(elm in query for elm in query_elms ) for query in asked_queries["content"]])
    return asked_queries.iloc[fits_criteria]