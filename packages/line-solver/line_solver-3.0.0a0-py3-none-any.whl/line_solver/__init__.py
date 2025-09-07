
import jpype
import pandas as pd

from urllib.request import urlretrieve
import jpype.imports
from jpype import startJVM, shutdownJVM, java
import numpy as np
import os, sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, dir_path)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.precision', 4)


class GlobalImport:
    def __enter__(self):
        return self

    def __call__(self):
        import inspect
        self.collector = inspect.getargvalues(inspect.getouterframes(inspect.currentframe())[1].frame).locals

    def __exit__(self, *args):
        try:
            globals().update(self.collector)
        except:
            pass


def lineRootFolder():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def jlineStart():
    with GlobalImport() as gi:
        package_dir = os.path.dirname(os.path.realpath(__file__))
        python_dir = os.path.dirname(package_dir)
        root_dir = os.path.dirname(python_dir)
        common_dir = os.path.join(root_dir, 'common')
        jar_file_path = os.path.join(common_dir, "jline.jar")

        if not os.path.exists(common_dir):
            os.makedirs(common_dir)

        if not os.path.isfile(jar_file_path):
            print("Downloading LINE solver JAR, please wait... ", end='')
            urlretrieve("https://sourceforge.net/p/line-solver/code/ci/master/tree/matlab/jline.jar?format=raw",
                        jar_file_path)
            print("done.")
        jpype.startJVM()
        #jpype.startJVM(jpype.getDefaultJVMPath(),
        #               "-agentlib:jdwp=transport=dt_socket,server=n,suspend=y,address=5005")
        jpype.addClassPath(jar_file_path)
        from jline import GlobalConstants
        from jline.lang import Chain, Element, Ensemble, Metric
        from jline.lang import FeatureSet, FiniteCapacityRegion
        from jline.lang import Model, NetworkAttribute, NetworkElement, Event
        from jline.lang import ItemSet, NodeAttribute, OutputStrategy, ServiceBinding
        from jline.lang.layered import ActivityPrecedence, CacheTask, FunctionTask, LayeredNetworkElement
        from jline.lang.layered import LayeredNetworkStruct, ItemEntry, Host
        from jline.lang.processes import ContinuousDistribution, Coxian
        from jline.lang.processes import DiscreteDistribution, DiscreteSampler, Distribution
        from jline.lang.processes import Markovian
        from jline.lang.nodes import Logger, Place
        from jline.lang.nodes import StatefulNode, Station, Transition
        from jline.lang.processes import MarkedMAP, MarkedMMPP
        from jline.lang.sections import Buffer, CacheClassSwitcher, ClassSwitcher, Dispatcher
        from jline.lang.sections import Forker, InfiniteServer, InputSection, Joiner, OutputSection, PreemptiveServer
        from jline.lang.sections import RandomSource, Section, Server, ServiceSection, ServiceTunnel, SharedServer
        from jline.lang.sections import StatefulClassSwitcher, StatelessClassSwitcher
        from jline.lang.state import State
        from jline.solvers import EnsembleSolver, NetworkAvgTable, NetworkSolver, SolverAvgHandles, SolverTranHandles
        gi()
        jpype.JPackage('jline').util.Maths.setMatlabRandomSeed(True)


def jlineMapMatrixToArray(mapmatrix):
    d = dict(mapmatrix)
    for i in range(len(d)):
        d[i] = jlineMatrixToArray(d[i])
    return d

def jlineMatrixCellToArray(matrixcell):
    d = {}
    for i in range(matrixcell.size()):
        matrix = matrixcell.get(i)
        if matrix is not None:
            d[i] = jlineMatrixToArray(matrix)
        else:
            d[i] = None
    return d


