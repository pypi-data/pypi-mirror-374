
import jpype
import numpy as np
from line_solver import jlineMatrixToArray, jlineMatrixFromArray


def pfqn_ca(N, L, Z):
    ret = jpype.JPackage('jline').api.pfqn.Pfqn_caKt.pfqn_ca(
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(Z)
    )

    return ret.G, ret.lG


def pfqn_panacea(N, L, Z):
    ret = jpype.JPackage('jline').api.pfqn.Pfqn_panaceaKt.pfqn_panacea(
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(Z)
    )

    return ret.G, ret.lG


def pfqn_bs(N, L, Z):
    ret = jpype.JPackage('jline').api.pfqn.Pfqn_bsKt.pfqn_bs(
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(Z)
    )

    XN = jlineMatrixToArray(ret.XN)
    QN = jlineMatrixToArray(ret.QN)
    UN = jlineMatrixToArray(ret.UN)
    RN = jlineMatrixToArray(ret.RN)
    TN = jlineMatrixToArray(ret.TN)
    AN = jlineMatrixToArray(ret.AN)

    CN = np.sum(RN, axis=0) + np.diag(Z)

    return XN, CN, QN, UN, RN, TN, AN


def pfqn_mva(N, L, Z):
    ret = jpype.JPackage('jline').api.pfqn.Pfqn_mvaKt.pfqn_mva(
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(Z)
    )

    XN = jlineMatrixToArray(ret.XN)
    QN = jlineMatrixToArray(ret.QN)
    UN = jlineMatrixToArray(ret.UN)
    RN = jlineMatrixToArray(ret.RN)
    TN = jlineMatrixToArray(ret.TN)
    AN = jlineMatrixToArray(ret.AN)

    CN = np.sum(RN, axis=0) + np.diag(Z)

    return XN, CN, QN, UN, RN, TN, AN


def pfqn_aql(N, L, Z):
    ret = jpype.JPackage('jline').api.pfqn.Pfqn_aqlKt.pfqn_aql(
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(Z),
        jpype.JInt(1000)
    )

    XN = jlineMatrixToArray(ret.XN)
    QN = jlineMatrixToArray(ret.QN)
    UN = jlineMatrixToArray(ret.UN)
    RN = jlineMatrixToArray(ret.RN)
    TN = jlineMatrixToArray(ret.TN)
    AN = jlineMatrixToArray(ret.AN)

    CN = np.sum(RN, axis=0) + np.diag(Z)

    return XN, CN, QN, UN, RN, TN, AN


def pfqn_mvald(L, N, Z, mu, stabilize=True):
    result = jpype.JPackage("jline").api.pfqn.Pfqn_mvaldKt.pfqn_mvald(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jlineMatrixFromArray(mu),
        jpype.JBoolean(stabilize)
    )

    XN = jlineMatrixToArray(result.XN)
    QN = jlineMatrixToArray(result.QN)
    UN = jlineMatrixToArray(result.UN)
    CN = jlineMatrixToArray(result.CN)
    lGN = jlineMatrixToArray(result.lGN)

    return XN, QN, UN, CN, lGN, result.isNumStable, jlineMatrixToArray(result.newpi)


def pfqn_mvaldms(lambda_rates, D, N, Z, S):
    result = jpype.JPackage("jline").api.pfqn.Pfqn_mvaldmsKt.pfqn_mvaldms(
        jlineMatrixFromArray(lambda_rates),
        jlineMatrixFromArray(D),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jlineMatrixFromArray(S)
    )

    XN = jlineMatrixToArray(result.XN)
    QN = jlineMatrixToArray(result.QN)
    UN = jlineMatrixToArray(result.UN)
    CN = jlineMatrixToArray(result.CN)
    lGN = jlineMatrixToArray(result.lGN)

    return XN, QN, UN, CN, lGN


def pfqn_mvaldmx(lambda_rates, D, N, Z, mu=None, S=None):
    mu_matrix = jlineMatrixFromArray(mu) if mu is not None else None
    S_matrix = jlineMatrixFromArray(S) if S is not None else None

    result = jpype.JPackage("jline").api.pfqn.Pfqn_mvaldmxKt.pfqn_mvaldmx(
        jlineMatrixFromArray(lambda_rates),
        jlineMatrixFromArray(D),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        mu_matrix,
        S_matrix
    )

    XN = jlineMatrixToArray(result.XN)
    QN = jlineMatrixToArray(result.QN)
    UN = jlineMatrixToArray(result.UN)
    CN = jlineMatrixToArray(result.CN)
    lGN = jlineMatrixToArray(result.lGN)
    newPc = jlineMatrixToArray(result.newPc)

    return XN, QN, UN, CN, lGN, newPc


