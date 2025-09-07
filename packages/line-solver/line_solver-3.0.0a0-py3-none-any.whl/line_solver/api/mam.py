
import jpype
import numpy as np
from line_solver import jlineMatrixToArray, jlineMatrixFromArray


def map_pie(D0, D1=None):
    if hasattr(D0, 'get') and hasattr(D0, 'length'):
        if D0.length() == 2:
            return jlineMatrixToArray(
                jpype.JPackage('jline').api.mam.Map_pieKt.map_pie(D0)
            )
        else:
            raise ValueError("D0 container must have exactly 2 elements")

    elif D1 is None:
        if isinstance(D0, (list, np.ndarray)):
            D0_array = np.array(D0)
            if D0_array.ndim == 3 and D0_array.shape[0] == 2:
                D0_mat = jlineMatrixFromArray(D0_array[0])
                D1_mat = jlineMatrixFromArray(D0_array[1])
                return jlineMatrixToArray(
                    jpype.JPackage('jline').api.mam.Map_pieKt.map_pie(D0_mat, D1_mat)
                )
            else:
                raise ValueError("When D1 is None, D0 must be a 3D array with shape (2, n, n)")
        else:
            raise ValueError("Invalid input type for D0 when D1 is None")

    else:
        return jlineMatrixToArray(
            jpype.JPackage('jline').api.mam.Map_pieKt.map_pie(
                jlineMatrixFromArray(D0),
                jlineMatrixFromArray(D1)
            )
        )


def map_mean(D0, D1=None):
    if hasattr(D0, 'get') and hasattr(D0, 'length'):
        if D0.length() == 2:
            return jpype.JPackage('jline').api.mam.Map_meanKt.map_mean(D0)
        else:
            raise ValueError("D0 container must have exactly 2 elements")

    elif D1 is None:
        if isinstance(D0, (list, np.ndarray)):
            D0_array = np.array(D0)
            if D0_array.ndim == 3 and D0_array.shape[0] == 2:
                D0_mat = jlineMatrixFromArray(D0_array[0])
                D1_mat = jlineMatrixFromArray(D0_array[1])
                return jpype.JPackage('jline').api.mam.Map_meanKt.map_mean(D0_mat, D1_mat)
            else:
                raise ValueError("When D1 is None, D0 must be a 3D array with shape (2, n, n)")
        else:
            raise ValueError("Invalid input type for D0 when D1 is None")

    else:
        return jpype.JPackage('jline').api.mam.Map_meanKt.map_mean(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1)
        )


def map_var(D0, D1=None):
    if D1 is None:
        return jpype.JPackage('jline').api.mam.Map_varKt.map_var(D0)
    else:
        return jpype.JPackage('jline').api.mam.Map_varKt.map_var(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1)
        )


def map_scv(D0, D1=None):
    if D1 is None:
        return jpype.JPackage('jline').api.mam.Map_scvKt.map_scv(D0)
    else:
        return jpype.JPackage('jline').api.mam.Map_scvKt.map_scv(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1)
        )


def map_skew(D0, D1=None):
    if D1 is None:
        return jpype.JPackage('jline').api.mam.Map_skewKt.map_skew(D0)
    else:
        return jpype.JPackage('jline').api.mam.Map_skewKt.map_skew(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1)
        )


def map_moment(D0, D1, order):
    return jpype.JPackage('jline').api.mam.Map_momentKt.map_moment(
        jlineMatrixFromArray(D0),
        jlineMatrixFromArray(D1),
        jpype.JInt(order)
    )


def map_lambda(D0, D1=None):
    if D1 is None:
        return jpype.JPackage('jline').api.mam.Map_lambdaKt.map_lambda(D0)
    else:
        return jpype.JPackage('jline').api.mam.Map_lambdaKt.map_lambda(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1)
        )


def map_acf(D0, D1, lags):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Map_acfKt.map_acf(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1),
            jlineMatrixFromArray(lags)
        )
    )


def map_acfc(D0, D1, lags, u):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Map_acfcKt.map_acfc(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1),
            jlineMatrixFromArray(lags),
            jpype.JDouble(u)
        )
    )


def map_idc(D0, D1=None):
    if D1 is None:
        return jpype.JPackage('jline').api.mam.Map_idcKt.map_idc(D0)
    else:
        return jpype.JPackage('jline').api.mam.Map_idcKt.map_idc(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1)
        )


def map_gamma(D0, D1=None):
    if D1 is None:
        return jpype.JPackage('jline').api.mam.Map_gammaKt.map_gamma(D0)
    else:
        return jpype.JPackage('jline').api.mam.Map_gammaKt.map_gamma(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1)
        )


def map_gamma2(MAP):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Map_gamma2Kt.map_gamma2(MAP)
    )


def map_cdf(D0, D1, points):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Map_cdfKt.map_cdf(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1),
            jlineMatrixFromArray(points)
        )
    )


def map_piq(D0, D1=None):
    if D1 is None:
        return jlineMatrixToArray(
            jpype.JPackage('jline').api.mam.Map_piqKt.map_piq(D0)
        )
    else:
        return jlineMatrixToArray(
            jpype.JPackage('jline').api.mam.Map_piqKt.map_piq(
                jlineMatrixFromArray(D0),
                jlineMatrixFromArray(D1)
            )
        )


def map_embedded(D0, D1=None):
    if D1 is None:
        return jlineMatrixToArray(
            jpype.JPackage('jline').api.mam.Map_embeddedKt.map_embedded(D0)
        )
    else:
        return jlineMatrixToArray(
            jpype.JPackage('jline').api.mam.Map_embeddedKt.map_embedded(
                jlineMatrixFromArray(D0),
                jlineMatrixFromArray(D1)
            )
        )


def map_count_mean(MAP, t):
    return jpype.JPackage('jline').api.mam.Map_count_meanKt.map_count_mean(
        MAP, jpype.JDouble(t)
    )


def map_count_var(MAP, t):
    return jpype.JPackage('jline').api.mam.Map_count_varKt.map_count_var(
        MAP, jpype.JDouble(t)
    )


def map_varcount(D0, D1, t):
    return jpype.JPackage('jline').api.mam.Map_varcountKt.map_varcount(
        jlineMatrixFromArray(D0),
        jlineMatrixFromArray(D1),
        jpype.JDouble(t)
    )




def map2_fit(e1, e2, e3, g2):
    result = jpype.JPackage('jline').api.mam.Map2_fitKt.map2_fit(
        jpype.JDouble(e1),
        jpype.JDouble(e2),
        jpype.JDouble(e3),
        jpype.JDouble(g2)
    )

    D0 = jlineMatrixToArray(result.get(0))
    D1 = jlineMatrixToArray(result.get(1))

    return D0, D1


def aph_fit(e1, e2, e3, nmax=10):
    result = jpype.JPackage('jline').api.mam.Aph_fitKt.aph_fit(
        jpype.JDouble(e1),
        jpype.JDouble(e2),
        jpype.JDouble(e3),
        jpype.JInt(nmax)
    )

    alpha = jlineMatrixToArray(result.alpha)
    T = jlineMatrixToArray(result.T)
    feasible = result.feasible

    return alpha, T, feasible


def aph2_fit(M1, M2, M3):
    result = jpype.JPackage('jline').api.mam.Aph2_fitKt.aph2_fit(
        jpype.JDouble(M1),
        jpype.JDouble(M2),
        jpype.JDouble(M3)
    )

    alpha = jlineMatrixToArray(result.alpha)
    T = jlineMatrixToArray(result.T)
    feasible = result.feasible

    return alpha, T, feasible


def aph2_fitall(M1, M2, M3):
    result = jpype.JPackage('jline').api.mam.Aph2_fitallKt.aph2_fitall(
        jpype.JDouble(M1),
        jpype.JDouble(M2),
        jpype.JDouble(M3)
    )

    fits = []
    for i in range(result.size()):
        fit = result.get(i)
        alpha = jlineMatrixToArray(fit.alpha)
        T = jlineMatrixToArray(fit.T)
        fits.append((alpha, T))

    return fits


def aph2_adjust(M1, M2, M3, method="default"):
    result = jpype.JPackage('jline').api.mam.Aph2_adjustKt.aph2_adjust(
        jpype.JDouble(M1),
        jpype.JDouble(M2),
        jpype.JDouble(M3),
        jpype.JString(method)
    )

    return result.M1, result.M2, result.M3


