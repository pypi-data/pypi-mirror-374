
import sys

import jpype
import jpype.imports
import numpy as np

from line_solver import jlineMatrixFromArray, jlineMatrixToArray

class NamedParam:
    def __init__(self, *args):
        if len(args) == 1:
            self.obj = args[0]
        else:
            self.name = args[0]
            self.value = args[1]

    def getName(self):
        return self.name

    def getValue(self):
        return self.value

    get_name = getName
    get_value = getValue

class Distribution:

    def __init__(self):
        pass

    def evalCDF(self, x):
        return self.obj.evalCDF(x)

    def evalLST(self, x):
        return self.obj.evalLST(x)

    def getName(self):
        return self.obj.getName()

    def getParam(self, id):
        nparam = NamedParam(self.obj.getParam(id))
        return nparam

    def getMean(self):
        return self.obj.getMean()

    def getRate(self):
        return self.obj.getRate()

    def getSCV(self):
        return self.obj.getSCV()

    def getVar(self):
        return self.obj.getVar()

    def getSkew(self):
        return self.obj.getSkew()

    def getSupport(self):
        return self.obj.getSupport()

    def isContinuous(self):
        return self.obj.isContinuous()

    def isDisabled(self):
        return self.obj.isDisabled()

    def isDiscrete(self):
        return self.obj.isDiscrete()

    def isImmediate(self):
        return self.obj.isImmediate()

    def sample(self, *args):
        if len(args) == 1:
            n = args[0]
            return jlineMatrixToArray(self.obj.sample(n))
        else:
            n = args[0]
            seed = args[1]

    get_name = getName
    get_param = getParam
    get_mean = getMean
    get_rate = getRate
    get_scv = getSCV
    get_var = getVar
    get_skew = getSkew
    get_support = getSupport

class ContinuousDistribution(Distribution):
    def __init__(self):
        super().__init__()

class DiscreteDistribution(Distribution):
    def __init__(self):
        super().__init__()

class MarkovianDistribution(Distribution):
    def __init__(self):
        super().__init__()

    def getD0(self):
        return self.obj.getD0()

    def getD1(self):
        return self.obj.getD1()

    def getMu(self):
        return self.obj.getMu()

    def getNumberOfPhases(self):
        return self.obj.getNumberOfPhases()

    def getPH(self):
        return self.obj.getPH()

    def getPhi(self):
        return self.obj.getPhi()

    def getInitProb(self):
        return self.obj.getInitProb()

    get_d0 = getD0
    get_d1 = getD1
    get_mu = getMu
    get_number_of_phases = getNumberOfPhases
    get_ph = getPH
    get_phi = getPhi
    get_init_prob = getInitProb