def pfqn_mvams(lambda_rates, L, N, Z, mi=None, S=None):
    mi_matrix = jlineMatrixFromArray(mi) if mi is not None else None
    S_matrix = jlineMatrixFromArray(S) if S is not None else None

    result = jpype.JPackage("jline").api.pfqn.Pfqn_mvamsKt.pfqn_mvams(
        jlineMatrixFromArray(lambda_rates),
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        mi_matrix,
        S_matrix
    )

    XN = jlineMatrixToArray(result.XN)
    QN = jlineMatrixToArray(result.QN)
    UN = jlineMatrixToArray(result.UN)
    CN = jlineMatrixToArray(result.CN)
    lGN = jlineMatrixToArray(result.lGN)

    return XN, QN, UN, CN, lGN


def pfqn_mvamx(lambda_rates, D, N, Z, mi=None):
    mi_matrix = jlineMatrixFromArray(mi) if mi is not None else None

    result = jpype.JPackage("jline").api.pfqn.Pfqn_mvamxKt.pfqn_mvamx(
        jlineMatrixFromArray(lambda_rates),
        jlineMatrixFromArray(D),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        mi_matrix
    )

    XN = jlineMatrixToArray(result.XN)
    QN = jlineMatrixToArray(result.QN)
    UN = jlineMatrixToArray(result.UN)
    CN = jlineMatrixToArray(result.CN)
    lGN = jlineMatrixToArray(result.lGN)

    return XN, QN, UN, CN, lGN


def pfqn_nc(lambda_rates, L, N, Z, options):
    result = jpype.JPackage("jline").api.pfqn.Pfqn_ncKt.pfqn_nc(
        jlineMatrixFromArray(lambda_rates),
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        options
    )

    lG = result.lG
    X = jlineMatrixToArray(result.X)
    Q = jlineMatrixToArray(result.Q)
    method = result.method

    return lG, X, Q, method


def pfqn_gld(L, N, mu=None, options=None):
    mu_matrix = jlineMatrixFromArray(mu) if mu is not None else None

    result = jpype.JPackage("jline").api.pfqn.Pfqn_gldKt.pfqn_gld(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        mu_matrix,
        options
    )

    return result.G, result.lG


def pfqn_gldsingle(L, N, mu, options=None):
    result = jpype.JPackage("jline").api.pfqn.Pfqn_gldsingleKt.pfqn_gldsingle(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(mu),
        options
    )

    return result.G, result.lG


def pfqn_comomrm(L, N, Z, m=None, atol=1e-8):
    m_val = jpype.JInt(m) if m is not None else None

    result = jpype.JPackage("jline").api.pfqn.Pfqn_comomrmKt.pfqn_comomrm(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        m_val,
        jpype.JDouble(atol)
    )

    return result.lG, jlineMatrixToArray(result.lGbasis)



def pfqn_linearizer(L, N, Z, schedule_types, tol=1e-8, maxiter=1000):
    java_schedule_types = jpype.JArray(jpype.JPackage("jline").lang.constant.SchedStrategy)(len(schedule_types))
    for i, sched in enumerate(schedule_types):
        java_schedule_types[i] = sched

    result = jpype.JPackage("jline").api.pfqn.Pfqn_linearizerKt.pfqn_linearizer(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        java_schedule_types,
        jpype.JDouble(tol),
        jpype.JInt(maxiter)
    )

    Q = jlineMatrixToArray(result.Q)
    U = jlineMatrixToArray(result.U)
    R = jlineMatrixToArray(result.R)
    C = jlineMatrixToArray(result.C)
    X = jlineMatrixToArray(result.X)

    return Q, U, R, C, X, result.totiter


def pfqn_linearizerms(L, N, Z, nservers, schedule_types, tol=1e-8, maxiter=1000):
    java_schedule_types = jpype.java.util.ArrayList()
    for sched in schedule_types:
        java_schedule_types.add(sched)

    result = jpype.JPackage("jline").api.pfqn.Pfqn_linearizermxKt.pfqn_linearizerms(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jlineMatrixFromArray(nservers),
        java_schedule_types,
        jpype.JDouble(tol),
        jpype.JInt(maxiter)
    )

    Q = jlineMatrixToArray(result.Q)
    U = jlineMatrixToArray(result.U)
    W = jlineMatrixToArray(result.W)
    C = jlineMatrixToArray(result.C)
    X = jlineMatrixToArray(result.X)

    return Q, U, W, C, X, result.totiter