def mmpp2_fit(E1, E2, E3, G2):
    result = jpype.JPackage('jline').api.mam.Mmpp2_fitKt.mmpp2_fit(
        jpype.JDouble(E1),
        jpype.JDouble(E2),
        jpype.JDouble(E3),
        jpype.JDouble(G2)
    )

    D0 = jlineMatrixToArray(result.D0)
    D1 = jlineMatrixToArray(result.D1)
    feasible = result.feasible

    return D0, D1, feasible


def mmpp2_fit1(mean, scv, skew, idc):
    result = jpype.JPackage('jline').api.mam.Mmpp2_fit1Kt.mmpp2_fit1(
        jpype.JDouble(mean),
        jpype.JDouble(scv),
        jpype.JDouble(skew),
        jpype.JDouble(idc)
    )

    D0 = jlineMatrixToArray(result.D0)
    D1 = jlineMatrixToArray(result.D1)
    feasible = result.feasible

    return D0, D1, feasible


def mmap_mixture_fit(P2, M1, M2, M3):
    result = jpype.JPackage('jline').api.mam.Mmap_mixture_fitKt.mmap_mixture_fit(
        jlineMatrixFromArray(P2),
        jlineMatrixFromArray(M1),
        jlineMatrixFromArray(M2),
        jlineMatrixFromArray(M3)
    )

    D0 = jlineMatrixToArray(result.D0)
    D1 = jlineMatrixToArray(result.D1)
    feasible = result.feasible

    return D0, D1, feasible


def mmap_mixture_fit_mmap(mmap):
    result = jpype.JPackage('jline').api.mam.Mmap_mixture_fit_mmapKt.mmap_mixture_fit_mmap(mmap)

    D0 = jlineMatrixToArray(result.D0)
    D1 = jlineMatrixToArray(result.D1)

    components = []
    for i in range(result.components.size()):
        component = result.components.get(i)
        components.append(jlineMatrixToArray(component))

    return D0, D1, components


def mamap2m_fit_gamma_fb_mmap(mmap):
    result = jpype.JPackage('jline').api.mam.Mamap2m_fit_gamma_fb_mmapKt.mamap2m_fit_gamma_fb_mmap(mmap)

    D0 = jlineMatrixToArray(result.get(0))
    D1 = jlineMatrixToArray(result.get(1))

    D_classes = []
    for i in range(2, result.length()):
        D_classes.append(jlineMatrixToArray(result.get(i)))

    return D0, D1, D_classes


def mamap2m_fit_gamma_fb(M1, M2, M3, GAMMA, P, F, B):
    import numpy as np

    P_java = jpype.JArray(jpype.JDouble)(P)
    F_java = jpype.JArray(jpype.JDouble)(F)
    B_java = jpype.JArray(jpype.JDouble)(B)

    result = jpype.JPackage('jline').api.mam.Mamap2m_fit_gamma_fb_mmapKt.mamap2m_fit_gamma_fb(
        jpype.JDouble(M1), jpype.JDouble(M2), jpype.JDouble(M3), jpype.JDouble(GAMMA),
        P_java, F_java, B_java
    )

    D0 = jlineMatrixToArray(result.get(0))
    D1 = jlineMatrixToArray(result.get(1))

    D_classes = []
    for i in range(2, result.length()):
        D_classes.append(jlineMatrixToArray(result.get(i)))

    return D0, D1, D_classes



def map_exponential(mean):
    result = jpype.JPackage('jline').api.mam.Map_exponentialKt.map_exponential(
        jpype.JDouble(mean)
    )

    D0 = jlineMatrixToArray(result.get(0))
    D1 = jlineMatrixToArray(result.get(1))

    return D0, D1


def map_erlang(mean, k):
    result = jpype.JPackage('jline').api.mam.Map_erlangKt.map_erlang(
        jpype.JDouble(mean),
        jpype.JInt(k)
    )

    D0 = jlineMatrixToArray(result.get(0))
    D1 = jlineMatrixToArray(result.get(1))

    return D0, D1


def map_hyperexp(mean, scv, p):
    result = jpype.JPackage('jline').api.mam.Map_hyperexpKt.map_hyperexp(
        jpype.JDouble(mean),
        jpype.JDouble(scv),
        jlineMatrixFromArray(p)
    )

    D0 = jlineMatrixToArray(result.get(0))
    D1 = jlineMatrixToArray(result.get(1))

    return D0, D1


def map_scale(D0, D1, newMean):
    result = jpype.JPackage('jline').api.mam.Map_scaleKt.map_scale(
        jlineMatrixFromArray(D0),
        jlineMatrixFromArray(D1),
        jpype.JDouble(newMean)
    )

    D0_scaled = jlineMatrixToArray(result.get(0))
    D1_scaled = jlineMatrixToArray(result.get(1))

    return D0_scaled, D1_scaled


def map_normalize(D0, D1):
    result = jpype.JPackage('jline').api.mam.Map_normalizeKt.map_normalize(
        jlineMatrixFromArray(D0),
        jlineMatrixFromArray(D1)
    )

    D0_norm = jlineMatrixToArray(result.get(0))
    D1_norm = jlineMatrixToArray(result.get(1))

    return D0_norm, D1_norm


def map_timereverse(map_input):
    if isinstance(map_input, tuple):
        D0, D1 = map_input
        result = jpype.JPackage('jline').api.mam.Map_timereverseKt.map_timereverse(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Map_timereverseKt.map_timereverse(map_input)

    D0_rev = jlineMatrixToArray(result.get(0))
    D1_rev = jlineMatrixToArray(result.get(1))

    return D0_rev, D1_rev


def map_mark(MAP, prob):
    if isinstance(MAP, tuple):
        D0, D1 = MAP
        result = jpype.JPackage('jline').api.mam.Map_markKt.map_mark(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1),
            jlineMatrixFromArray(prob)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Map_markKt.map_mark(
            MAP,
            jlineMatrixFromArray(prob)
        )

    D0 = jlineMatrixToArray(result.get(0))
    D1 = jlineMatrixToArray(result.get(1))

    return D0, D1


def map_infgen(D0, D1):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Map_infgenKt.map_infgen(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1)
        )
    )




def map_super(MAPa, MAPb):
    if isinstance(MAPa, tuple) and isinstance(MAPb, tuple):
        D0a, D1a = MAPa
        D0b, D1b = MAPb
        result = jpype.JPackage('jline').api.mam.Map_superKt.map_super(
            jlineMatrixFromArray(D0a),
            jlineMatrixFromArray(D1a),
            jlineMatrixFromArray(D0b),
            jlineMatrixFromArray(D1b)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Map_superKt.map_super(MAPa, MAPb)

    D0_super = jlineMatrixToArray(result.get(0))
    D1_super = jlineMatrixToArray(result.get(1))

    return D0_super, D1_super


def map_sum(MAP, n):
    if isinstance(MAP, tuple):
        D0, D1 = MAP
        result = jpype.JPackage('jline').api.mam.Map_sumKt.map_sum(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1),
            jpype.JInt(n)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Map_sumKt.map_sum(MAP, jpype.JInt(n))

    D0_sum = jlineMatrixToArray(result.get(0))
    D1_sum = jlineMatrixToArray(result.get(1))

    return D0_sum, D1_sum


def map_sumind(MAPs):
    java_maps = jpype.java.util.ArrayList()
    for MAP in MAPs:
        if isinstance(MAP, tuple):
            D0, D1 = MAP
            map_matrices = jpype.java.util.ArrayList()
            map_matrices.add(jlineMatrixFromArray(D0))
            map_matrices.add(jlineMatrixFromArray(D1))
            java_maps.add(map_matrices)
        else:
            java_maps.add(MAP)

    result = jpype.JPackage('jline').api.mam.Map_sumindKt.map_sumind(java_maps)

    D0_sum = jlineMatrixToArray(result.get(0))
    D1_sum = jlineMatrixToArray(result.get(1))

    return D0_sum, D1_sum


def map_checkfeasible(MAP, TOL=1e-10):
    if isinstance(MAP, tuple):
        D0, D1 = MAP
        return jpype.JPackage('jline').api.mam.Map_checkfeasibleKt.map_checkfeasible(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1),
            jpype.JDouble(TOL)
        )
    else:
        return jpype.JPackage('jline').api.mam.Map_checkfeasibleKt.map_checkfeasible(
            MAP, jpype.JDouble(TOL)
        )


