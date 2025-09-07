
import jpype
import numpy as np
from line_solver import jlineMatrixToArray, jlineMatrixFromArray


def trace_mean(trace):
    java_trace = jpype.JArray(jpype.JDouble)(trace)

    result = jpype.JPackage('jline').api.trace.Trace_meanKt.trace_mean(java_trace)
    return float(result)


def trace_var(trace):
    java_trace = jpype.JArray(jpype.JDouble)(trace)

    result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_var(java_trace)
    return float(result)


def mtrace_mean(trace, ntypes, type_array):
    java_trace = jpype.JArray(jpype.JDouble)(trace)
    java_type_array = jpype.JArray(jpype.JInt)(type_array)

    result = jpype.JPackage('jline').api.trace.Mtrace_meanKt.mtrace_mean(
        java_trace, jpype.JInt(ntypes), java_type_array
    )

    return jlineMatrixToArray(result)


def trace_scv(trace):
    java_trace = jpype.JArray(jpype.JDouble)(trace)
    result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_scv(java_trace)
    return float(result)


def trace_acf(trace, lags=None):
    java_trace = jpype.JArray(jpype.JDouble)(trace)

    if lags is None:
        lags = [1]
    java_lags = jpype.JArray(jpype.JInt)(lags)

    result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_acf(java_trace, java_lags)
    return np.array([float(x) for x in result])


def trace_gamma(trace, limit=1000):
    java_trace = jpype.JArray(jpype.JDouble)(trace)
    result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_gamma(java_trace, jpype.JInt(limit))
    return (float(result[0]), float(result[1]), float(result[2]))


def trace_iat2counts(trace, scale):
    java_trace = jpype.JArray(jpype.JDouble)(trace)
    result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_iat2counts(java_trace, jpype.JDouble(scale))
    return np.array([int(x) for x in result])


def trace_idi(trace, kset, option=None, n=1):
    java_trace = jpype.JArray(jpype.JDouble)(trace)
    java_kset = jpype.JArray(jpype.JInt)(kset)

    if option is None:
        result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_idi(java_trace, java_kset)
    else:
        result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_idi(
            java_trace, java_kset, jpype.JString(option), jpype.JInt(n)
        )

    idi_values = np.array([float(x) for x in result.getFirst()])
    support_values = np.array([int(x) for x in result.getSecond()])
    return (idi_values, support_values)


def trace_idc(trace):
    java_trace = jpype.JArray(jpype.JDouble)(trace)
    result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_idc(java_trace)
    return float(result)


def trace_pmf(data):
    java_data = jpype.JArray(jpype.JInt)([int(x) for x in data])
    result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_pmf(java_data)

    pmf_values = np.array([float(x) for x in result.getFirst()])
    unique_values = np.array([int(x) for x in result.getSecond()])
    return (pmf_values, unique_values)


def trace_shuffle(trace):
    java_trace = jpype.JArray(jpype.JDouble)(trace)
    result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_shuffle(java_trace)
    return np.array([float(x) for x in result])


def trace_bicov(trace, grid):
    java_trace = jpype.JArray(jpype.JDouble)(trace)
    java_grid = jpype.JArray(jpype.JInt)(grid)

    result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_bicov(java_trace, java_grid)

    bicov_values = np.array([float(x) for x in result.getFirst()])
    lag_combinations = []
    for lag_array in result.getSecond():
        lag_combinations.append([int(x) for x in lag_array])

    return (bicov_values, lag_combinations)


def trace_iat2bins(trace, scale):
    java_trace = jpype.JArray(jpype.JDouble)(trace)
    result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_iat2bins(java_trace, jpype.JDouble(scale))

    counts = np.array([int(x) for x in result.getFirst()])
    bin_membership = np.array([int(x) for x in result.getSecond()])
    return (counts, bin_membership)


def trace_joint(trace, lag, order):
    java_trace = jpype.JArray(jpype.JDouble)(trace)
    java_lag = jpype.JArray(jpype.JInt)(lag)
    java_order = jpype.JArray(jpype.JInt)(order)

    result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_joint(java_trace, java_lag, java_order)
    return float(result)


def trace_summary(trace):
    java_trace = jpype.JArray(jpype.JDouble)(trace)
    result = jpype.JPackage('jline').api.trace.Trace_varKt.trace_summary(java_trace)

    result_array = [float(x) for x in result]

    return {
        'mean': result_array[0],
        'scv': result_array[1],
        'mad': result_array[2],
        'skew': result_array[3],
        'kurt': result_array[4],
        'q25': result_array[5],
        'q50': result_array[6],
        'q75': result_array[7],
        'p95': result_array[8],
        'min': result_array[9],
        'max': result_array[10],
        'iqr': result_array[11],
        'acf1': result_array[12],
        'acf2': result_array[13],
        'acf3': result_array[14],
        'acf4': result_array[15],
        'idc_scv_ratio': result_array[16]
    }


def trace_cdf(trace, x_values=None):
    import numpy as np

    trace = np.array(trace).flatten()

    if x_values is None:
        x_values = np.unique(np.sort(trace))
    else:
        x_values = np.array(x_values)

    n = len(trace)
    cdf_values = np.zeros_like(x_values, dtype=float)

    for i, x in enumerate(x_values):
        cdf_values[i] = np.sum(trace <= x) / n

    return {
        'x': x_values,
        'y': cdf_values
    }


