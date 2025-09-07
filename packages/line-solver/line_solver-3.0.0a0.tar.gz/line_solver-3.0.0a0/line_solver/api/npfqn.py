
import jpype
from line_solver import jlineMatrixToArray, jlineMatrixFromArray


def npfqn_nonexp_approx(method, sn, ST, V, SCV, Tin, Uin, gamma, nservers):
    method_str = str(method)

    ret = jpype.JPackage('jline').api.npfqn.Npfqn_nonexp_approxKt.npfqn_nonexp_approx(
        method_str,
        sn,
        jlineMatrixFromArray(ST),
        jlineMatrixFromArray(V),
        jlineMatrixFromArray(SCV),
        jlineMatrixFromArray(Tin),
        jlineMatrixFromArray(Uin),
        jlineMatrixFromArray(gamma),
        jlineMatrixFromArray(nservers)
    )

    ST_new = jlineMatrixToArray(ret.get(0))
    gamma_new = jlineMatrixToArray(ret.get(1))
    nservers_new = jlineMatrixToArray(ret.get(2))
    rho = jlineMatrixToArray(ret.get(3))
    scva = jlineMatrixToArray(ret.get(4))
    scvs = jlineMatrixToArray(ret.get(5))
    eta = jlineMatrixToArray(ret.get(6))

    return [ST_new, gamma_new, nservers_new, rho, scva, scvs, eta]


def npfqn_traffic_merge(lambda_rates, scv_rates):
    result = jpype.JPackage('jline').api.npfqn.Npfqn_traffic_mergeKt.npfqn_traffic_merge(
        jlineMatrixFromArray(lambda_rates),
        jlineMatrixFromArray(scv_rates)
    )

    return result.lambda_merged, result.scv_merged


def npfqn_traffic_merge_cs(lambda_rates, scv_rates, P):
    result = jpype.JPackage('jline').api.npfqn.Npfqn_traffic_merge_csKt.npfqn_traffic_merge_cs(
        jlineMatrixFromArray(lambda_rates),
        jlineMatrixFromArray(scv_rates),
        jlineMatrixFromArray(P)
    )

    return jlineMatrixToArray(result.lambda_merged), jlineMatrixToArray(result.scv_merged)


def npfqn_traffic_split_cs(lambda_rate, scv_rate, P):
    result = jpype.JPackage('jline').api.npfqn.Npfqn_traffic_split_csKt.npfqn_traffic_split_cs(
        jpype.JDouble(lambda_rate),
        jpype.JDouble(scv_rate),
        jlineMatrixFromArray(P)
    )

    return jlineMatrixToArray(result.lambda_split), jlineMatrixToArray(result.scv_split)