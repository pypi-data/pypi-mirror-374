
import pandas as pd
import jpype
import numpy as np
from . import jlineMatrixToArray

def tget(df, *args):
    if not args:
        return df

    mask = pd.Series([True] * len(df), index=df.index)

    columns = df.columns.tolist()

    default_columns = ['Station', 'JobClass']

    for arg in args:
        if hasattr(arg, 'getName'):
            arg_value = str(arg.getName())
        else:
            arg_value = str(arg)

        if arg_value in df.columns:
            columns = default_columns + [arg_value]
        else:
            mask = mask & df.apply(lambda row: row.astype(str).str.contains(arg_value).any(), axis=1)

    return df.loc[mask, columns].drop_duplicates()


def circul(c):
    from . import jlineMatrixFromArray

    if isinstance(c, (int, float)):
        result = jpype.JPackage('jline').util.Maths.circul(int(c))
    else:
        c_matrix = jlineMatrixFromArray(c)
        result = jpype.JPackage('jline').util.Maths.circul(c_matrix)

    return jlineMatrixToArray(result)