def pfqn_linearizerpp(L, N, Z, level=2, tol=1e-8, maxiter=1000, flag=0):
    result = jpype.JPackage("jline").api.pfqn.Pfqn_linearizerppKt.pfqn_linearizerpp(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jpype.JInt(level),
        jpype.JDouble(tol),
        jpype.JInt(maxiter),
        jpype.JInt(flag)
    )

    Q = jlineMatrixToArray(result.Q)
    U = jlineMatrixToArray(result.U)
    R = jlineMatrixToArray(result.R)
    C = jlineMatrixToArray(result.C)
    X = jlineMatrixToArray(result.X)

    return Q, U, R, C, X, result.totiter


def pfqn_linearizermx(lambda_rates, L, N, Z, nservers, schedule_types, tol=1e-8, maxiter=1000, method="lin"):
    java_schedule_types = jpype.JArray(jpype.JPackage("jline").lang.constant.SchedStrategy)(len(schedule_types))
    for i, sched in enumerate(schedule_types):
        java_schedule_types[i] = sched

    result = jpype.JPackage("jline").api.pfqn.Pfqn_linearizermxKt.pfqn_linearizermx(
        jlineMatrixFromArray(lambda_rates),
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jlineMatrixFromArray(nservers),
        java_schedule_types,
        jpype.JDouble(tol),
        jpype.JInt(maxiter),
        jpype.JString(method)
    )

    Q = jlineMatrixToArray(result.Q)
    U = jlineMatrixToArray(result.U)
    R = jlineMatrixToArray(result.R)
    C = jlineMatrixToArray(result.C)
    X = jlineMatrixToArray(result.X)

    return Q, U, R, C, X, result.totiter


def pfqn_kt(L, N, Z):
    result = jpype.JPackage("jline").api.pfqn.Pfqn_ktKt.pfqn_kt(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z)
    )

    return result.G, result.lG


def pfqn_recal(L, N, Z=None, m0=None):
    Z_matrix = jlineMatrixFromArray(Z) if Z is not None else None
    m0_matrix = jlineMatrixFromArray(m0) if m0 is not None else None

    result = jpype.JPackage("jline").api.pfqn.Pfqn_recalKt.pfqn_recal(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        Z_matrix,
        m0_matrix
    )

    return result.G, result.lG


def pfqn_cub(L, N, Z, order=3, atol=1e-8):
    result = jpype.JPackage("jline").api.pfqn.Pfqn_cubKt.pfqn_cub(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jpype.JInt(order),
        jpype.JDouble(atol)
    )

    return result.G, result.lG


def pfqn_mmint2(L, N, Z):
    result = jpype.JPackage("jline").api.pfqn.Pfqn_mmint2Kt.pfqn_mmint2(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z)
    )

    return result.G, result.lG


def pfqn_ls(L, N, Z=None, I=10000, seed=12345):
    Z_matrix = jlineMatrixFromArray(Z) if Z is not None else None

    result = jpype.JPackage("jline").api.pfqn.Pfqn_lsKt.pfqn_ls(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        Z_matrix,
        jpype.JLong(I),
        jpype.JLong(seed)
    )

    return result.G, result.lG


def pfqn_rd(L, N, Z, mu, options=None):
    result = jpype.JPackage("jline").api.pfqn.Pfqn_rdKt.pfqn_rd(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jlineMatrixFromArray(mu),
        options
    )

    return result.lG, jlineMatrixToArray(result.Cgamma)


def pfqn_fnc(alpha, c):
    result = jpype.JPackage("jline").api.pfqn.Pfqn_fncKt.pfqn_fnc(
        jlineMatrixFromArray(alpha),
        jlineMatrixFromArray(c)
    )

    return jlineMatrixToArray(result.mu), jlineMatrixToArray(result.c)


def pfqn_propfair(L, N, Z):
    result = jpype.JPackage("jline").api.pfqn.Pfqn_propfairKt.pfqn_propfair(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z)
    )

    return result.G, result.lG, jlineMatrixToArray(result.X), jlineMatrixToArray(result.Q), result.method