def map_isfeasible(MAP, TOL=1e-10):
    if isinstance(MAP, tuple):
        D0, D1 = MAP
        return jpype.JPackage('jline').api.mam.Map_isfeasibleKt.map_isfeasible(
            jlineMatrixFromArray(D0),
            jlineMatrixFromArray(D1),
            jpype.JDouble(TOL)
        )
    else:
        return jpype.JPackage('jline').api.mam.Map_isfeasibleKt.map_isfeasible(
            MAP, jpype.JDouble(TOL)
        )


def map_feastol():
    return jpype.JPackage('jline').api.mam.Map_feastolKt.map_feastol()


def map_largemap():
    return jpype.JPackage('jline').api.mam.Map_largemapKt.map_largemap()


def aph2_assemble(l1, l2, p1):
    result = jpype.JPackage('jline').api.mam.Aph2_assembleKt.aph2_assemble(
        jpype.JDouble(l1),
        jpype.JDouble(l2),
        jpype.JDouble(p1)
    )

    alpha = jlineMatrixToArray(result.alpha)
    T = jlineMatrixToArray(result.T)

    return alpha, T


def ph_reindex(PHs, stationToClass):
    java_phs = jpype.java.util.ArrayList()
    for ph in PHs:
        java_phs.add(ph)

    result = jpype.JPackage('jline').api.mam.Ph_reindexKt.ph_reindex(
        java_phs,
        jlineMatrixFromArray(stationToClass)
    )

    reindexed_phs = []
    for i in range(result.size()):
        reindexed_phs.append(result.get(i))

    return reindexed_phs


def map_rand(K):
    result = jpype.JPackage('jline').api.mam.Map_randKt.map_rand(jpype.JInt(K))

    D0 = jlineMatrixToArray(result.get(0))
    D1 = jlineMatrixToArray(result.get(1))

    return D0, D1


def map_randn(K, mu, sigma):
    result = jpype.JPackage('jline').api.mam.Map_randnKt.map_randn(
        jpype.JInt(K),
        jpype.JDouble(mu),
        jpype.JDouble(sigma)
    )

    D0 = jlineMatrixToArray(result.get(0))
    D1 = jlineMatrixToArray(result.get(1))

    return D0, D1




def mmap_lambda(MMAP):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Mmap_lambdaKt.mmap_lambda(MMAP)
    )


def mmap_count_mean(MMAP, t):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Mmap_count_meanKt.mmap_count_mean(
            MMAP, jpype.JDouble(t)
        )
    )


def mmap_count_var(MMAP, t):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Mmap_count_varKt.mmap_count_var(
            MMAP, jpype.JDouble(t)
        )
    )


def mmap_count_idc(MMAP, t):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Mmap_count_idcKt.mmap_count_idc(
            MMAP, jpype.JDouble(t)
        )
    )


def mmap_idc(MMAP):
    return jpype.JPackage('jline').api.mam.Mmap_idcKt.mmap_idc(MMAP)


def mmap_sigma2(mmap):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Mmap_sigma2Kt.mmap_sigma2(mmap)
    )


def mmap_exponential(lambda_rates, n):
    return jpype.JPackage('jline').api.mam.Mmap_exponentialKt.mmap_exponential(
        jlineMatrixFromArray(lambda_rates),
        jpype.JInt(n)
    )


def mmap_mixture(alpha, MAPs):
    java_maps = jpype.java.util.ArrayList()
    for MAP in MAPs:
        java_maps.add(MAP)

    return jpype.JPackage('jline').api.mam.Mmap_mixtureKt.mmap_mixture(
        jlineMatrixFromArray(alpha),
        java_maps
    )


def mmap_super(MMAPa, MMAPb, opt="default"):
    return jpype.JPackage('jline').api.mam.Mmap_superKt.mmap_super(
        MMAPa, MMAPb, jpype.JString(opt)
    )


def mmap_super_safe(MMAPS, maxorder=10, method="default"):
    java_mmaps = jpype.java.util.ArrayList()
    for MMAP in MMAPS:
        java_mmaps.add(MMAP)

    return jpype.JPackage('jline').api.mam.Mmap_super_safeKt.mmap_super_safe(
        java_mmaps,
        jpype.JInt(maxorder),
        jpype.JString(method)
    )



def mmap_compress(MMAP, config="default"):
    return jpype.JPackage('jline').api.mam.Mmap_compressKt.mmap_compress(
        MMAP, jpype.JString(config)
    )


def mmap_normalize(MMAP):
    return jpype.JPackage('jline').api.mam.Mmap_normalizeKt.mmap_normalize(MMAP)


def mmap_scale(MMAP, M, maxIter=100):
    return jpype.JPackage('jline').api.mam.Mmap_scaleKt.mmap_scale(
        MMAP, jlineMatrixFromArray(M), jpype.JInt(maxIter)
    )


def mmap_timereverse(mmap):
    return jpype.JPackage('jline').api.mam.Mmap_timereverseKt.mmap_timereverse(mmap)


def mmap_hide(MMAP, types):
    return jpype.JPackage('jline').api.mam.Mmap_hideKt.mmap_hide(
        MMAP, jlineMatrixFromArray(types)
    )


def mmap_shorten(mmap):
    return jpype.JPackage('jline').api.mam.Mmap_shortenKt.mmap_shorten(mmap)


def mmap_maps(MMAP):
    result = jpype.JPackage('jline').api.mam.Mmap_mapsKt.mmap_maps(MMAP)

    maps = []
    for i in range(result.size()):
        maps.append(result.get(i))

    return maps


def mmap_pc(MMAP):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Mmap_pcKt.mmap_pc(MMAP)
    )


def mmap_forward_moment(MMAP, ORDERS, NORM=True):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Mmap_forward_momentKt.mmap_forward_moment(
            MMAP, jlineMatrixFromArray(ORDERS), jpype.JBoolean(NORM)
        )
    )


def mmap_backward_moment(MMAP, ORDERS, NORM=True):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Mmap_backward_momentKt.mmap_backward_moment(
            MMAP, jlineMatrixFromArray(ORDERS), jpype.JBoolean(NORM)
        )
    )


def mmap_cross_moment(mmap, k):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Mmap_cross_momentKt.mmap_cross_moment(
            mmap, jpype.JInt(k)
        )
    )