def trace_pdf(trace, x_values=None, bandwidth=None):
    import numpy as np
    from scipy.stats import gaussian_kde

    trace = np.array(trace).flatten()

    trace = trace[np.isfinite(trace)]

    if len(trace) == 0:
        raise ValueError("No finite values in trace data")

    if x_values is None:
        x_min, x_max = np.min(trace), np.max(trace)
        x_range = x_max - x_min
        x_values = np.linspace(x_min - 0.1*x_range, x_max + 0.1*x_range, 100)
    else:
        x_values = np.array(x_values)

    kde = gaussian_kde(trace)
    if bandwidth is not None:
        kde.set_bandwidth(bandwidth)

    pdf_values = kde(x_values)

    return {
        'x': x_values,
        'y': pdf_values
    }


def trace_hist(trace, bins=None):
    import numpy as np

    trace = np.array(trace).flatten()
    trace = trace[np.isfinite(trace)]

    if bins is None:
        bins = 'auto'

    counts, bin_edges = np.histogram(trace, bins=bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    return {
        'counts': counts,
        'bin_edges': bin_edges,
        'bin_centers': bin_centers
    }


def trace_moment(trace, k):
    import numpy as np

    trace = np.array(trace).flatten()
    trace = trace[np.isfinite(trace)]

    if len(trace) == 0:
        return 0.0

    return float(np.mean(trace ** k))


def trace_skew(trace):
    import numpy as np
    from scipy.stats import skew

    trace = np.array(trace).flatten()
    trace = trace[np.isfinite(trace)]

    if len(trace) < 3:
        return 0.0

    return float(skew(trace))


def trace_kurt(trace):
    import numpy as np
    from scipy.stats import kurtosis

    trace = np.array(trace).flatten()
    trace = trace[np.isfinite(trace)]

    if len(trace) < 4:
        return 0.0

    return float(kurtosis(trace, fisher=True))


def trace_fit_gamma(trace):
    import numpy as np

    trace = np.array(trace).flatten()
    trace = trace[np.isfinite(trace) & (trace > 0)]

    if len(trace) == 0:
        raise ValueError("No positive finite values in trace data")

    sample_mean = np.mean(trace)
    sample_var = np.var(trace, ddof=1)

    if sample_var <= 0:
        raise ValueError("Sample variance must be positive for gamma fitting")

    scale = sample_var / sample_mean
    shape = sample_mean / scale
    rate = 1.0 / scale

    return {
        'shape': float(shape),
        'scale': float(scale),
        'rate': float(rate),
        'mean': float(sample_mean),
        'var': float(sample_var)
    }


def mtrace_corr(trace, ntypes, type_array, lags=None):
    import numpy as np

    trace = np.array(trace).flatten()
    type_array = np.array(type_array).flatten()

    if len(trace) != len(type_array):
        raise ValueError("trace and type_array must have same length")

    if lags is None:
        lags = [0, 1, 2, 3, 4]
    lags = np.array(lags)

    nlags = len(lags)
    correlations = np.zeros((ntypes, ntypes, nlags))

    for i in range(ntypes):
        for j in range(ntypes):
            for k, lag in enumerate(lags):
                if lag == 0:
                    mask_i = (type_array == i)
                    mask_j = (type_array == j)
                    if np.sum(mask_i) > 0 and np.sum(mask_j) > 0:
                        if i == j:
                            correlations[i, j, k] = 1.0
                        else:
                            correlations[i, j, k] = np.corrcoef(
                                trace[mask_i], trace[mask_j]
                            )[0, 1] if len(trace[mask_i]) > 1 and len(trace[mask_j]) > 1 else 0.0
                else:
                    if len(trace) > lag:
                        trace1 = trace[:-lag]
                        trace2 = trace[lag:]
                        type1 = type_array[:-lag]
                        type2 = type_array[lag:]

                        mask1 = (type1 == i)
                        mask2 = (type2 == j)

                        if np.sum(mask1) > 0 and np.sum(mask2) > 0:
                            correlations[i, j, k] = np.corrcoef(
                                trace1[mask1], trace2[mask2]
                            )[0, 1] if len(trace1[mask1]) > 1 and len(trace2[mask2]) > 1 else 0.0

    return {
        'correlations': correlations,
        'lags': lags
    }


def mtrace_cov(trace, ntypes, type_array, lags=None):
    import numpy as np

    trace = np.array(trace).flatten()
    type_array = np.array(type_array).flatten()

    if len(trace) != len(type_array):
        raise ValueError("trace and type_array must have same length")

    if lags is None:
        lags = [0, 1, 2, 3, 4]
    lags = np.array(lags)

    nlags = len(lags)
    covariances = np.zeros((ntypes, ntypes, nlags))

    for i in range(ntypes):
        for j in range(ntypes):
            for k, lag in enumerate(lags):
                if lag == 0:
                    mask_i = (type_array == i)
                    mask_j = (type_array == j)
                    if np.sum(mask_i) > 0 and np.sum(mask_j) > 0:
                        if i == j:
                            covariances[i, j, k] = np.var(trace[mask_i], ddof=1)
                        else:
                            covariances[i, j, k] = np.cov(
                                trace[mask_i], trace[mask_j], ddof=1
                            )[0, 1] if len(trace[mask_i]) > 1 and len(trace[mask_j]) > 1 else 0.0
                else:
                    if len(trace) > lag:
                        trace1 = trace[:-lag]
                        trace2 = trace[lag:]
                        type1 = type_array[:-lag]
                        type2 = type_array[lag:]

                        mask1 = (type1 == i)
                        mask2 = (type2 == j)

                        if np.sum(mask1) > 0 and np.sum(mask2) > 0:
                            covariances[i, j, k] = np.cov(
                                trace1[mask1], trace2[mask2], ddof=1
                            )[0, 1] if len(trace1[mask1]) > 1 and len(trace2[mask2]) > 1 else 0.0

    return {
        'covariances': covariances,
        'lags': lags
    }