def pfqn_xia(L, N, s, options=None):
    return jpype.JPackage("jline").api.pfqn.Pfqn_xiaKt.pfqn_xia(
        jlineMatrixFromArray(L),
        jpype.JInt(N),
        jlineMatrixFromArray(s),
        options
    )


def pfqn_xzabalow(L, N, Z):
    return jpype.JPackage("jline").api.pfqn.Pfqn_xzabalowKt.pfqn_xzabalow(
        jlineMatrixFromArray(L),
        jpype.JDouble(N),
        jpype.JDouble(Z)
    )


def pfqn_xzabaup(L, N, Z):
    return jpype.JPackage("jline").api.pfqn.Pfqn_xzabaupKt.pfqn_xzabaup(
        jlineMatrixFromArray(L),
        jpype.JDouble(N),
        jpype.JDouble(Z)
    )


def pfqn_xzgsblow(L, N, Z):
    return jpype.JPackage("jline").api.pfqn.Pfqn_xzgsblowKt.pfqn_xzgsblow(
        jlineMatrixFromArray(L),
        jpype.JDouble(N),
        jpype.JDouble(Z)
    )


def pfqn_xzgsbup(L, N, Z):
    return jpype.JPackage("jline").api.pfqn.Pfqn_xzgsbupKt.pfqn_xzgsbup(
        jlineMatrixFromArray(L),
        jpype.JDouble(N),
        jpype.JDouble(Z)
    )




def pfqn_conwayms(lambda_rates, L, N, Z, nservers, options=None):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_conwaymsKt.pfqn_conwayms(
        jlineMatrixFromArray(lambda_rates),
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jlineMatrixFromArray(nservers),
        options
    )

    XN = jlineMatrixToArray(result.XN)
    QN = jlineMatrixToArray(result.QN)
    UN = jlineMatrixToArray(result.UN)
    RN = jlineMatrixToArray(result.RN)

    return XN, QN, UN, RN


def pfqn_egflinearizer(L, N, Z, tol=1e-8, maxiter=1000):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_egflinearizerKt.pfqn_egflinearizer(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jpype.JDouble(tol),
        jpype.JInt(maxiter)
    )

    Q = jlineMatrixToArray(result.Q)
    U = jlineMatrixToArray(result.U)
    R = jlineMatrixToArray(result.R)
    X = jlineMatrixToArray(result.X)

    return Q, U, R, X, result.totiter


def pfqn_gflinearizer(L, N, Z, tol=1e-8, maxiter=1000):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_gflinearizerKt.pfqn_gflinearizer(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jpype.JDouble(tol),
        jpype.JInt(maxiter)
    )

    Q = jlineMatrixToArray(result.Q)
    U = jlineMatrixToArray(result.U)
    R = jlineMatrixToArray(result.R)
    X = jlineMatrixToArray(result.X)

    return Q, U, R, X, result.totiter


def pfqn_gld_complex(L, N, mu=None, options=None):
    mu_matrix = jlineMatrixFromArray(mu) if mu is not None else None

    result = jpype.JPackage('jline').api.pfqn.Pfqn_gld_complexKt.pfqn_gld_complex(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        mu_matrix,
        options
    )

    return result.G, result.lG


def pfqn_gldsingle_complex(L, N, mu, options=None):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_gldsingle_complexKt.pfqn_gldsingle_complex(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(mu),
        options
    )

    return result.G, result.lG


def pfqn_le_hessian(L, N, Z, mu=None, options=None):
    mu_matrix = jlineMatrixFromArray(mu) if mu is not None else None

    return jlineMatrixToArray(
        jpype.JPackage('jline').api.pfqn.Pfqn_le_hessianKt.pfqn_le_hessian(
            jlineMatrixFromArray(L),
            jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z),
            mu_matrix,
            options
        )
    )


def pfqn_le_hessianZ(L, N, Z, mu=None, options=None):
    mu_matrix = jlineMatrixFromArray(mu) if mu is not None else None

    return jlineMatrixToArray(
        jpype.JPackage('jline').api.pfqn.Pfqn_le_hessianZKt.pfqn_le_hessianZ(
            jlineMatrixFromArray(L),
            jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z),
            mu_matrix,
            options
        )
    )


def pfqn_lldfun(L, N, Z, mu, options=None):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.pfqn.Pfqn_lldfunKt.pfqn_lldfun(
            jlineMatrixFromArray(L),
            jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z),
            jlineMatrixFromArray(mu),
            options
        )
    )