def mmap_sample(MMAP, n, random=None):
    if random is None:
        result = jpype.JPackage('jline').api.mam.Mmap_sampleKt.mmap_sample(
            MMAP, jpype.JInt(n)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Mmap_sampleKt.mmap_sample(
            MMAP, jpype.JInt(n), random
        )

    times = jlineMatrixToArray(result.times)
    classes = jlineMatrixToArray(result.classes)

    return times, classes


def mmap_rand(order, classes):
    return jpype.JPackage('jline').api.mam.Mmap_randKt.mmap_rand(
        jpype.JInt(order), jpype.JInt(classes)
    )




def map_sample(MAP, n, random=None):
    if isinstance(MAP, tuple):
        D0, D1 = MAP
        if random is None:
            return jlineMatrixToArray(
                jpype.JPackage('jline').api.mam.Map_sampleKt.map_sample(
                    jlineMatrixFromArray(D0),
                    jlineMatrixFromArray(D1),
                    jpype.JInt(n)
                )
            )
        else:
            return jlineMatrixToArray(
                jpype.JPackage('jline').api.mam.Map_sampleKt.map_sample(
                    jlineMatrixFromArray(D0),
                    jlineMatrixFromArray(D1),
                    jpype.JInt(n),
                    random
                )
            )
    else:
        if random is None:
            return jlineMatrixToArray(
                jpype.JPackage('jline').api.mam.Map_sampleKt.map_sample(
                    MAP, jpype.JInt(n)
                )
            )
        else:
            return jlineMatrixToArray(
                jpype.JPackage('jline').api.mam.Map_sampleKt.map_sample(
                    MAP, jpype.JInt(n), random
                )
            )



def mmap_count_lambda(mmap):
    if isinstance(mmap, list):
        java_mmap = jpype.JPackage('jline').util.matrix.MatrixCell(len(mmap))
        for matrix in mmap:
            java_mmap.add(jlineMatrixFromArray(matrix))
    else:
        java_mmap = mmap

    result = jpype.JPackage('jline').api.mam.Mmap_count_lambdaKt.mmap_count_lambda(java_mmap)
    return jlineMatrixToArray(result)


def mmap_isfeasible(mmap):
    if isinstance(mmap, list):
        java_mmap = jpype.JPackage('jline').util.matrix.MatrixCell(len(mmap))
        for matrix in mmap:
            java_mmap.add(jlineMatrixFromArray(matrix))
    else:
        java_mmap = mmap

    return jpype.JPackage('jline').api.mam.Mmap_isfeasibleKt.mmap_isfeasible(java_mmap)


def mmap_mark(mmap, prob):
    if isinstance(mmap, list):
        java_mmap = jpype.JPackage('jline').util.matrix.MatrixCell(len(mmap))
        for matrix in mmap:
            java_mmap.add(jlineMatrixFromArray(matrix))
    else:
        java_mmap = mmap

    result = jpype.JPackage('jline').api.mam.Mmap_markKt.mmap_mark(
        java_mmap,
        jlineMatrixFromArray(prob)
    )

    new_mmap = []
    for i in range(result.length()):
        new_mmap.append(jlineMatrixToArray(result.get(i)))

    return new_mmap


def aph_bernstein(f, order):
    class FunctionWrapper:
        def __init__(self, python_func):
            self.python_func = python_func

        def apply(self, x):
            return float(self.python_func(float(x)))

    function_wrapper = FunctionWrapper(f)

    result = jpype.JPackage('jline').api.mam.Aph_bernsteinKt.aph_bernstein(
        function_wrapper.apply,
        jpype.JInt(order)
    )

    D0 = jlineMatrixToArray(result.getFirst())
    D1 = jlineMatrixToArray(result.getSecond())

    return D0, D1


def map_jointpdf_derivative(map_matrices, iset):
    java_map = jpype.JPackage('jline').util.matrix.MatrixCell(
        jpype.JArray(jpype.JPackage('jline').util.matrix.Matrix)([
            jlineMatrixFromArray(map_matrices[0]),
            jlineMatrixFromArray(map_matrices[1])
        ])
    )

    java_iset = jpype.JArray(jpype.JInt)(len(iset))
    for i, val in enumerate(iset):
        java_iset[i] = int(val)

    return jpype.JPackage('jline').api.mam.Map_jointpdf_derivativeKt.map_jointpdf_derivative(
        java_map, java_iset
    )


def map_ccdf_derivative(map_matrices, i):
    java_map = jpype.JPackage('jline').util.matrix.MatrixCell(
        jpype.JArray(jpype.JPackage('jline').util.matrix.Matrix)([
            jlineMatrixFromArray(map_matrices[0]),
            jlineMatrixFromArray(map_matrices[1])
        ])
    )

    return jpype.JPackage('jline').api.mam.Map_ccdf_derivativeKt.map_ccdf_derivative(
        java_map, jpype.JInt(i)
    )


def qbd_R(B, L, F, iter_max=100000):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Qbd_RKt.qbd_R(
            jlineMatrixFromArray(B),
            jlineMatrixFromArray(L),
            jlineMatrixFromArray(F),
            jpype.JInt(iter_max)
        )
    )


def qbd_R_logred(B, L, F, iter_max=100000):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Qbd_R_logredKt.qbd_R_logred(
            jlineMatrixFromArray(B),
            jlineMatrixFromArray(L),
            jlineMatrixFromArray(F),
            jpype.JInt(iter_max)
        )
    )


def qbd_rg(map_a, map_s, util=None):
    java_map_a = jpype.JPackage('jline').util.matrix.MatrixCell(
        jpype.JArray(jpype.JPackage('jline').util.matrix.Matrix)([
            jlineMatrixFromArray(map_a[0]),
            jlineMatrixFromArray(map_a[1])
        ])
    )

    java_map_s = jpype.JPackage('jline').util.matrix.MatrixCell(
        jpype.JArray(jpype.JPackage('jline').util.matrix.Matrix)([
            jlineMatrixFromArray(map_s[0]),
            jlineMatrixFromArray(map_s[1])
        ])
    )

    if util is not None:
        result = jpype.JPackage('jline').api.mam.Qbd_rgKt.qbd_rg(
            java_map_a, java_map_s, jpype.JDouble(util)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Qbd_rgKt.qbd_rg(
            java_map_a, java_map_s, None
        )

    return {
        'R': jlineMatrixToArray(result.getR()),
        'G': jlineMatrixToArray(result.getG()),
        'B': jlineMatrixToArray(result.getB()),
        'L': jlineMatrixToArray(result.getL()),
        'F': jlineMatrixToArray(result.getF()),
        'U': jlineMatrixToArray(result.getU())
    }


def map_pdf(MAP, points):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Map_pdfKt.map_pdf(
            map_cell, jlineMatrixFromArray(points)
        )
    )


def map_prob(MAP, t):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Map_probKt.map_prob(
            map_cell, jpype.JDouble(t)
        )
    )


def map_joint(MAP1, MAP2):
    if isinstance(MAP1, (list, tuple)) and len(MAP1) == 2:
        D0_1, D1_1 = MAP1
        map_cell_1 = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_1), jlineMatrixFromArray(D1_1)
        )
    else:
        raise ValueError("MAP1 must be a tuple/list of (D0, D1) matrices")

    if isinstance(MAP2, (list, tuple)) and len(MAP2) == 2:
        D0_2, D1_2 = MAP2
        map_cell_2 = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_2), jlineMatrixFromArray(D1_2)
        )
    else:
        raise ValueError("MAP2 must be a tuple/list of (D0, D1) matrices")

    result = jpype.JPackage('jline').api.mam.Map_jointKt.map_joint(
        map_cell_1, map_cell_2
    )

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def map_mixture(alpha, MAPs):
    java_alpha = jpype.JArray(jpype.JDouble)(list(alpha))

    java_maps = jpype.JArray(jpype.JClass("jline.lang.MatrixCell"))(len(MAPs))
    for i, MAP in enumerate(MAPs):
        if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
            D0, D1 = MAP
            java_maps[i] = jpype.JClass("jline.lang.MatrixCell")(
                jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
            )
        else:
            raise ValueError(f"MAP {i} must be a tuple/list of (D0, D1) matrices")

    result = jpype.JPackage('jline').api.mam.Map_mixtureKt.map_mixture(
        java_alpha, java_maps
    )

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def map_mark(MAP, prob):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    result = jpype.JPackage('jline').api.mam.Map_markKt.map_mark(
        map_cell, jlineMatrixFromArray(prob)
    )

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def map_max(MAP1, MAP2):
    if isinstance(MAP1, (list, tuple)) and len(MAP1) == 2:
        D0_1, D1_1 = MAP1
        map_cell_1 = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_1), jlineMatrixFromArray(D1_1)
        )
    else:
        raise ValueError("MAP1 must be a tuple/list of (D0, D1) matrices")

    if isinstance(MAP2, (list, tuple)) and len(MAP2) == 2:
        D0_2, D1_2 = MAP2
        map_cell_2 = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_2), jlineMatrixFromArray(D1_2)
        )
    else:
        raise ValueError("MAP2 must be a tuple/list of (D0, D1) matrices")

    result = jpype.JPackage('jline').api.mam.Map_maxKt.map_max(
        map_cell_1, map_cell_2
    )

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def map_renewal(MAPIN):
    if isinstance(MAPIN, (list, tuple)) and len(MAPIN) == 2:
        D0, D1 = MAPIN
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAPIN must be a tuple/list of (D0, D1) matrices")

    result = jpype.JPackage('jline').api.mam.Map_renewalKt.map_renewal(map_cell)

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def map_sample(MAP, n, seed=None):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    if seed is not None:
        random_obj = jpype.JClass("java.util.Random")(jpype.JLong(seed))
    else:
        random_obj = None

    java_result = jpype.JPackage('jline').api.mam.Map_sampleKt.map_sample(
        map_cell, jpype.JLong(n), random_obj
    )

    return jpype.JArray(jpype.JDouble)(java_result)[:]


def map_stochcomp(MAP):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    result = jpype.JPackage('jline').api.mam.Map_stochcompKt.map_stochcomp(map_cell)

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def map_embedded(MAP):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Map_embeddedKt.map_embedded(map_cell)
    )


def map_infgen(MAP):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Map_infgenKt.map_infgen(map_cell)
    )


def map_piq(MAP):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    return jlineMatrixToArray(
        jpype.JPackage('jline').api.mam.Map_piqKt.map_piq(map_cell)
    )


