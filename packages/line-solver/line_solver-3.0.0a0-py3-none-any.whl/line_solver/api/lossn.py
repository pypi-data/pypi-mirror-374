
import numpy as np
import jpype
from line_solver import jlineMatrixToArray, jlineMatrixFromArray


def lossn_erlangfp(nu_vec, amat, c_vec):
    nu_matrix = jlineMatrixFromArray(nu_vec)
    a_matrix = jlineMatrixFromArray(amat)
    c_matrix = jlineMatrixFromArray(c_vec)

    result = jpype.JPackage('jline').api.lossn.Lossn_erlangfpKt.lossn_erlangfp(
        nu_matrix, a_matrix, c_matrix
    )

    qlen = jlineMatrixToArray(result.qLen)
    loss_prob = jlineMatrixToArray(result.lossProb)
    block_prob = jlineMatrixToArray(result.blockProb)
    niter = result.niter

    return qlen, loss_prob, block_prob, niter