def pfqn_mci(L, N, Z, nsample=10000, seed=12345):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_mciKt.pfqn_mci(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jpype.JInt(nsample),
        jpype.JInt(seed)
    )

    return result.G, result.lG, result.variance


def pfqn_mmint2_gausslegendre(L, N, Z, order=5):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_mmint2_gausslegendreKt.pfqn_mmint2_gausslegendre(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jpype.JInt(order)
    )

    return result.G, result.lG


def pfqn_mmsample2(L, N, Z, nsample=10000, seed=12345):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_mmsample2Kt.pfqn_mmsample2(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jpype.JInt(nsample),
        jpype.JInt(seed)
    )

    return result.G, result.lG, jlineMatrixToArray(result.samples)


def pfqn_mushift(L, N, Z, mu, shift_factor=1.0):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_mushiftKt.pfqn_mushift(
        jlineMatrixFromArray(L),
        jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z),
        jlineMatrixFromArray(mu),
        jpype.JDouble(shift_factor)
    )

    return jlineMatrixToArray(result.mu_shifted), result.G, result.lG


def pfqn_le(L, N, Z, options=None):
    java_options = None
    if options is not None:
        pass

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_leKt.pfqn_le(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_leKt.pfqn_le(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z)
        )

    return {
        'X': jlineMatrixToArray(result.getX()) if hasattr(result, 'getX') else None,
        'R': jlineMatrixToArray(result.getR()) if hasattr(result, 'getR') else None,
        'Q': jlineMatrixToArray(result.getQ()) if hasattr(result, 'getQ') else None
    }


def pfqn_le_fpi(L, N, Z, max_iter=1000, tol=1e-6):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_le_fpiKt.pfqn_le_fpi(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z), jpype.JInt(max_iter), jpype.JDouble(tol)
    )

    return {
        'X': jlineMatrixToArray(result.getX()),
        'R': jlineMatrixToArray(result.getR()),
        'Q': jlineMatrixToArray(result.getQ()),
        'converged': bool(result.getConverged()) if hasattr(result, 'getConverged') else None,
        'iterations': int(result.getIterations()) if hasattr(result, 'getIterations') else None
    }


def pfqn_le_fpiZ(L, N, Z, max_iter=1000, tol=1e-6):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_le_fpiZKt.pfqn_le_fpiZ(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z), jpype.JInt(max_iter), jpype.JDouble(tol)
    )

    return {
        'X': jlineMatrixToArray(result.getX()),
        'R': jlineMatrixToArray(result.getR()),
        'Q': jlineMatrixToArray(result.getQ()),
        'Z_coeffs': jlineMatrixToArray(result.getZCoeffs()) if hasattr(result, 'getZCoeffs') else None
    }


def pfqn_le_hessian(L, N, Z, step_size=1e-6):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_le_hessianKt.pfqn_le_hessian(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z), jpype.JDouble(step_size)
    )

    return {
        'X': jlineMatrixToArray(result.getX()),
        'R': jlineMatrixToArray(result.getR()),
        'Q': jlineMatrixToArray(result.getQ()),
        'hessian': jlineMatrixToArray(result.getHessian()) if hasattr(result, 'getHessian') else None
    }


def pfqn_le_hessianZ(L, N, Z, step_size=1e-6):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_le_hessianZKt.pfqn_le_hessianZ(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z), jpype.JDouble(step_size)
    )

    return {
        'X': jlineMatrixToArray(result.getX()),
        'R': jlineMatrixToArray(result.getR()),
        'Q': jlineMatrixToArray(result.getQ()),
        'hessian_Z': jlineMatrixToArray(result.getHessianZ()) if hasattr(result, 'getHessianZ') else None
    }


def pfqn_lldfun(L, N, Z, lambda_vec):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_lldfunKt.pfqn_lldfun(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z), jlineMatrixFromArray(lambda_vec)
    )

    return {
        'lld': jlineMatrixToArray(result.getLLD()),
        'gradient': jlineMatrixToArray(result.getGradient()) if hasattr(result, 'getGradient') else None,
        'likelihood': float(result.getLikelihood()) if hasattr(result, 'getLikelihood') else None
    }