def map_largemap(D0, D1):
    return bool(
        jpype.JPackage('jline').api.mam.Map_largemapKt.map_largemap(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    )


def map_rand(K):
    result = jpype.JPackage('jline').api.mam.Map_randKt.map_rand(jpype.JInt(K))

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def qbd_mapmap1(MAP_A, MAP_S, mu=None):
    if isinstance(MAP_A, (list, tuple)) and len(MAP_A) == 2:
        D0_A, D1_A = MAP_A
        map_a_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_A), jlineMatrixFromArray(D1_A)
        )
    else:
        raise ValueError("MAP_A must be a tuple/list of (D0, D1) matrices")

    if isinstance(MAP_S, (list, tuple)) and len(MAP_S) == 2:
        D0_S, D1_S = MAP_S
        map_s_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_S), jlineMatrixFromArray(D1_S)
        )
    else:
        raise ValueError("MAP_S must be a tuple/list of (D0, D1) matrices")

    if mu is not None:
        result = jpype.JPackage('jline').api.mam.Qbd_mapmap1Kt.qbd_mapmap1(
            map_a_cell, map_s_cell, jpype.JDouble(mu)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Qbd_mapmap1Kt.qbd_mapmap1(
            map_a_cell, map_s_cell
        )

    return {
        'pi': jlineMatrixToArray(result.getPi()) if hasattr(result, 'getPi') else None,
        'R': jlineMatrixToArray(result.getR()) if hasattr(result, 'getR') else None,
        'utilization': float(result.getUtilization()) if hasattr(result, 'getUtilization') else None,
        'mean_queue_length': float(result.getMeanQueueLength()) if hasattr(result, 'getMeanQueueLength') else None,
        'mean_waiting_time': float(result.getMeanWaitingTime()) if hasattr(result, 'getMeanWaitingTime') else None
    }


def qbd_raprap1(RAP_A, RAP_S, util=None):
    if isinstance(RAP_A, (list, tuple)) and len(RAP_A) == 2:
        D0_A, D1_A = RAP_A
        rap_a_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_A), jlineMatrixFromArray(D1_A)
        )
    else:
        raise ValueError("RAP_A must be a tuple/list of (D0, D1) matrices")

    if isinstance(RAP_S, (list, tuple)) and len(RAP_S) == 2:
        D0_S, D1_S = RAP_S
        rap_s_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_S), jlineMatrixFromArray(D1_S)
        )
    else:
        raise ValueError("RAP_S must be a tuple/list of (D0, D1) matrices")

    if util is not None:
        result = jpype.JPackage('jline').api.mam.Qbd_raprap1Kt.qbd_raprap1(
            rap_a_cell, rap_s_cell, jpype.JDouble(util)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Qbd_raprap1Kt.qbd_raprap1(
            rap_a_cell, rap_s_cell
        )

    return {
        'R': jlineMatrixToArray(result.getR()) if hasattr(result, 'getR') else None,
        'G': jlineMatrixToArray(result.getG()) if hasattr(result, 'getG') else None,
        'pi': jlineMatrixToArray(result.getPi()) if hasattr(result, 'getPi') else None,
        'performance_metrics': result.getPerformanceMetrics() if hasattr(result, 'getPerformanceMetrics') else None
    }


def qbd_bmapbmap1(BMAP_A, BMAP_S):
    if isinstance(BMAP_A, list) and len(BMAP_A) >= 2:
        java_bmap_a = jpype.JClass("jline.lang.MatrixCell")(len(BMAP_A))
        for i, matrix in enumerate(BMAP_A):
            java_bmap_a.set(i, jlineMatrixFromArray(matrix))
    else:
        raise ValueError("BMAP_A must be a list of at least 2 matrices [D0, D1, ...]")

    if isinstance(BMAP_S, list) and len(BMAP_S) >= 2:
        java_bmap_s = jpype.JClass("jline.lang.MatrixCell")(len(BMAP_S))
        for i, matrix in enumerate(BMAP_S):
            java_bmap_s.set(i, jlineMatrixFromArray(matrix))
    else:
        raise ValueError("BMAP_S must be a list of at least 2 matrices [D0, D1, ...]")

    result = jpype.JPackage('jline').api.mam.Qbd_bmapbmap1Kt.qbd_bmapbmap1(
        java_bmap_a, java_bmap_s
    )

    return {
        'R': jlineMatrixToArray(result.getR()) if hasattr(result, 'getR') else None,
        'G': jlineMatrixToArray(result.getG()) if hasattr(result, 'getG') else None,
        'performance_metrics': result.getMetrics() if hasattr(result, 'getMetrics') else None
    }


def qbd_setupdelayoff(MAP_A, MAP_S, setup_time, delay_time, off_time):
    if isinstance(MAP_A, (list, tuple)) and len(MAP_A) == 2:
        D0_A, D1_A = MAP_A
        map_a_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_A), jlineMatrixFromArray(D1_A)
        )
    else:
        raise ValueError("MAP_A must be a tuple/list of (D0, D1) matrices")

    if isinstance(MAP_S, (list, tuple)) and len(MAP_S) == 2:
        D0_S, D1_S = MAP_S
        map_s_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_S), jlineMatrixFromArray(D1_S)
        )
    else:
        raise ValueError("MAP_S must be a tuple/list of (D0, D1) matrices")

    result = jpype.JPackage('jline').api.mam.Qbd_setupdelayoffKt.qbd_setupdelayoff(
        map_a_cell, map_s_cell,
        jpype.JDouble(setup_time), jpype.JDouble(delay_time), jpype.JDouble(off_time)
    )

    return {
        'steady_state': jlineMatrixToArray(result.getSteadyState()) if hasattr(result, 'getSteadyState') else None,
        'performance_metrics': result.getMetrics() if hasattr(result, 'getMetrics') else None
    }


def aph_simplify(a1, T1, a2, T2, p1, p2, pattern):
    result = jpype.JPackage('jline').api.mam.Aph_simplifyKt.aph_simplify(
        jlineMatrixFromArray(a1), jlineMatrixFromArray(T1),
        jlineMatrixFromArray(a2), jlineMatrixFromArray(T2),
        jpype.JDouble(p1), jpype.JDouble(p2), jpype.JInt(pattern)
    )

    return (jlineMatrixToArray(result.getFirst()), jlineMatrixToArray(result.getSecond()))


def aph_rand(n):
    result = jpype.JPackage('jline').api.mam.Aph_randKt.aph_rand(jpype.JInt(n))

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def aph_rand():
    result = jpype.JPackage('jline').api.mam.Aph_randKt.aph_rand()

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def amap2_fit_gamma(mean1, var1, mean2, var2, p):
    result = jpype.JPackage('jline').api.mam.Amap2_fit_gammaKt.amap2_fit_gamma(
        jpype.JDouble(mean1), jpype.JDouble(var1),
        jpype.JDouble(mean2), jpype.JDouble(var2),
        jpype.JDouble(p)
    )

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def mamap2m_fit_gamma_fb_mmap(moments, classes):
    result = jpype.JPackage('jline').api.mam.Mamap2m_fit_gamma_fb_mmapKt.mamap2m_fit_gamma_fb_mmap(
        jlineMatrixFromArray(moments), jpype.JInt(classes)
    )

    return result


def mamap2m_fit_fb_multiclass(data, classes, options=None):
    java_options = None
    if options is not None:
        pass

    if java_options is not None:
        result = jpype.JPackage('jline').api.mam.Mamap2m_fit_fb_multiclassKt.mamap2m_fit_fb_multiclass(
            jlineMatrixFromArray(data), jpype.JInt(classes), java_options
        )
    else:
        result = jpype.JPackage('jline').api.mam.Mamap2m_fit_fb_multiclassKt.mamap2m_fit_fb_multiclass(
            jlineMatrixFromArray(data), jpype.JInt(classes)
        )

    return {
        'fitted_amap': result.getFittedAmap() if hasattr(result, 'getFittedAmap') else None,
        'quality_metrics': result.getQualityMetrics() if hasattr(result, 'getQualityMetrics') else None
    }


def ph_reindex(alpha, T, new_order):
    result = jpype.JPackage('jline').api.mam.Ph_reindexKt.ph_reindex(
        jlineMatrixFromArray(alpha), jlineMatrixFromArray(T), jlineMatrixFromArray(new_order)
    )

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def mmap_pc(MMAP):
    if isinstance(MMAP, list) and len(MMAP) >= 2:
        java_mmap = jpype.JClass("jline.lang.MatrixCell")(len(MMAP))
        for i, matrix in enumerate(MMAP):
            java_mmap.set(i, jlineMatrixFromArray(matrix))
    else:
        raise ValueError("MMAP must be a list of at least 2 matrices [D0, D1, ...]")

    return float(jpype.JPackage('jline').api.mam.Mmap_pcKt.mmap_pc(java_mmap))


