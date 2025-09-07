
import jpype
import numpy as np
from .. import jlineMatrixToArray, jlineMatrixFromArray


def ctmc_makeinfgen(birth_rates, death_rates, max_states=None):
    birth_rates = np.array(birth_rates)
    death_rates = np.array(death_rates)

    if max_states is None:
        max_states = max(len(birth_rates), len(death_rates))

    if len(birth_rates) < max_states:
        birth_rates = np.pad(birth_rates, (0, max_states - len(birth_rates)), 'constant')
    if len(death_rates) < max_states:
        death_rates = np.pad(death_rates, (0, max_states - len(death_rates)), 'constant')

    Q = np.zeros((max_states, max_states))

    for i in range(max_states):
        if i < max_states - 1 and birth_rates[i] > 0:
            Q[i, i+1] = birth_rates[i]

        if i > 0 and death_rates[i] > 0:
            Q[i, i-1] = death_rates[i]

        Q[i, i] = -np.sum(Q[i, :])

    return Q


def ctmc_solve(Q):
    Q = np.array(Q)
    n = Q.shape[0]

    java_Q = jlineMatrixFromArray(Q)
    java_result = jpype.JPackage('jline').api.mc.Ctmc_solveKt.ctmc_solve(java_Q)

    return jlineMatrixToArray(java_result).flatten()


def ctmc_transient(Q, initial_dist, time_points):
    Q = np.array(Q)
    initial_dist = np.array(initial_dist)
    time_points = np.array(time_points)

    java_Q = jlineMatrixFromArray(Q)
    java_initial = jlineMatrixFromArray(initial_dist.reshape(1, -1))
    java_times = jpype.JArray(jpype.JDouble)(time_points)

    java_result = jpype.JPackage('jline').api.mc.Ctmc_transientKt.ctmc_transient(
        java_Q, java_initial, java_times
    )

    return jlineMatrixToArray(java_result)


def ctmc_simulate(Q, initial_state, max_time, max_events=10000):
    Q = np.array(Q)

    java_Q = jlineMatrixFromArray(Q)
    java_result = jpype.JPackage('jline').api.mc.Ctmc_simulateKt.ctmc_simulate(
        java_Q,
        jpype.JInt(initial_state),
        jpype.JDouble(max_time),
        jpype.JInt(max_events)
    )

    return {
        'states': np.array(java_result.getStates()),
        'times': np.array(java_result.getTimes()),
        'sojourn_times': np.array(java_result.getSojournTimes())
    }


def ctmc_randomization(Q, initial_dist, time_points, precision=1e-10):
    Q = np.array(Q)
    initial_dist = np.array(initial_dist)
    time_points = np.array(time_points)

    java_Q = jlineMatrixFromArray(Q)
    java_initial = jlineMatrixFromArray(initial_dist.reshape(1, -1))
    java_times = jpype.JArray(jpype.JDouble)(time_points)

    java_result = jpype.JPackage('jline').api.mc.Ctmc_randomizationKt.ctmc_randomization(
        java_Q, java_initial, java_times, jpype.JDouble(precision)
    )

    return jlineMatrixToArray(java_result)


def ctmc_uniformization(Q, lambda_rate=None):
    Q = np.array(Q)

    if lambda_rate is None:
        lambda_rate = -np.min(np.diag(Q))

    n = Q.shape[0]
    I = np.eye(n)
    P = I + Q / lambda_rate

    return {
        'P': P,
        'lambda': lambda_rate
    }


def ctmc_stochcomp(Q, keep_states, eliminate_states):
    Q = np.array(Q)
    keep_states = np.array(keep_states, dtype=int)
    eliminate_states = np.array(eliminate_states, dtype=int)

    java_Q = jlineMatrixFromArray(Q)
    java_keep = jpype.JArray(jpype.JInt)(keep_states)
    java_eliminate = jpype.JArray(jpype.JInt)(eliminate_states)

    java_result = jpype.JPackage('jline').api.mc.Ctmc_stochcompKt.ctmc_stochcomp(
        java_Q, java_keep, java_eliminate
    )

    return jlineMatrixToArray(java_result)


def ctmc_timereverse(Q, pi=None):
    Q = np.array(Q)

    if pi is None:
        pi = ctmc_solve(Q)
    else:
        pi = np.array(pi)

    java_Q = jlineMatrixFromArray(Q)
    java_pi = jlineMatrixFromArray(pi.reshape(1, -1))

    java_result = jpype.JPackage('jline').api.mc.Ctmc_timereverseKt.ctmc_timereverse(
        java_Q, java_pi
    )

    return jlineMatrixToArray(java_result)


def ctmc_rand(n, density=0.3, max_rate=10.0):
    java_result = jpype.JPackage('jline').api.mc.Ctmc_randKt.ctmc_rand(
        jpype.JInt(n),
        jpype.JDouble(density),
        jpype.JDouble(max_rate)
    )

    return jlineMatrixToArray(java_result)



def dtmc_solve(P):
    P = np.array(P)

    java_P = jlineMatrixFromArray(P)
    java_result = jpype.JPackage('jline').api.mc.Dtmc_solveKt.dtmc_solve(java_P)

    return jlineMatrixToArray(java_result).flatten()


def dtmc_makestochastic(A):
    A = np.array(A, dtype=float)

    row_sums = np.sum(A, axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1

    return A / row_sums


def dtmc_isfeasible(P, tolerance=1e-10):
    P = np.array(P)

    if np.any(P < 0):
        return False

    row_sums = np.sum(P, axis=1)
    if np.any(np.abs(row_sums - 1.0) > tolerance):
        return False

    return True


def dtmc_simulate(P, initial_state, num_steps):
    P = np.array(P)

    java_P = jlineMatrixFromArray(P)
    java_result = jpype.JPackage('jline').api.mc.Dtmc_simulateKt.dtmc_simulate(
        java_P,
        jpype.JInt(initial_state),
        jpype.JInt(num_steps)
    )

    return np.array(java_result)


def dtmc_rand(n, density=0.5):
    java_result = jpype.JPackage('jline').api.mc.Dtmc_randKt.dtmc_rand(
        jpype.JInt(n),
        jpype.JDouble(density)
    )

    return jlineMatrixToArray(java_result)


def dtmc_stochcomp(P, keep_states, eliminate_states):
    P = np.array(P)
    keep_states = np.array(keep_states, dtype=int)
    eliminate_states = np.array(eliminate_states, dtype=int)

    java_P = jlineMatrixFromArray(P)
    java_keep = jpype.JArray(jpype.JInt)(keep_states)
    java_eliminate = jpype.JArray(jpype.JInt)(eliminate_states)

    java_result = jpype.JPackage('jline').api.mc.Dtmc_stochcompKt.dtmc_stochcomp(
        java_P, java_keep, java_eliminate
    )

    return jlineMatrixToArray(java_result)


def dtmc_timereverse(P, pi=None):
    P = np.array(P)

    if pi is None:
        pi = dtmc_solve(P)
    else:
        pi = np.array(pi)

    java_P = jlineMatrixFromArray(P)
    java_pi = jlineMatrixFromArray(pi.reshape(1, -1))

    java_result = jpype.JPackage('jline').api.mc.Dtmc_timereverseKt.dtmc_timereverse(
        java_P, java_pi
    )

    return jlineMatrixToArray(java_result)