def pfqn_mci(L, N, Z, num_samples=10000, confidence=0.95):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_mciKt.pfqn_mci(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z), jpype.JInt(num_samples), jpype.JDouble(confidence)
    )

    return {
        'X_mean': jlineMatrixToArray(result.getXMean()),
        'X_ci': jlineMatrixToArray(result.getXCI()) if hasattr(result, 'getXCI') else None,
        'R_mean': jlineMatrixToArray(result.getRMean()),
        'R_ci': jlineMatrixToArray(result.getRCI()) if hasattr(result, 'getRCI') else None,
        'samples_used': int(result.getSamplesUsed()) if hasattr(result, 'getSamplesUsed') else num_samples
    }


def pfqn_mmint2_gausslegendre(L, N, Z, order=10):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_mmint2_gausslegendreKt.pfqn_mmint2_gausslegendre(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z), jpype.JInt(order)
    )

    return {
        'integral': jlineMatrixToArray(result.getIntegral()),
        'nodes': jlineMatrixToArray(result.getNodes()) if hasattr(result, 'getNodes') else None,
        'weights': jlineMatrixToArray(result.getWeights()) if hasattr(result, 'getWeights') else None
    }


def pfqn_mmsample2(L, N, Z, num_samples=1000):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_mmsample2Kt.pfqn_mmsample2(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z), jpype.JInt(num_samples)
    )

    return {
        'stage1_X': jlineMatrixToArray(result.getStage1X()),
        'stage2_X': jlineMatrixToArray(result.getStage2X()),
        'combined_X': jlineMatrixToArray(result.getCombinedX()),
        'variance_reduction': float(result.getVarianceReduction()) if hasattr(result, 'getVarianceReduction') else None
    }


def pfqn_mu_ms(L, N, Z, server_counts):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_mu_msKt.pfqn_mu_ms(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z), jlineMatrixFromArray(server_counts)
    )

    return {
        'X': jlineMatrixToArray(result.getX()),
        'R': jlineMatrixToArray(result.getR()),
        'Q': jlineMatrixToArray(result.getQ()),
        'U': jlineMatrixToArray(result.getU()) if hasattr(result, 'getU') else None
    }


