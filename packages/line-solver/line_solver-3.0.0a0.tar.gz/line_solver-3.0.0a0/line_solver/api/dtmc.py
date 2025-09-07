
import jpype
import numpy as np
from line_solver import jlineMatrixToArray, jlineMatrixFromArray


def dtmc_solve(matrix):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mc.Dtmc_solveKt.dtmc_solve(
            jlineMatrixFromArray(matrix)
        )
    )


def dtmc_stochcomp(matrix, indexes):
    ind = jpype.java.util.ArrayList()
    for i in range(len(indexes)):
        ind.add(jpype.JInt(indexes[i]))

    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mc.Dtmc_stochcompKt.dtmc_stochcomp(
            jlineMatrixFromArray(matrix), ind
        )
    )


def dtmc_timereverse(matrix):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mc.Dtmc_timereverseKt.dtmc_timereverse(
            jlineMatrixFromArray(matrix)
        )
    )


def dtmc_makestochastic(matrix):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mc.Dtmc_makestochasticKt.dtmc_makestochastic(
            jlineMatrixFromArray(matrix)
        )
    )


def dtmc_rand(length):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mc.Dtmc_randKt.dtmc_rand(jpype.JInt(length))
    )


def dtmc_simulate(P, pi0, n):
    result = jpype.JPackage('jline').api.mc.Dtmc_simulateKt.dtmc_simulate(
        jlineMatrixFromArray(P),
        jlineMatrixFromArray(pi0),
        jpype.JInt(n)
    )
    return np.array([result[i] for i in range(len(result))])


def dtmc_isfeasible(P):
    return jpype.JPackage('jline').api.mc.Dtmc_isfeasibleKt.dtmc_isfeasible(
        jlineMatrixFromArray(P)
    )