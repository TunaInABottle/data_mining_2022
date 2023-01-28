import pandas as pd 
import numpy as np
import math
import random
import statistics
from svd_flood import controlled_flooding


#Two Methods 
#Method1: Randomly erasing 0.2 of non nan values to create train, test sets
def Masked_df (df, test_ratio=0.2):
  """
  Calculate the number of values that will be masked (n)
  Mask n non "nan" values, (the masking operation will turn them into "nan")
  :returns: new_df: masked dataframe with a ratio of 0.2*density(dataframe)
            l: list of the masked values 
  """

  n=len(df) - statistics.mean(df.isna().sum())
  n=min(max(int(n*test_ratio), 1), len(df))
  #print(n)

  new_df=df.copy()
  new_df=new_df.drop('user_id', axis=1)
  k=df.isna().sum().to_dict()
  new_df=np.array(new_df)

  l=[]
  for _ in range(n):
    a=True
    while a:
      i = random.randint(0, new_df.shape[0]-1)
      j = random.randint(0, new_df.shape[1]-1)
      if ( not(math.isnan(new_df[i,j])) ) and ( k[list(df.columns)[j+1]] < df.shape[0]-1 ) :
        l.append([new_df[i,j],i,j])
        new_df[i,j]=np.nan
        k[list(df.columns)[3]]-=1
        a=False

  new_df=pd.DataFrame(new_df)
  new_df.insert(0, 'user_id', df['user_id'])
  a=dict({i-1:df.columns[i] for i in range(1,len(df.columns))})
  new_df.rename(a, axis=1, inplace=True)

  return(new_df, l)


def test_err (utility_matrix, asked_queries, query_combinations, masked_matrix, L):
  #Root-mean-square error
  filled_masked_utility= controlled_flooding(masked_matrix, asked_queries, query_combinations)
  
  filled_masked_utility=np.array(filled_masked_utility.drop('user_id', axis=1))

  s=0
  for i in L:
    s+= (i[0] - filled_masked_utility[i[1], i[2]])**2
  
  return( math.sqrt(s/len(L)) )


def mult_test (utility_matrix, asked_queries, query_combinations, mult=10, test_ratio=[0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]):
  """
  :param n_folds: Number of different selections of testing samples over which 
                  the process of testing will be repeated (default 3)
  :param n_folds: a list of test_ratio for each train/test split (defaut 0.2 for all iterations)
  """
  s=0
  for i in range(mult):
    masked_matrix, L= Masked_df (utility_matrix, test_ratio[i])
    s+= test_err (utility_matrix, asked_queries, query_combinations, masked_matrix, L)
  
  return (s/mult)



#Method2: split the data into (n_folds) folds and train the algorithm on (n_folds)-1 folds, and test it on the remaining one, n_folds times
def create_folds (utility_matrix, n, n_folds):
  """ Create X_train, X_test
      :param utility_matrix: the utility matrix
      :param n: number of the iteration (the execution of the hole algorithm of the train/test)
      :param n_folds: number of folds
      :returns new_df: X_train
      :returns l: list of the values, and their indexes, left for X_test
  """
  new_df=utility_matrix.copy()
  new_df.drop(columns='user_id', inplace=True)
  l=[]
  for i in range (len(utility_matrix)//n_folds) :
    for j in range (len(utility_matrix.columns)//n_folds):
      j=j+n*n_folds 
      for k in range (n_folds):
        u=(i+k*n_folds) % len(utility_matrix)
        v=(j+k*n_folds) % len(utility_matrix.columns)
        #df[list(df.columns)[1]][0]
        if not(pd.isna(new_df.iat[u, v])):
          l.append([new_df.loc[u, list(utility_matrix.columns)[v]], u, v])
          new_df.loc[u, list(utility_matrix.columns)[v]] = pd.np.nan

  new_df.insert(0, 'user_id', utility_matrix['user_id'])
  return(new_df, l)


def cross_validation(utility_matrix, asked_queries, query_combinations, n_folds):
  """ Evaluate the model using cross validation
      :param utility_matrix: the utility matrix
      :param asked_queries: full description of the queries
      :param query_combinations: a table containing all keys and values a query can have
      :param n_folds: number of folds
      :returns: the computed error 
  """  
  s=0
  for i in range (n_folds):
    # Split the data into training and test sets
    new_df, l= create_folds (utility_matrix, i, n_folds)
    # Add the error of iteration i
    s+= test_err (utility_matrix, asked_queries, query_combinations, new_df, l)
  return(s/n_folds)
    