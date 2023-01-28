import pandas as pd 
import numpy as np
from svd_flood import controlled_flooding

def query_utility(utility_matrix, asked_queries, query_combinations):
  """ Evaluate the utility of the queries using Standard Deviation 
  :param utility_matrix: the utility matrix
  :param asked_queries: full description of the queries
  :param query_combinations: a table containing all keys and values a query can have
  :returns filled_utility: filled matrix, and the last row represents the utility of each query
  :returns L: list of queries' utility
  """

  filled_utility= controlled_flooding(utility_matrix, asked_queries, query_combinations)
  new_df= filled_utility - filled_utility.mean()
  L=['SD:']
  for j in range (1, len(filled_utility.columns)):
    s=0
    for i in range (len(filled_utility)):
      s += new_df.loc[i, list(new_df.columns)[j]] **2
    L.append ( s/len(filled_utility) )

  filled_utility.iloc[len(filled_utility)] = L

  return(filled_utility, L)