def mmap_shorten(MMAP, max_batch_size):
    if isinstance(MMAP, list) and len(MMAP) >= 2:
        java_mmap = jpype.JClass("jline.lang.MatrixCell")(len(MMAP))
        for i, matrix in enumerate(MMAP):
            java_mmap.set(i, jlineMatrixFromArray(matrix))
    else:
        raise ValueError("MMAP must be a list of at least 2 matrices [D0, D1, ...]")

    result = jpype.JPackage('jline').api.mam.Mmap_shortenKt.mmap_shorten(
        java_mmap, jpype.JInt(max_batch_size)
    )

    shortened_mmap = []
    for i in range(result.size()):
        shortened_mmap.append(jlineMatrixToArray(result.get(i)))

    return shortened_mmap


def mmap_sigma2(MMAP):
    if isinstance(MMAP, list) and len(MMAP) >= 2:
        java_mmap = jpype.JClass("jline.lang.MatrixCell")(len(MMAP))
        for i, matrix in enumerate(MMAP):
            java_mmap.set(i, jlineMatrixFromArray(matrix))
    else:
        raise ValueError("MMAP must be a list of at least 2 matrices [D0, D1, ...]")

    return float(jpype.JPackage('jline').api.mam.Mmap_sigma2Kt.mmap_sigma2(java_mmap))


def mmpp2_fit(moments):
    result = jpype.JPackage('jline').api.mam.Mmpp2_fitKt.mmpp2_fit(
        jlineMatrixFromArray(moments)
    )

    return (jlineMatrixToArray(result.getQ()), jlineMatrixToArray(result.getLambda()))


def mmpp2_fit1(data, method='moments'):
    java_method = jpype.JString(method) if isinstance(method, str) else None

    if java_method is not None:
        result = jpype.JPackage('jline').api.mam.Mmpp2_fit1Kt.mmpp2_fit1(
            jlineMatrixFromArray(data), java_method
        )
    else:
        result = jpype.JPackage('jline').api.mam.Mmpp2_fit1Kt.mmpp2_fit1(
            jlineMatrixFromArray(data)
        )

    return (jlineMatrixToArray(result.getQ()), jlineMatrixToArray(result.getLambda()))


def mmpp_rand(states, lambda_range=(0.1, 5.0)):
    result = jpype.JPackage('jline').api.mam.Mmpp_randKt.mmpp_rand(
        jpype.JInt(states), jpype.JDouble(lambda_range[0]), jpype.JDouble(lambda_range[1])
    )

    return (jlineMatrixToArray(result.getQ()), jlineMatrixToArray(result.getLambda()))


def map_count_moment(MAP, k, lag=0):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    return float(jpype.JPackage('jline').api.mam.Map_count_momentKt.map_count_moment(
        map_cell, jpype.JInt(k), jpype.JInt(lag)
    ))


def map_varcount(MAP, t):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    return float(jpype.JPackage('jline').api.mam.Map_varcountKt.map_varcount(
        map_cell, jpype.JDouble(t)
    ))


def map_jointpdf_derivative(MAP, x, y, order_x=1, order_y=1):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    return float(jpype.JPackage('jline').api.mam.Map_jointpdf_derivativeKt.map_jointpdf_derivative(
        map_cell, jpype.JDouble(x), jpype.JDouble(y), jpype.JInt(order_x), jpype.JInt(order_y)
    ))


def map_ccdf_derivative(MAP, x, order=1):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    return float(jpype.JPackage('jline').api.mam.Map_ccdf_derivativeKt.map_ccdf_derivative(
        map_cell, jpype.JDouble(x), jpype.JInt(order)
    ))


def map_kurt(MAP):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    return float(jpype.JPackage('jline').api.mam.Map_kurtKt.map_kurt(map_cell))


def mmap_sigma2_cell(MMAP):
    if isinstance(MMAP, list):
        mmap_cell = jpype.JClass("jline.lang.MatrixCell")()
        for i, matrix in enumerate(MMAP):
            mmap_cell.set(i, jlineMatrixFromArray(matrix))
    else:
        mmap_cell = MMAP

    return float(jpype.JPackage('jline').api.mam.Mmap_sigma2_cellKt.mmap_sigma2_cell(mmap_cell))


def amap2_adjust_gamma(mean1, var1, mean2, var2, p, target_mean, target_var):
    result = jpype.JPackage('jline').api.mam.Amap2_adjust_gammaKt.amap2_adjust_gamma(
        jpype.JDouble(mean1), jpype.JDouble(var1),
        jpype.JDouble(mean2), jpype.JDouble(var2),
        jpype.JDouble(p), jpype.JDouble(target_mean), jpype.JDouble(target_var)
    )

    return {
        'mean1': result.mean1 if hasattr(result, 'mean1') else None,
        'var1': result.var1 if hasattr(result, 'var1') else None,
        'mean2': result.mean2 if hasattr(result, 'mean2') else None,
        'var2': result.var2 if hasattr(result, 'var2') else None,
        'p': result.p if hasattr(result, 'p') else None
    }


