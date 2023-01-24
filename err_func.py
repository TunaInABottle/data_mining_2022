import pandas as pd 
import numpy as np
import math
import random
import statistics
from svd_flood import controlled_flooding


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
  new_df=np.array(new_df)

  l=[]
  for _ in range(n):
    a=True
    while a:
      i = random.randint(0, new_df.shape[0]-1)
      j = random.randint(0, new_df.shape[1]-1)
      if not(math.isnan(new_df[i,j])):
        l.append([new_df[i,j],i,j])
        new_df[i,j]=np.nan
        a=False

  new_df=pd.DataFrame(new_df)
  new_df.insert(0, 'user_id', df['user_id'])
  a=dict({i-1:df.columns[i] for i in range(1,len(df.columns))})
  new_df.rename(a, axis=1, inplace=True)

  return(new_df, l)


def test_err (utility_matrix, asked_queries, query_combinations):
  #Root-mean-square error
  masked_matrix, L= Masked_df (utility_matrix)
  filled_masked_utility= controlled_flooding(masked_matrix, asked_queries, query_combinations)
  
  filled_masked_utility=np.array(filled_masked_utility.drop('user_id', axis=1))

  s=0
  for i in L:
    s+= (i[0] - filled_masked_utility[i[1], i[2]])**2
  
  return( math.sqrt(s/len(L)) )