def pfqn_nrl(L, N, Z, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_nrlKt.pfqn_nrl(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_nrlKt.pfqn_nrl(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z)
        )

    return {
        'G': result.G if hasattr(result, 'G') else None,
        'logG': result.logG if hasattr(result, 'logG') else None,
        'converged': result.converged if hasattr(result, 'converged') else None
    }


def pfqn_nrp(L, N, Z, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_nrpKt.pfqn_nrp(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_nrpKt.pfqn_nrp(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z)
        )

    return {
        'G': result.G if hasattr(result, 'G') else None,
        'prob': jlineMatrixToArray(result.prob) if hasattr(result, 'prob') else None,
        'converged': result.converged if hasattr(result, 'converged') else None
    }


def pfqn_stdf(L, N, Z, S, fcfs_nodes, rates, tset):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_stdfKt.pfqn_stdf(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z), jlineMatrixFromArray(S),
        jlineMatrixFromArray(fcfs_nodes), jlineMatrixFromArray(rates),
        jlineMatrixFromArray(tset)
    )

    return {
        'cdf': jlineMatrixToArray(result.cdf) if hasattr(result, 'cdf') else None,
        'pdf': jlineMatrixToArray(result.pdf) if hasattr(result, 'pdf') else None,
        'mean': jlineMatrixToArray(result.mean) if hasattr(result, 'mean') else None
    }


def pfqn_stdf_heur(L, N, Z, S, fcfs_nodes, rates, tset, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_stdf_heurKt.pfqn_stdf_heur(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(S),
            jlineMatrixFromArray(fcfs_nodes), jlineMatrixFromArray(rates),
            jlineMatrixFromArray(tset), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_stdf_heurKt.pfqn_stdf_heur(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(S),
            jlineMatrixFromArray(fcfs_nodes), jlineMatrixFromArray(rates),
            jlineMatrixFromArray(tset)
        )

    return {
        'cdf': jlineMatrixToArray(result.cdf) if hasattr(result, 'cdf') else None,
        'pdf': jlineMatrixToArray(result.pdf) if hasattr(result, 'pdf') else None,
        'mean': jlineMatrixToArray(result.mean) if hasattr(result, 'mean') else None
    }


def pfqn_conwayms_core(L, N, Z, S, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_conwayms_coreKt.pfqn_conwayms_core(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(S), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_conwayms_coreKt.pfqn_conwayms_core(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(S)
        )

    return {
        'XN': jlineMatrixToArray(result.XN) if hasattr(result, 'XN') else None,
        'QN': jlineMatrixToArray(result.QN) if hasattr(result, 'QN') else None,
        'RN': jlineMatrixToArray(result.RN) if hasattr(result, 'RN') else None,
        'UN': jlineMatrixToArray(result.UN) if hasattr(result, 'UN') else None
    }


def pfqn_conwayms_estimate(L, N, Z, S, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_conwayms_estimateKt.pfqn_conwayms_estimate(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(S), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_conwayms_estimateKt.pfqn_conwayms_estimate(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(S)
        )

    return {
        'XN': jlineMatrixToArray(result.XN) if hasattr(result, 'XN') else None,
        'QN': jlineMatrixToArray(result.QN) if hasattr(result, 'QN') else None,
        'RN': jlineMatrixToArray(result.RN) if hasattr(result, 'RN') else None,
        'UN': jlineMatrixToArray(result.UN) if hasattr(result, 'UN') else None
    }


def pfqn_conwayms_forwardmva(L, N, Z, S, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_conwayms_forwardmvaKt.pfqn_conwayms_forwardmva(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(S), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_conwayms_forwardmvaKt.pfqn_conwayms_forwardmva(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(S)
        )

    return {
        'XN': jlineMatrixToArray(result.XN) if hasattr(result, 'XN') else None,
        'QN': jlineMatrixToArray(result.QN) if hasattr(result, 'QN') else None,
        'RN': jlineMatrixToArray(result.RN) if hasattr(result, 'RN') else None,
        'UN': jlineMatrixToArray(result.UN) if hasattr(result, 'UN') else None
    }


def pfqn_mu_ms_gnaux(L, N, Z, S, mu, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_mu_ms_gnauxKt.pfqn_mu_ms_gnaux(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(S),
            jlineMatrixFromArray(mu), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_mu_ms_gnauxKt.pfqn_mu_ms_gnaux(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(S),
            jlineMatrixFromArray(mu)
        )

    return {
        'scaling': jlineMatrixToArray(result.scaling) if hasattr(result, 'scaling') else None,
        'G': result.G if hasattr(result, 'G') else None,
        'converged': result.converged if hasattr(result, 'converged') else None
    }


def pfqn_nc(N, L, Z, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_ncKt.pfqn_nc(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_ncKt.pfqn_nc(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z)
        )

    return {
        'QN': jlineMatrixToArray(result.QN),
        'UN': jlineMatrixToArray(result.UN),
        'RN': jlineMatrixToArray(result.RN),
        'TN': jlineMatrixToArray(result.TN),
        'CN': jlineMatrixToArray(result.CN) if hasattr(result, 'CN') else None
    }


def pfqn_gld(L, N, mu, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_gldKt.pfqn_gld(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(mu), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_gldKt.pfqn_gld(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(mu)
        )

    return {
        'QN': jlineMatrixToArray(result.QN),
        'UN': jlineMatrixToArray(result.UN),
        'RN': jlineMatrixToArray(result.RN),
        'TN': jlineMatrixToArray(result.TN)
    }


def pfqn_le(N, L, Z, mu, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_leKt.pfqn_le(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(mu), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_leKt.pfqn_le(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(mu)
        )

    return {
        'QN': jlineMatrixToArray(result.QN),
        'UN': jlineMatrixToArray(result.UN),
        'RN': jlineMatrixToArray(result.RN),
        'TN': jlineMatrixToArray(result.TN)
    }


def pfqn_conwayms(N, L, Z, S, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_conwaymsKt.pfqn_conwayms(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(S), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_conwaymsKt.pfqn_conwayms(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(S)
        )

    return {
        'QN': jlineMatrixToArray(result.QN),
        'UN': jlineMatrixToArray(result.UN),
        'RN': jlineMatrixToArray(result.RN),
        'TN': jlineMatrixToArray(result.TN)
    }


def pfqn_cdfun(N, L, Z, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_cdfunKt.pfqn_cdfun(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_cdfunKt.pfqn_cdfun(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z)
        )

    return {
        'cdf': jlineMatrixToArray(result.cdf) if hasattr(result, 'cdf') else None,
        'support': jlineMatrixToArray(result.support) if hasattr(result, 'support') else None
    }


def pfqn_nca(N, L, Z, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_ncaKt.pfqn_nca(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_ncaKt.pfqn_nca(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z)
        )

    return {
        'QN': jlineMatrixToArray(result.QN),
        'UN': jlineMatrixToArray(result.UN),
        'RN': jlineMatrixToArray(result.RN),
        'TN': jlineMatrixToArray(result.TN)
    }


def pfqn_ncld(N, L, Z, mu, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_ncldKt.pfqn_ncld(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(mu), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_ncldKt.pfqn_ncld(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z), jlineMatrixFromArray(mu)
        )

    return {
        'QN': jlineMatrixToArray(result.QN),
        'UN': jlineMatrixToArray(result.UN),
        'RN': jlineMatrixToArray(result.RN),
        'TN': jlineMatrixToArray(result.TN)
    }


def pfqn_pff_delay(N, L, Z, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_pff_delayKt.pfqn_pff_delay(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_pff_delayKt.pfqn_pff_delay(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z)
        )

    return {
        'QN': jlineMatrixToArray(result.QN),
        'UN': jlineMatrixToArray(result.UN),
        'RN': jlineMatrixToArray(result.RN),
        'TN': jlineMatrixToArray(result.TN)
    }


def pfqn_sqni(N, L, Z, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_sqniKt.pfqn_sqni(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_sqniKt.pfqn_sqni(
            jlineMatrixFromArray(N), jlineMatrixFromArray(L),
            jlineMatrixFromArray(Z)
        )

    return {
        'QN': jlineMatrixToArray(result.QN),
        'UN': jlineMatrixToArray(result.UN),
        'RN': jlineMatrixToArray(result.RN),
        'TN': jlineMatrixToArray(result.TN)
    }


def pfqn_nc_sanitize(L, N, Z, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_nc_sanitizeKt.pfqn_nc_sanitize(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z), java_options
        )
    else:
        result = jpype.JPackage('jline').api.pfqn.Pfqn_nc_sanitizeKt.pfqn_nc_sanitize(
            jlineMatrixFromArray(L), jlineMatrixFromArray(N),
            jlineMatrixFromArray(Z)
        )

    return {
        'QN': jlineMatrixToArray(result.QN),
        'UN': jlineMatrixToArray(result.UN),
        'RN': jlineMatrixToArray(result.RN),
        'TN': jlineMatrixToArray(result.TN),
        'G': float(result.G) if hasattr(result, 'G') else None
    }


def pfqn_qzgblow(M, N):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_qzgblowKt.pfqn_qzgblow(
        jlineMatrixFromArray(M), jlineMatrixFromArray(N)
    )
    return float(result)


def pfqn_qzgbup(M, N):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_qzgbupKt.pfqn_qzgbup(
        jlineMatrixFromArray(M), jlineMatrixFromArray(N)
    )
    return float(result)


def pfqn_nc_sanitize(L, N, Z):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_nc_sanitizeKt.pfqn_nc_sanitize(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z)
    )

    return {
        'L_sanitized': jlineMatrixToArray(result.L),
        'N_sanitized': jlineMatrixToArray(result.N),
        'Z_sanitized': jlineMatrixToArray(result.Z),
        'scaling_factor': float(result.scalingFactor) if hasattr(result, 'scalingFactor') else None
    }


def pfqn_comomrm_ld(L, N, Z, S):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_comomrm_ldKt.pfqn_comomrm_ld(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z), jlineMatrixFromArray(S)
    )

    return {
        'QN': jlineMatrixToArray(result.QN),
        'UN': jlineMatrixToArray(result.UN),
        'RN': jlineMatrixToArray(result.RN),
        'TN': jlineMatrixToArray(result.TN),
        'G': float(result.G) if hasattr(result, 'G') else None
    }


def pfqn_mvaldmx_ec(L, N, Z, S):
    result = jpype.JPackage('jline').api.pfqn.Pfqn_mvaldmx_ecKt.pfqn_mvaldmx_ec(
        jlineMatrixFromArray(L), jlineMatrixFromArray(N),
        jlineMatrixFromArray(Z), jlineMatrixFromArray(S)
    )

    return {
        'QN': jlineMatrixToArray(result.QN),
        'UN': jlineMatrixToArray(result.UN),
        'RN': jlineMatrixToArray(result.RN),
        'TN': jlineMatrixToArray(result.TN),
        'G': float(result.G) if hasattr(result, 'G') else None
    }