def amap2_fitall_gamma(data, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.mam.Amap2_fitall_gammaKt.amap2_fitall_gamma(
            jlineMatrixFromArray(data), java_options
        )
    else:
        result = jpype.JPackage('jline').api.mam.Amap2_fitall_gammaKt.amap2_fitall_gamma(
            jlineMatrixFromArray(data)
        )

    return {
        'parameters': {
            'mean1': result.mean1 if hasattr(result, 'mean1') else None,
            'var1': result.var1 if hasattr(result, 'var1') else None,
            'mean2': result.mean2 if hasattr(result, 'var2') else None,
            'var2': result.var2 if hasattr(result, 'var2') else None,
            'p': result.p if hasattr(result, 'p') else None
        },
        'quality': result.quality if hasattr(result, 'quality') else None,
        'converged': result.converged if hasattr(result, 'converged') else None
    }


def mmpp2_fit_mu00(data, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.mam.Mmpp2_fit_mu00Kt.mmpp2_fit_mu00(
            jlineMatrixFromArray(data), java_options
        )
    else:
        result = jpype.JPackage('jline').api.mam.Mmpp2_fit_mu00Kt.mmpp2_fit_mu00(
            jlineMatrixFromArray(data)
        )

    return float(result)


def mmpp2_fit_mu11(data, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.mam.Mmpp2_fit_mu11Kt.mmpp2_fit_mu11(
            jlineMatrixFromArray(data), java_options
        )
    else:
        result = jpype.JPackage('jline').api.mam.Mmpp2_fit_mu11Kt.mmpp2_fit_mu11(
            jlineMatrixFromArray(data)
        )

    return float(result)


def mmpp2_fit_q01(data, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.mam.Mmpp2_fit_q01Kt.mmpp2_fit_q01(
            jlineMatrixFromArray(data), java_options
        )
    else:
        result = jpype.JPackage('jline').api.mam.Mmpp2_fit_q01Kt.mmpp2_fit_q01(
            jlineMatrixFromArray(data)
        )

    return float(result)


def mmpp2_fit_q10(data, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.mam.Mmpp2_fit_q10Kt.mmpp2_fit_q10(
            jlineMatrixFromArray(data), java_options
        )
    else:
        result = jpype.JPackage('jline').api.mam.Mmpp2_fit_q10Kt.mmpp2_fit_q10(
            jlineMatrixFromArray(data)
        )

    return float(result)


def assess_compression_quality(original_MAP, compressed_MAP, metrics=['mean', 'var', 'acf']):
    if isinstance(original_MAP, (list, tuple)) and len(original_MAP) == 2:
        D0_orig, D1_orig = original_MAP
        orig_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_orig), jlineMatrixFromArray(D1_orig)
        )
    else:
        raise ValueError("original_MAP must be a tuple/list of (D0, D1) matrices")

    if isinstance(compressed_MAP, (list, tuple)) and len(compressed_MAP) == 2:
        D0_comp, D1_comp = compressed_MAP
        comp_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_comp), jlineMatrixFromArray(D1_comp)
        )
    else:
        raise ValueError("compressed_MAP must be a tuple/list of (D0, D1) matrices")

    java_metrics = jpype.JPackage('java.util').ArrayList()
    for metric in metrics:
        java_metrics.add(jpype.JObject(metric, jpype.JClass("java.lang.String")))

    result = jpype.JPackage('jline').api.mam.Assess_compression_qualityKt.assess_compression_quality(
        orig_cell, comp_cell, java_metrics
    )

    return {
        'error_metrics': jlineMatrixToArray(result.errorMetrics) if hasattr(result, 'errorMetrics') else None,
        'relative_errors': jlineMatrixToArray(result.relativeErrors) if hasattr(result, 'relativeErrors') else None,
        'quality_score': result.qualityScore if hasattr(result, 'qualityScore') else None
    }


def compress_adaptive(MAP, target_order, options=None):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.mam.Compress_adaptiveKt.compress_adaptive(
            map_cell, jpype.JInt(target_order), java_options
        )
    else:
        result = jpype.JPackage('jline').api.mam.Compress_adaptiveKt.compress_adaptive(
            map_cell, jpype.JInt(target_order)
        )

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def compress_autocorrelation(MAP, target_order, options=None):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.mam.Compress_autocorrelationKt.compress_autocorrelation(
            map_cell, jpype.JInt(target_order), java_options
        )
    else:
        result = jpype.JPackage('jline').api.mam.Compress_autocorrelationKt.compress_autocorrelation(
            map_cell, jpype.JInt(target_order)
        )

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def compress_spectral(MAP, target_order, options=None):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.mam.Compress_spectralKt.compress_spectral(
            map_cell, jpype.JInt(target_order), java_options
        )
    else:
        result = jpype.JPackage('jline').api.mam.Compress_spectralKt.compress_spectral(
            map_cell, jpype.JInt(target_order)
        )

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def compress_with_quality_control(MAP, target_order, quality_threshold=0.95, options=None):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.mam.Compress_with_quality_controlKt.compress_with_quality_control(
            map_cell, jpype.JInt(target_order), jpype.JDouble(quality_threshold), java_options
        )
    else:
        result = jpype.JPackage('jline').api.mam.Compress_with_quality_controlKt.compress_with_quality_control(
            map_cell, jpype.JInt(target_order), jpype.JDouble(quality_threshold)
        )

    return {
        'compressed_MAP': (jlineMatrixToArray(result.compressedMAP.get(0)), jlineMatrixToArray(result.compressedMAP.get(1))),
        'quality_achieved': result.qualityAchieved if hasattr(result, 'qualityAchieved') else None,
        'meets_threshold': result.meetsThreshold if hasattr(result, 'meetsThreshold') else None
    }


def map_count_moment(MAP, k):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    return float(jpype.JPackage('jline').api.mam.Map_count_momentKt.map_count_moment(
        map_cell, jpype.JInt(k)
    ))


def mamap2m_fit_fb_multiclass(data, classes, options=None):
    java_options = jpype.JObject(options) if options is not None else None

    if java_options is not None:
        result = jpype.JPackage('jline').api.mam.Mamap2m_fit_fb_multiclassKt.mamap2m_fit_fb_multiclass(
            jlineMatrixFromArray(data), jlineMatrixFromArray(classes), java_options
        )
    else:
        result = jpype.JPackage('jline').api.mam.Mamap2m_fit_fb_multiclassKt.mamap2m_fit_fb_multiclass(
            jlineMatrixFromArray(data), jlineMatrixFromArray(classes)
        )

    return {
        'D0': jlineMatrixToArray(result.D0) if hasattr(result, 'D0') else None,
        'D1': jlineMatrixToArray(result.D1) if hasattr(result, 'D1') else None,
        'parameters': result.parameters if hasattr(result, 'parameters') else None,
        'quality': result.quality if hasattr(result, 'quality') else None
    }


def mmpp_rand(n, lambda_rates=None, q_matrix=None):
    if lambda_rates is not None and q_matrix is not None:
        result = jpype.JPackage('jline').api.mam.Mmpp_randKt.mmpp_rand(
            jpype.JInt(n),
            jlineMatrixFromArray(lambda_rates),
            jlineMatrixFromArray(q_matrix)
        )
    elif lambda_rates is not None:
        result = jpype.JPackage('jline').api.mam.Mmpp_randKt.mmpp_rand(
            jpype.JInt(n),
            jlineMatrixFromArray(lambda_rates)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Mmpp_randKt.mmpp_rand(jpype.JInt(n))

    return {
        'lambda': jlineMatrixToArray(result.lambda_rates) if hasattr(result, 'lambda_rates') else None,
        'Q': jlineMatrixToArray(result.Q) if hasattr(result, 'Q') else None
    }


def ph_reindex(alpha, T, new_order):
    result = jpype.JPackage('jline').api.mam.Ph_reindexKt.ph_reindex(
        jlineMatrixFromArray(alpha), jlineMatrixFromArray(T),
        jlineMatrixFromArray(new_order)
    )

    return (jlineMatrixToArray(result.get(0)), jlineMatrixToArray(result.get(1)))


def mmap_maps(MMAP):
    if isinstance(MMAP, list):
        mmap_cell = jpype.JClass("jline.lang.MatrixCell")()
        for i, matrix in enumerate(MMAP):
            mmap_cell.set(i, jlineMatrixFromArray(matrix))
    else:
        mmap_cell = MMAP

    result = jpype.JPackage('jline').api.mam.Mmap_mapsKt.mmap_maps(mmap_cell)

    maps = []
    for i in range(result.size()):
        map_result = result.get(i)
        maps.append((jlineMatrixToArray(map_result.get(0)), jlineMatrixToArray(map_result.get(1))))

    return maps


def mmap_shorten(MMAP, target_length):
    if isinstance(MMAP, list):
        mmap_cell = jpype.JClass("jline.lang.MatrixCell")()
        for i, matrix in enumerate(MMAP):
            mmap_cell.set(i, jlineMatrixFromArray(matrix))
    else:
        mmap_cell = MMAP

    result = jpype.JPackage('jline').api.mam.Mmap_shortenKt.mmap_shorten(
        mmap_cell, jpype.JInt(target_length)
    )

    shortened = []
    for i in range(result.size()):
        shortened.append(jlineMatrixToArray(result.get(i)))

    return shortened


def map_largemap(MAP, threshold=1000):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        raise ValueError("MAP must be a tuple/list of (D0, D1) matrices")

    return bool(jpype.JPackage('jline').api.mam.Map_largemapKt.map_largemap(
        map_cell, jpype.JInt(threshold)
    ))


def map_joint(MAP1, MAP2):
    if isinstance(MAP1, (list, tuple)) and len(MAP1) == 2:
        D0_1, D1_1 = MAP1
        map_cell1 = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_1), jlineMatrixFromArray(D1_1)
        )
    else:
        map_cell1 = MAP1

    if isinstance(MAP2, (list, tuple)) and len(MAP2) == 2:
        D0_2, D1_2 = MAP2
        map_cell2 = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0_2), jlineMatrixFromArray(D1_2)
        )
    else:
        map_cell2 = MAP2

    result = jpype.JPackage('jline').api.mam.Map_jointKt.map_joint(
        map_cell1, map_cell2
    )

    return result


def map_jointpdf_derivative(MAP, t1, t2):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        map_cell = MAP

    result = jpype.JPackage('jline').api.mam.Map_jointpdf_derivativeKt.map_jointpdf_derivative(
        map_cell, jpype.JDouble(t1), jpype.JDouble(t2)
    )

    return float(result)


def map_prob(MAP, t):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        result = jpype.JPackage('jline').api.mam.Map_probKt.map_prob(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1), jpype.JDouble(t)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Map_probKt.map_prob(
            MAP, jpype.JDouble(t)
        )

    return jlineMatrixToArray(result)


def map_mixture(alpha, MAPs):
    alpha_array = jpype.JArray(jpype.JDouble)(alpha)

    map_cells = jpype.JArray(jpype.JClass("jline.lang.MatrixCell"))(len(MAPs))
    for i, MAP in enumerate(MAPs):
        if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
            D0, D1 = MAP
            map_cells[i] = jpype.JClass("jline.lang.MatrixCell")(
                jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
            )
        else:
            map_cells[i] = MAP

    result = jpype.JPackage('jline').api.mam.Map_mixtureKt.map_mixture(
        alpha_array, map_cells
    )

    return result


def map_pdf(MAP, points):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        result = jpype.JPackage('jline').api.mam.Map_pdfKt.map_pdf(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1),
            jlineMatrixFromArray(points)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Map_pdfKt.map_pdf(
            MAP, jlineMatrixFromArray(points)
        )

    return jlineMatrixToArray(result)