def jlineFromDistribution(distrib):
    python_distrib = None
    if distrib is not None:
        distrib_name = distrib.getName()
        if distrib_name == 'APH':
            python_distrib = APH(distrib)
        elif distrib_name == 'Cox2':
            python_distrib = Cox2(distrib)
        elif distrib_name == 'Det':
            python_distrib = Det(distrib)
        elif distrib_name == 'Disabled':
            python_distrib = Disabled()
        elif distrib_name == 'Erlang':
            python_distrib = Erlang(distrib)
        elif distrib_name == 'Exp':
            python_distrib = Exp(distrib)
        elif distrib_name == 'Gamma':
            python_distrib = Gamma(distrib)
        elif distrib_name == 'HyperExp':
            python_distrib = HyperExp(distrib)
        elif distrib_name == 'Immediate':
            python_distrib = Immediate()
        elif distrib_name == 'Lognormal':
            python_distrib = Lognormal(distrib)
        elif distrib_name == 'MAP':
            python_distrib = MAP(distrib)
        elif distrib_name == 'Pareto':
            python_distrib = Pareto(distrib)
        elif distrib_name == 'PH':
            python_distrib = PH(distrib)
        elif distrib_name == 'Replayer':
            python_distrib = Replayer(distrib)
        elif distrib_name == 'Uniform':
            python_distrib = Uniform(distrib)
        elif distrib_name == 'Weibull':
            python_distrib = Weibull(distrib)
        elif distrib_name == 'Binomial':
            python_distrib = Binomial(distrib)
        elif distrib_name == 'DiscreteSampler':
            python_distrib = DiscreteSampler(distrib)
        elif distrib_name == 'Geometric':
            python_distrib = Geometric(distrib)
        elif distrib_name == 'Poisson':
            python_distrib = Poisson(distrib)
        elif distrib_name == 'Zipf':
            python_distrib = Zipf(distrib)
    return python_distrib


def jlineMatrixToArray(matrix):
    if matrix is None:
        return None
    else:
        return np.array(list(matrix.toArray2D()))


def jlineMatrixFromArray(array):
    if isinstance(array, list):
        array = np.array(array)
    if len(np.shape(array)) > 1:
        ret = jpype.JPackage('jline').util.matrix.Matrix(np.size(array, 0), np.size(array, 1), array.size)
        for i in range(np.size(array, 0)):
            for j in range(np.size(array, 1)):
                ret.set(i, j, array[i][j])
    else:
        ret = jpype.JPackage('jline').util.matrix.Matrix(1, np.size(array, 0), array.size)
        for i in range(np.size(array, 0)):
            ret.set(0, i, array[i])
    return ret


def jlineMatrixZeros(rows, cols):
    return jlineMatrixFromArray([[0.0] * cols for _ in range(rows)])


def jlineMatrixSingleton(value):
    return jlineMatrixFromArray([value])


def is_interactive():
    import __main__ as main
    return not hasattr(main, '__file__')


def lineDefaults(solverName='Solver'):
    from .solvers import SolverOptions
    from .constants import SolverType

    if solverName == 'Solver':
        return SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.MVA)
    else:
        solver_type_map = {
            'MVA': jpype.JPackage('jline').lang.constant.SolverType.MVA,
            'CTMC': jpype.JPackage('jline').lang.constant.SolverType.CTMC,
            'JMT': jpype.JPackage('jline').lang.constant.SolverType.JMT,
            'SSA': jpype.JPackage('jline').lang.constant.SolverType.SSA,
            'MAM': jpype.JPackage('jline').lang.constant.SolverType.MAM,
            'FLUID': jpype.JPackage('jline').lang.constant.SolverType.FLUID,
            'NC': jpype.JPackage('jline').lang.constant.SolverType.NC,
            'AUTO': jpype.JPackage('jline').lang.constant.SolverType.AUTO,
            'ENV': jpype.JPackage('jline').lang.constant.SolverType.ENV,
            'LQNS': jpype.JPackage('jline').lang.constant.SolverType.LQNS,
            'LN': jpype.JPackage('jline').lang.constant.SolverType.LN,
            'QNS': jpype.JPackage('jline').lang.constant.SolverType.QNS
        }

        solver_type = solver_type_map.get(solverName.upper(), jpype.JPackage('jline').lang.constant.SolverType.MVA)
        return SolverOptions(solver_type)


jlineStart()
from .api import *
from .constants import *
from .lang import *
from .utils import *
from .solvers import *
from .distributions import *
from .layered import *
from .gallery import *
