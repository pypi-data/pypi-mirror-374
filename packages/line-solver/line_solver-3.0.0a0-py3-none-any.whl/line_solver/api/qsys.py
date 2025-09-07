
import jpype
import numpy as np
from line_solver import jlineMatrixToArray, jlineMatrixFromArray


def qsys_mm1(lambda_val, mu):
    result = jpype.JPackage('jline').api.qsys.Qsys_mm1Kt.qsys_mm1(
        jpype.JDouble(lambda_val), jpype.JDouble(mu)
    )

    return {
        'L': result.L,
        'Lq': result.Lq,
        'W': result.W,
        'Wq': result.Wq,
        'rho': result.rho
    }


def qsys_mmk(lambda_val, mu, k):
    result = jpype.JPackage('jline').api.qsys.Qsys_mmkKt.qsys_mmk(
        jpype.JDouble(lambda_val), jpype.JDouble(mu), jpype.JInt(k)
    )

    return {
        'L': result.L,
        'Lq': result.Lq,
        'W': result.W,
        'Wq': result.Wq,
        'rho': result.rho,
        'P0': result.P0
    }


def qsys_gm1(lambda_val, mu, sigma_s_squared):
    result = jpype.JPackage('jline').api.qsys.Qsys_gm1Kt.qsys_gm1(
        jpype.JDouble(lambda_val), jpype.JDouble(mu), jpype.JDouble(sigma_s_squared)
    )

    return {
        'L': result.L,
        'Lq': result.Lq,
        'W': result.W,
        'Wq': result.Wq,
        'rho': result.rho
    }


def qsys_mg1(lambda_val, mu, sigma_s_squared):
    result = jpype.JPackage('jline').api.qsys.Qsys_mg1Kt.qsys_mg1(
        jpype.JDouble(lambda_val), jpype.JDouble(mu), jpype.JDouble(sigma_s_squared)
    )

    return {
        'L': result.L,
        'Lq': result.Lq,
        'W': result.W,
        'Wq': result.Wq,
        'rho': result.rho
    }


def qsys_gig1_approx_lin(lambda_val, mu, ca_squared, cs_squared):
    result = jpype.JPackage('jline').api.qsys.Qsys_gig1_approx_linKt.qsys_gig1_approx_lin(
        jpype.JDouble(lambda_val), jpype.JDouble(mu),
        jpype.JDouble(ca_squared), jpype.JDouble(cs_squared)
    )

    return {
        'L': result.L,
        'Lq': result.Lq,
        'W': result.W,
        'Wq': result.Wq,
        'rho': result.rho
    }


def qsys_gig1_approx_kk(lambda_val, mu, ca_squared, cs_squared):
    result = jpype.JPackage('jline').api.qsys.Qsys_gig1_approx_kkKt.qsys_gig1_approx_kk(
        jpype.JDouble(lambda_val), jpype.JDouble(mu),
        jpype.JDouble(ca_squared), jpype.JDouble(cs_squared)
    )

    return {
        'L': result.L,
        'Lq': result.Lq,
        'W': result.W,
        'Wq': result.Wq,
        'rho': result.rho
    }


def qsys_gig1_approx_whitt(lambda_val, mu, ca_squared, cs_squared):
    result = jpype.JPackage('jline').api.qsys.Qsys_gig1_approx_whittKt.qsys_gig1_approx_whitt(
        jpype.JDouble(lambda_val), jpype.JDouble(mu),
        jpype.JDouble(ca_squared), jpype.JDouble(cs_squared)
    )

    return {
        'L': result.L,
        'Lq': result.Lq,
        'W': result.W,
        'Wq': result.Wq,
        'rho': result.rho
    }

def qsys_gig1_approx_allencunneen(lambda_val, mu, ca_squared, cs_squared):
    result = jpype.JPackage('jline').api.qsys.Qsys_gig1_approx_allencunneenKt.qsys_gig1_approx_allencunneen(
        jpype.JDouble(lambda_val), jpype.JDouble(mu),
        jpype.JDouble(ca_squared), jpype.JDouble(cs_squared)
    )

    return {
        'W': result.W,
        'rho': result.rho
    }


def qsys_gig1_approx_heyman(lambda_val, mu, ca_squared, cs_squared):
    result = jpype.JPackage('jline').api.qsys.Qsys_gig1_approx_heymanKt.qsys_gig1_approx_heyman(
        jpype.JDouble(lambda_val), jpype.JDouble(mu),
        jpype.JDouble(ca_squared), jpype.JDouble(cs_squared)
    )

    return {
        'W': result.W,
        'rho': result.rho
    }


def qsys_gig1_approx_kobayashi(lambda_val, mu, ca_squared, cs_squared):
    result = jpype.JPackage('jline').api.qsys.Qsys_gig1_approx_kobayashiKt.qsys_gig1_approx_kobayashi(
        jpype.JDouble(lambda_val), jpype.JDouble(mu),
        jpype.JDouble(ca_squared), jpype.JDouble(cs_squared)
    )

    return {
        'W': result.W,
        'rho': result.rho
    }


def qsys_gig1_approx_marchal(lambda_val, mu, ca_squared, cs_squared):
    result = jpype.JPackage('jline').api.qsys.Qsys_gig1_approx_marchalKt.qsys_gig1_approx_marchal(
        jpype.JDouble(lambda_val), jpype.JDouble(mu),
        jpype.JDouble(ca_squared), jpype.JDouble(cs_squared)
    )

    return {
        'W': result.W,
        'rho': result.rho
    }


def qsys_gig1_ubnd_kingman(lambda_val, mu, ca_squared, cs_squared):
    result = jpype.JPackage('jline').api.qsys.Qsys_gig1_ubnd_kingmanKt.qsys_gig1_ubnd_kingman(
        jpype.JDouble(lambda_val), jpype.JDouble(mu),
        jpype.JDouble(ca_squared), jpype.JDouble(cs_squared)
    )

    return {
        'W': result.W,
        'rho': result.rho
    }


def qsys_gigk_approx(lambda_val, mu, ca_squared, cs_squared, k):
    result = jpype.JPackage('jline').api.qsys.Qsys_gigk_approxKt.qsys_gigk_approx(
        jpype.JDouble(lambda_val), jpype.JDouble(mu),
        jpype.JDouble(ca_squared), jpype.JDouble(cs_squared), jpype.JInt(k)
    )

    return {
        'W': result.W,
        'rho': result.rho
    }


def qsys_gigk_approx_kingman(lambda_val, mu, ca_squared, cs_squared, k):
    result = jpype.JPackage('jline').api.qsys.Qsys_gigk_approx_kingmanKt.qsys_gigk_approx_kingman(
        jpype.JDouble(lambda_val), jpype.JDouble(mu),
        jpype.JDouble(ca_squared), jpype.JDouble(cs_squared), jpype.JInt(k)
    )

    return {
        'W': result.W,
        'rho': result.rho
    }


def qsys_gig1_approx_klb(lambda_val, mu, ca_squared, cs_squared):
    result = jpype.JPackage('jline').api.qsys.Qsys_gig1_approx_klbKt.qsys_gig1_approx_klb(
        jpype.JDouble(lambda_val), jpype.JDouble(mu),
        jpype.JDouble(ca_squared), jpype.JDouble(cs_squared)
    )

    return {
        'L': result.L,
        'Lq': result.Lq,
        'W': result.W,
        'Wq': result.Wq,
        'rho': result.rho
    }