def map_gamma(MAP):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        result = jpype.JPackage('jline').api.mam.Map_gammaKt.map_gamma(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Map_gammaKt.map_gamma(MAP)

    return float(result)


def mmap_sigma2(MMAP):
    result = jpype.JPackage('jline').api.mam.Mmap_sigma2Kt.mmap_sigma2(MMAP)
    return float(result)


def mmap_normalize(MMAP):
    result = jpype.JPackage('jline').api.mam.Mmap_normalizeKt.mmap_normalize(MMAP)
    return result


def mmap_count_mean(MMAP, t):
    if isinstance(t, (list, tuple, np.ndarray)):
        t_array = jpype.JArray(jpype.JDouble)(t)
        result = jpype.JPackage('jline').api.mam.Mmap_count_meanKt.mmap_count_mean(
            MMAP, t_array
        )
        return np.array([float(x) for x in result])
    else:
        result = jpype.JPackage('jline').api.mam.Mmap_count_meanKt.mmap_count_mean(
            MMAP, jpype.JDouble(t)
        )
        return float(result)


def mmap_count_var(MMAP, t):
    if isinstance(t, (list, tuple, np.ndarray)):
        t_array = jpype.JArray(jpype.JDouble)(t)
        result = jpype.JPackage('jline').api.mam.Mmap_count_varKt.mmap_count_var(
            MMAP, t_array
        )
        return np.array([float(x) for x in result])
    else:
        result = jpype.JPackage('jline').api.mam.Mmap_count_varKt.mmap_count_var(
            MMAP, jpype.JDouble(t)
        )
        return float(result)


def qbd_R(A0, A1, A2):
    A0_matrix = jlineMatrixFromArray(A0)
    A1_matrix = jlineMatrixFromArray(A1)
    A2_matrix = jlineMatrixFromArray(A2)

    result = jpype.JPackage('jline').api.mam.Qbd_RKt.qbd_R(
        A0_matrix, A1_matrix, A2_matrix
    )

    return jlineMatrixToArray(result)


def qbd_G(A0, A1, A2):
    A0_matrix = jlineMatrixFromArray(A0)
    A1_matrix = jlineMatrixFromArray(A1)
    A2_matrix = jlineMatrixFromArray(A2)

    result = jpype.JPackage('jline').api.mam.Qbd_GKt.qbd_G(
        A0_matrix, A1_matrix, A2_matrix
    )

    return jlineMatrixToArray(result)


def ph_fit(data, max_phases=10):
    data_array = jpype.JArray(jpype.JDouble)(data)

    result = jpype.JPackage('jline').api.mam.Ph_fitKt.ph_fit(
        data_array, jpype.JInt(max_phases)
    )

    alpha = jlineMatrixToArray(result.getFirst())
    T = jlineMatrixToArray(result.getSecond())

    return alpha, T


def ph_mean(alpha, T):
    alpha_matrix = jlineMatrixFromArray(alpha)
    T_matrix = jlineMatrixFromArray(T)

    result = jpype.JPackage('jline').api.mam.Ph_meanKt.ph_mean(
        alpha_matrix, T_matrix
    )

    return float(result)


def ph_var(alpha, T):
    alpha_matrix = jlineMatrixFromArray(alpha)
    T_matrix = jlineMatrixFromArray(T)

    result = jpype.JPackage('jline').api.mam.Ph_varKt.ph_var(
        alpha_matrix, T_matrix
    )

    return float(result)


def ph_pdf(alpha, T, points):
    alpha_matrix = jlineMatrixFromArray(alpha)
    T_matrix = jlineMatrixFromArray(T)
    points_matrix = jlineMatrixFromArray(points)

    result = jpype.JPackage('jline').api.mam.Ph_pdfKt.ph_pdf(
        alpha_matrix, T_matrix, points_matrix
    )

    return jlineMatrixToArray(result)


def ph_cdf(alpha, T, points):
    alpha_matrix = jlineMatrixFromArray(alpha)
    T_matrix = jlineMatrixFromArray(T)
    points_matrix = jlineMatrixFromArray(points)

    result = jpype.JPackage('jline').api.mam.Ph_cdfKt.ph_cdf(
        alpha_matrix, T_matrix, points_matrix
    )

    return jlineMatrixToArray(result)


def aph_bernstein(alpha, T, order):
    alpha_matrix = jlineMatrixFromArray(alpha)
    T_matrix = jlineMatrixFromArray(T)

    result = jpype.JPackage('jline').api.mam.Aph_bernsteinKt.aph_bernstein(
        alpha_matrix, T_matrix, jpype.JInt(order)
    )

    return jlineMatrixToArray(result)


def mmap_scale(MMAP, factor):
    result = jpype.JPackage('jline').api.mam.Mmap_scaleKt.mmap_scale(
        MMAP, jpype.JDouble(factor)
    )

    return result


def mmap_hide(MMAP, types):
    types_array = jpype.JArray(jpype.JInt)(types)

    result = jpype.JPackage('jline').api.mam.Mmap_hideKt.mmap_hide(
        MMAP, types_array
    )

    return result


def qbd_psif(A0, A1, A2, B, options=None):
    A0_matrix = jlineMatrixFromArray(A0)
    A1_matrix = jlineMatrixFromArray(A1)
    A2_matrix = jlineMatrixFromArray(A2)
    B_matrix = jlineMatrixFromArray(B)

    if options is not None:
        result = jpype.JPackage('jline').api.mam.Qbd_psifKt.qbd_psif(
            A0_matrix, A1_matrix, A2_matrix, B_matrix,
            jpype.JObject(options)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Qbd_psifKt.qbd_psif(
            A0_matrix, A1_matrix, A2_matrix, B_matrix
        )

    return jlineMatrixToArray(result)


def qbd_psi(A0, A1, A2, options=None):
    A0_matrix = jlineMatrixFromArray(A0)
    A1_matrix = jlineMatrixFromArray(A1)
    A2_matrix = jlineMatrixFromArray(A2)

    if options is not None:
        result = jpype.JPackage('jline').api.mam.Qbd_psiKt.qbd_psi(
            A0_matrix, A1_matrix, A2_matrix, jpype.JObject(options)
        )
    else:
        result = jpype.JPackage('jline').api.mam.Qbd_psiKt.qbd_psi(
            A0_matrix, A1_matrix, A2_matrix
        )

    return jlineMatrixToArray(result)


def aph2_check_feasibility(M1, M2, M3):
    result = jpype.JPackage('jline').api.mam.Aph2_check_feasibilityKt.aph2_check_feasibility(
        jpype.JDouble(M1), jpype.JDouble(M2), jpype.JDouble(M3)
    )

    return bool(result)


def aph2_canonical(a1, t11, a2, t22):
    result = jpype.JPackage('jline').api.mam.Aph2_canonicalKt.aph2_canonical(
        jpype.JDouble(a1), jpype.JDouble(t11),
        jpype.JDouble(a2), jpype.JDouble(t22)
    )

    alpha = jlineMatrixToArray(result.getFirst())
    T = jlineMatrixToArray(result.getSecond())

    return alpha, T


def map_cdf_derivative(MAP, x, order=1):
    if isinstance(MAP, (list, tuple)) and len(MAP) == 2:
        D0, D1 = MAP
        map_cell = jpype.JClass("jline.lang.MatrixCell")(
            jlineMatrixFromArray(D0), jlineMatrixFromArray(D1)
        )
    else:
        map_cell = MAP

    result = jpype.JPackage('jline').api.mam.Map_cdf_derivativeKt.map_cdf_derivative(
        map_cell, jpype.JDouble(x), jpype.JInt(order)
    )

    return float(result)


def map_rand_moment(K, target_mean=1.0, target_var=1.0):
    result = jpype.JPackage('jline').api.mam.Map_rand_momentKt.map_rand_moment(
        jpype.JInt(K), jpype.JDouble(target_mean), jpype.JDouble(target_var)
    )

    return result


def mmap_compress(MMAP, target_states, method='spectral'):
    result = jpype.JPackage('jline').api.mam.Mmap_compressKt.mmap_compress(
        MMAP, jpype.JInt(target_states), jpype.JString(method)
    )

    return result


def qbd_solve(A0, A1, A2):
    from .. import jlineMatrixFromArray, jlineMatrixToArray

    java_A0 = jlineMatrixFromArray(A0)
    java_A1 = jlineMatrixFromArray(A1)
    java_A2 = jlineMatrixFromArray(A2)

    java_result = jpype.JPackage('jline').api.mam.Qbd_solveKt.qbd_solve(
        java_A0, java_A1, java_A2
    )

    pi0 = jlineMatrixToArray(java_result.getPi0())
    R = jlineMatrixToArray(java_result.getR())

    return pi0, R

