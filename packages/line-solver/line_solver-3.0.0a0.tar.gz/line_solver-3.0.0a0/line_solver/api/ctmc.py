
import jpype

from line_solver import jlineMatrixToArray, jlineMatrixFromArray


def ctmc_uniformization(pi0, Q, t):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mc.Ctmc_uniformizationKt.ctmc_uniformization(
            jlineMatrixFromArray(pi0),
            jlineMatrixFromArray(Q),
            jlineMatrixFromArray(t)
        )
    )


def ctmc_timereverse(matrix):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mc.Ctmc_timereverseKt.ctmc_timereverse(
            jlineMatrixFromArray(matrix)
        )
    )


def ctmc_makeinfgen(matrix):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mc.Ctmc_makeinfgenKt.ctmc_makeinfgen(
            jlineMatrixFromArray(matrix)
        )
    )


def ctmc_solve(matrix):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mc.Ctmc_solveKt.ctmc_solve(
            jlineMatrixFromArray(matrix)
        )
    )


def ctmc_transient(Q, pi0=None, t0=None, t1=None):
    Q_matrix = jlineMatrixFromArray(Q)

    if pi0 is not None and t0 is not None and t1 is not None:
        result = jpype.JPackage('jline').api.mc.Ctmc_transientKt.ctmc_transient(
            Q_matrix, jlineMatrixFromArray(pi0), t0, t1
        )
    elif pi0 is not None and t1 is not None:
        result = jpype.JPackage('jline').api.mc.Ctmc_transientKt.ctmc_transient(
            Q_matrix, jlineMatrixFromArray(pi0), t1
        )
    elif t1 is not None:
        result = jpype.JPackage('jline').api.mc.Ctmc_transientKt.ctmc_transient(
            Q_matrix, t1
        )
    else:
        raise ValueError("t1 (end time) must be provided")

    times = list(result.first)
    probabilities = [list(prob_array) for prob_array in result.second]

    return times, probabilities


def ctmc_simulate(Q, pi0=None, n=1000):
    Q_matrix = jlineMatrixFromArray(Q)

    if pi0 is not None:
        pi0_array = jpype.JArray(jpype.JDouble)(len(pi0))
        for i, val in enumerate(pi0):
            pi0_array[i] = float(val)
    else:
        pi0_array = None

    result = jpype.JPackage('jline').api.mc.Ctmc_simulateKt.ctmc_simulate(
        Q_matrix, pi0_array, jpype.JInt(n)
    )

    states = list(result.states)
    sojourn_times = list(result.sojournTimes)

    return states, sojourn_times


def ctmc_rand(length):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mc.Ctmc_randKt.ctmc_rand(jpype.JInt(length))
    )


def ctmc_ssg(sn, options):
    result = jpype.JPackage('jline').api.mc.Ctmc_ssgKt.ctmc_ssg(sn, options)

    return {
        'state_space': jlineMatrixToArray(result.stateSpace),
        'state_space_aggr': jlineMatrixToArray(result.stateSpaceAggr),
        'state_space_hashed': jlineMatrixToArray(result.stateSpaceHashed),
        'node_state_space': {node: jlineMatrixToArray(space)
                           for node, space in result.nodeStateSpace.items()},
        'sn': result.sn
    }


def ctmc_stochcomp(Q, I_list=None):
    Q_matrix = jlineMatrixFromArray(Q)

    if I_list is None:
        I_list = []

    java_list = jpype.java.util.ArrayList()
    for idx in I_list:
        java_list.add(jpype.JDouble(float(idx)) if idx is not None else None)

    result = jpype.JPackage('jline').api.mc.Ctmc_stochcompKt.ctmc_stochcomp(
        Q_matrix, java_list
    )

    return {
        'S': jlineMatrixToArray(result.S),
        'Q11': jlineMatrixToArray(result.Q11),
        'Q12': jlineMatrixToArray(result.Q12),
        'Q21': jlineMatrixToArray(result.Q21),
        'Q22': jlineMatrixToArray(result.Q22),
        'T': jlineMatrixToArray(result.T)
    }

def ctmc_ssg_reachability(sn, options=None):
    result = jpype.JPackage('jline').api.mc.Ctmc_ssg_reachabilityKt.ctmc_ssg_reachability(
        sn, options
    )

    node_state_space = {}
    if result.nodeStateSpace:
        for node_entry in result.nodeStateSpace.entrySet():
            node_key = node_entry.getKey()
            node_value = jlineMatrixToArray(node_entry.getValue())
            node_state_space[node_key] = node_value

    return {
        'state_space': jlineMatrixToArray(result.stateSpace),
        'state_space_aggr': jlineMatrixToArray(result.stateSpaceAggr),
        'state_space_hashed': jlineMatrixToArray(result.stateSpaceHashed),
        'node_state_space': node_state_space,
        'sn': result.sn
    }


def ctmc_randomization(Q, q=None):
    Q_matrix = jlineMatrixFromArray(Q)

    if q is not None:
        result = jpype.JPackage('jline').api.mc.Ctmc_randomizationKt.ctmc_randomization(
            Q_matrix, jpype.JDouble(q)
        )
    else:
        result = jpype.JPackage('jline').api.mc.Ctmc_randomizationKt.ctmc_randomization(
            Q_matrix, None
        )

    P_matrix = jlineMatrixToArray(result.getFirst())
    q_rate = result.getSecond()

    return P_matrix, q_rate


def ctmc_krylov(Q, pi0, t, options=None):
    Q_matrix = jlineMatrixFromArray(Q)
    pi0_matrix = jlineMatrixFromArray(pi0)

    if options is not None:
        result = jpype.JPackage('jline').api.mc.Ctmc_krylovKt.ctmc_krylov(
            Q_matrix, pi0_matrix, jpype.JDouble(t), jpype.JObject(options)
        )
    else:
        result = jpype.JPackage('jline').api.mc.Ctmc_krylovKt.ctmc_krylov(
            Q_matrix, pi0_matrix, jpype.JDouble(t)
        )

    return jlineMatrixToArray(result)