class APH(MarkovianDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            alpha = args[0]
            subgen = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.APH(jlineMatrixFromArray(alpha),
                                                                      jlineMatrixFromArray(subgen))

    @staticmethod
    def fitMeanAndSCV(mean, scv):
        return APH(jpype.JPackage('jline').lang.processes.APH.fitMeanAndSCV(mean, scv))

    fit_mean_and_scv = fitMeanAndSCV

class Bernoulli(DiscreteDistribution):
    def __init__(self, *args):
        super().__init__()
        prob = args[0]
        self.obj = jpype.JPackage('jline').lang.processes.Bernoulli(prob)

class Binomial(DiscreteDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            prob = args[0]
            n = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.Binomial(prob, n)

class Coxian(MarkovianDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            mu = args[0]
            phi = args[1]

            if hasattr(phi, 'toArray'):
                phi_array = phi.toArray()
            else:
                phi_array = phi

            if hasattr(mu, 'obj'):
                mu_matrix = mu.obj
            else:
                mu_matrix = jlineMatrixFromArray(mu)

            if hasattr(phi, 'obj'):
                phi_matrix = phi.obj
            else:
                phi_matrix = jlineMatrixFromArray(phi)

            if len(phi_array.shape) == 2:
                phi_flat = phi_array.flatten()
            else:
                phi_flat = phi_array

            if phi_flat[-1] != 1.0:
                print("Invalid Coxian exit probabilities. The last element must be 1.0.", file=sys.stderr)
            elif max(phi_flat) > 1.0 or min(phi_flat) < 0.0:
                print("Invalid Coxian exit probabilities. Some values are not in [0,1].", file=sys.stderr)
            else:
                self.obj = jpype.JPackage('jline').lang.processes.Coxian(mu_matrix, phi_matrix)

    def fitMeanAndSCV(mean, scv):
        return Cox2(jpype.JPackage('jline').lang.processes.Cox2.fitMeanAndSCV(mean, scv))

    fit_mean_and_scv = fitMeanAndSCV

class Cox2(MarkovianDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            mu1 = args[0]
            mu2 = args[1]
            phi1 = args[2]
            self.obj = jpype.JPackage('jline').lang.processes.Cox2(mu1, mu2, phi1)

    def fitMeanAndSCV(mean, scv):
        return Cox2(jpype.JPackage('jline').lang.processes.Cox2.fitMeanAndSCV(mean, scv))

    fit_mean_and_scv = fitMeanAndSCV


class Det(Distribution):
    def __init__(self, value):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.processes.Det(value)


class Disabled(Distribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 0:
            self.obj = jpype.JPackage('jline').lang.processes.Disabled()
        else:
            self.obj = args[0]

    @staticmethod
    def getInstance():
        return Disabled(jpype.JPackage('jline').lang.processes.Disabled.getInstance())

    get_instance = getInstance

class DiscreteSampler(DiscreteDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            if isinstance(args[0], DiscreteDistribution):
                self.obj = args[0]
            else:
                p = args[0]
                if isinstance(p, list):
                    p = jlineMatrixFromArray(p)
                elif hasattr(p, 'obj'):
                    p = p.obj
                self.obj = jpype.JPackage('jline').lang.processes.DiscreteSampler(p)
        else:
            p = args[0]
            x = args[1]
            if isinstance(p, list):
                p = jlineMatrixFromArray(p)
            elif hasattr(p, 'obj'):
                p = p.obj
            if isinstance(x, list):
                x = jlineMatrixFromArray(x)
            elif hasattr(x, 'obj'):
                x = x.obj
            self.obj = jpype.JPackage('jline').lang.processes.DiscreteSampler(p, x)

class DiscreteUniform(DiscreteDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            minVal = args[0]
            maxVal = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.DiscreteUniform(minVal, maxVal)

class Exp(MarkovianDistribution):

    def __init__(self, *args):
        super().__init__()

        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, (int, float, np.integer, np.floating)):
                self.obj = jpype.JPackage('jline').lang.processes.Exp.fitRate(arg)
            else:
                self.obj = arg
        else:
            raise ValueError("Exp constructor accepts a single rate (float) or a pre-constructed object.")

    def fitRate(rate):
        return Exp(jpype.JPackage('jline').lang.processes.Exp.fitRate(rate))

    fit_rate = fitRate

    def fitMean(mean):
        return Exp(jpype.JPackage('jline').lang.processes.Exp.fitMean(mean))

    fit_mean = fitMean



class Erlang(MarkovianDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            rate = args[0]
            nphases = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.Erlang(rate, nphases)

    def fitMeanAndSCV(mean, scv):
        return Erlang(jpype.JPackage('jline').lang.processes.Erlang.fitMeanAndSCV(mean, scv))

    fit_mean_and_scv = fitMeanAndSCV

    def fitMeanAndOrder(mean, order):
        return Erlang(jpype.JPackage('jline').lang.processes.Erlang.fitMeanAndOrder(mean, order))

    fit_mean_and_order = fitMeanAndOrder


class Gamma(ContinuousDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            shape = args[0]
            scale = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.Gamma(shape, scale)

    def fitMeanAndSCV(mean, scv):
        return Gamma(jpype.JPackage('jline').lang.processes.Gamma.fitMeanAndSCV(mean, scv))

    fit_mean_and_scv = fitMeanAndSCV


class Geometric(DiscreteDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            if isinstance(args[0], jpype.JPackage('jline').lang.processes.DiscreteDistribution):
                self.obj = args[0]
            else:
                prob = args[0]
                self.obj = jpype.JPackage('jline').lang.processes.Geometric(prob)


class HyperExp(MarkovianDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            if hasattr(args[0], '__module__') and 'jpype' in args[0].__module__:
                self.obj = args[0]
            elif hasattr(args[0], '__class__') and 'jline.lang.processes.HyperExp' in str(args[0].__class__):
                self.obj = args[0]
            else:
                self.obj = jpype.JPackage('jline').lang.processes.HyperExp(0.5, args[0])
        elif len(args) == 2:
            p = args[0]
            lambda_rate = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.HyperExp(p, lambda_rate)
        else:
            p = args[0]
            lambda1 = args[1]
            lambda2 = args[2]
            self.obj = jpype.JPackage('jline').lang.processes.HyperExp(p, lambda1, lambda2)

    @staticmethod
    def fitMeanAndSCV(mean, scv):
        return HyperExp(jpype.JPackage('jline').lang.processes.HyperExp.fitMeanAndSCV(mean, scv))

    fit_mean_and_scv = fitMeanAndSCV

    @staticmethod
    def fitMeanAndSCVBalanced(mean, scv):
        return HyperExp(jpype.JPackage('jline').lang.processes.HyperExp.fitMeanAndSCVBalanced(mean, scv))

    fit_mean_and_scv_balanced = fitMeanAndSCVBalanced


class Immediate(Distribution):
    def __init__(self):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.processes.Immediate()


class Lognormal(ContinuousDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            mu = args[0]
            sigma = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.Lognormal(mu, sigma)

    def fitMeanAndSCV(mean, scv):
        return Lognormal(jpype.JPackage('jline').lang.processes.Lognormal.fitMeanAndSCV(mean, scv))

    fit_mean_and_scv = fitMeanAndSCV


class MAP(MarkovianDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            D0 = args[0]
            D1 = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.MAP(jlineMatrixFromArray(D0), jlineMatrixFromArray(D1))

    def toPH(self):
        self.obj.toPH()


class MMPP2(MarkovianDistribution):
    def __init__(self, lambda0, lambda1, sigma0, sigma1):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.processes.MMPP2(lambda0, lambda1, sigma0, sigma1)


class PH(MarkovianDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            alpha = args[0]
            subgen = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.PH(jlineMatrixFromArray(alpha),
                                                                     jlineMatrixFromArray(subgen))


class Pareto(ContinuousDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            shape = args[0]
            scale = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.Pareto(shape, scale)

    def fitMeanAndSCV(mean, scv):
        return Pareto(jpype.JPackage('jline').lang.processes.Pareto.fitMeanAndSCV(mean, scv))

    fit_mean_and_scv = fitMeanAndSCV


class Poisson(DiscreteDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            rate = args[0]
            self.obj = jpype.JPackage('jline').lang.processes.Poisson(rate)


class Replayer(Distribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            if isinstance(args[0], Distribution):
                self.obj = args[0]
            else:
                filename = args[0]
                self.obj = jpype.JPackage('jline').lang.processes.Replayer(filename)

    def fitAPH(self):
        return APH(self.obj.fitAPH())

    fit_aph = fitAPH


class Uniform(ContinuousDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            minVal = args[0]
            maxVal = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.Uniform(minVal, maxVal)


class Weibull(ContinuousDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            shape = args[0]
            scale = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.Weibull(shape, scale)

    def fitMeanAndSCV(mean, scv):
        return Weibull(jpype.JPackage('jline').lang.processes.Weibull.fitMeanAndSCV(mean, scv))

    fit_mean_and_scv = fitMeanAndSCV


class Zipf(DiscreteDistribution):
    def __init__(self, *args):
        super().__init__()
        if len(args) == 1:
            self.obj = args[0]
        else:
            s = args[0]
            n = args[1]
            self.obj = jpype.JPackage('jline').lang.processes.Zipf(s, n)

