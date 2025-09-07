
import jpype
import numpy as np
from line_solver import jlineMatrixToArray, jlineMatrixFromArray


def lsn_max_multiplicity(lsn):
    result = jpype.JPackage('jline').api.lsn.LsnMaxMultiplicityKt.lsnMaxMultiplicity(lsn)
    return jlineMatrixToArray(result)