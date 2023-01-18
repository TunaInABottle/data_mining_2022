import pandas as pd
from typing import Callable, Union
import statistics

def density(df:pd.DataFrame) -> Union[float, None]:
    if len(df) == 0 or len(df.columns) == 0:
        return None
    return 1 - statistics.mean(df.isna().sum()/(len(df)))

def below_cap(func_name: Callable[[pd.DataFrame], float], f_val: float) -> bool:
    if(" density " in str(func_name)):
        return f_val < 1
    raise Exception("Unexpected function name: " + str(func_name))