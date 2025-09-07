
import os

import jpype
import jpype.imports
import numpy as np
import pandas as pd
from jpype import JArray

from line_solver import VerboseLevel, SolverType, jlineMatrixToArray, GlobalConstants, jlineMatrixFromArray, \
    jlineMapMatrixToArray, jlineMatrixCellToArray


class SampleResult:
    def __init__(self, java_result):
        self.handle = java_result.handle if hasattr(java_result, 'handle') else ""
        self.t = jlineMatrixToArray(java_result.t) if hasattr(java_result, 't') and java_result.t is not None else None
        self.state = java_result.state if hasattr(java_result, 'state') else None
        self.event = self._parse_events(java_result) if hasattr(java_result, 'event') else []
        self.isaggregate = java_result.isAggregate if hasattr(java_result, 'isAggregate') else False
        self.nodeIndex = java_result.nodeIndex if hasattr(java_result, 'nodeIndex') else None
        self.numSamples = java_result.numSamples if hasattr(java_result, 'numSamples') else 0

    def _parse_events(self, java_result):
        events = []
        if hasattr(java_result, 'event') and java_result.event is not None:
            if hasattr(java_result.event, '__iter__') and not hasattr(java_result.event, 'getNumRows'):
                for event_info in java_result.event:
                    event_obj = EventInfo()
                    event_obj.node = event_info.node if hasattr(event_info, 'node') else 0
                    event_obj.jobclass = event_info.jobclass if hasattr(event_info, 'jobclass') else 0
                    event_obj.t = event_info.t if hasattr(event_info, 't') else 0.0
                    event_obj.event = getattr(event_info, 'event', None)
                    events.append(event_obj)
            else:
                event_matrix = jlineMatrixToArray(java_result.event)
                if event_matrix is not None and len(event_matrix) > 0:
                    for row in event_matrix:
                        if len(row) >= 3:
                            event_obj = EventInfo()
                            event_obj.t = float(row[0])
                            event_obj.node = int(row[1])
                            event_obj.jobclass = 0

                            event_type_int = int(row[2])
                            if event_type_int == 1:
                                event_obj.event = "ARV"
                            elif event_type_int == 2:
                                event_obj.event = "DEP"
                            elif event_type_int == 3:
                                event_obj.event = "PHASE"
                            else:
                                event_obj.event = None

                            events.append(event_obj)
        return events


class EventInfo:
    def __init__(self):
        self.node = 0
        self.jobclass = 0
        self.t = 0.0
        self.event = None


class DistributionResult:
    def __init__(self, java_result):
        self.java_result = java_result
        self.num_stations = java_result.numStations if hasattr(java_result, 'numStations') else 0
        self.num_classes = java_result.numClasses if hasattr(java_result, 'numClasses') else 0
        self.distribution_type = java_result.distributionType if hasattr(java_result, 'distributionType') else ""
        self.is_transient = java_result.isTransient if hasattr(java_result, 'isTransient') else False
        self.runtime = java_result.runtime if hasattr(java_result, 'runtime') else 0.0
        self.time_points = jlineMatrixToArray(java_result.timePoints) if hasattr(java_result, 'timePoints') and java_result.timePoints is not None else None

        self.cdf_data = self._parse_cdf_data(java_result)

    def _parse_cdf_data(self, java_result):
        """Parse CDF data from Java result into Python format"""
        if not hasattr(java_result, 'cdfData') or java_result.cdfData is None:
            return []

        try:
            cdf_data = []
            for i in range(self.num_stations):
                station_cdfs = []
                for j in range(self.num_classes):
                    if java_result.hasCdf(i, j):
                        cdf_matrix = java_result.getCdf(i, j)
                        cdf_array = jlineMatrixToArray(cdf_matrix)
                        station_cdfs.append(cdf_array)
                    else:
                        station_cdfs.append(None)
                cdf_data.append(station_cdfs)
            return cdf_data
        except Exception as e:
            print(f"Error parsing CDF data: {e}")
            return []

    def get_cdf(self, station, job_class):
        """Get CDF for a specific station and job class"""
        if station < 0 or station >= self.num_stations or job_class < 0 or job_class >= self.num_classes:
            return None

        if self.cdf_data and station < len(self.cdf_data) and job_class < len(self.cdf_data[station]):
            return self.cdf_data[station][job_class]
        return None

    def has_cdf(self, station, job_class):
        """Check if CDF data is available for a specific station and job class"""
        if hasattr(self.java_result, 'hasCdf'):
            return self.java_result.hasCdf(station, job_class)
        return False

class ProbabilityResult:
    def __init__(self, java_result):
        self.java_result = java_result
        self.probability = jlineMatrixToArray(java_result.probability) if hasattr(java_result, 'probability') and java_result.probability is not None else None
        self.log_normalizing_constant = java_result.logNormalizingConstant if hasattr(java_result, 'logNormalizingConstant') else 0.0
        self.is_aggregated = java_result.isAggregated if hasattr(java_result, 'isAggregated') else False
        self.node_index = java_result.nodeIndex if hasattr(java_result, 'nodeIndex') else None
        self.state = jlineMatrixToArray(java_result.state) if hasattr(java_result, 'state') and java_result.state is not None else None

    def get_probability(self):
        """Get the probability matrix as a numpy array"""
        return self.probability

    def get_log_normalizing_constant(self):
        """Get the logarithm of the normalizing constant"""
        return self.log_normalizing_constant

    def is_aggregated_result(self):
        """Check if this is an aggregated result"""
        return self.is_aggregated

    def get_node_index(self):
        """Get the node index (for node-specific results)"""
        return self.node_index

    def get_state(self):
        """Get the state specification"""
        return self.state



class Solver:
    @staticmethod
    def defaultOptions():
        options = {
            'keep': False,
            'verbose': VerboseLevel.STD,
            'cutoff': 10,
            'seed': 23000,
            'iter_max': 200,
            'samples': 10000,
            'method': 'default'
        }
        return options

    def __init__(self, options, *args, **kwargs):
        self.solveropt = options
        self._verbose_silent = False
        self._table_silent = False

        for key, value in kwargs.items():
            self._process_solver_option(key, value)

        if len(args) >= 1:
            ctr = 0
            while ctr < len(args):
                if args[ctr] == 'cutoff':
                    self.solveropt.obj.cutoff(args[ctr + 1])
                    ctr += 2
                elif args[ctr] == 'method':
                    self.solveropt.obj.method(args[ctr + 1])
                    ctr += 2
                elif args[ctr] == 'exact':
                    self.solveropt.obj.method('exact')
                    ctr += 1
                elif args[ctr] == 'keep':
                    self.solveropt.obj.keep(args[ctr + 1])
                    ctr += 2
                elif args[ctr] == 'seed':
                    self.solveropt.obj.seed(args[ctr + 1])
                    ctr += 2
                elif args[ctr] == 'samples':
                    self.solveropt.obj.samples(args[ctr + 1])
                    ctr += 2
                elif args[ctr] == 'timespan':
                    self.solveropt.obj.timespan = JArray(jpype.JDouble)(args[ctr + 1])
                    ctr += 2
                elif args[ctr] == 'timestep':
                    self.solveropt.obj.timestep = jpype.JDouble(args[ctr + 1]) if args[ctr + 1] is not None else None
                    ctr += 2
                elif args[ctr] == 'verbose':
                    self._process_verbose_option(args[ctr + 1])
                    ctr += 2
                else:
                    ctr += 1

    def _process_solver_option(self, key, value):
        """Process a single solver option from keyword arguments"""
        if key == 'cutoff':
            if hasattr(value, '__iter__') and not isinstance(value, str):
                from line_solver import jlineMatrixFromArray
                self.solveropt.obj.cutoff(jlineMatrixFromArray(value))
            else:
                self.solveropt.obj.cutoff(value)
        elif key == 'method':
            self.solveropt.obj.method(str(value))
        elif key == 'keep':
            self.solveropt.obj.keep(bool(value))
        elif key == 'seed':
            self.solveropt.obj.seed(int(value))
        elif key == 'samples':
            self.solveropt.obj.samples(int(value))
        elif key == 'timespan':
            if hasattr(value, '__iter__'):
                self.solveropt.obj.timespan = JArray(jpype.JDouble)(value)
            else:
                self.solveropt.obj.timespan = value
        elif key == 'timestep':
            self.solveropt.obj.timestep = jpype.JDouble(value) if value is not None else None
        elif key == 'verbose':
            self._process_verbose_option(value)
        elif key == 'force':
            self.solveropt.obj.force(bool(value))
        elif key == 'cache':
            self.solveropt.obj.cache = bool(value)
        elif key == 'hide_immediate':
            self.solveropt.obj.hide_immediate = bool(value)
        elif key == 'iter_max':
            self.solveropt.obj.iter_max = int(value)
        elif key == 'iter_tol':
            self.solveropt.obj.iter_tol = float(value)
        elif key == 'tol':
            self.solveropt.obj.tol = float(value)
        elif key == 'lang':
            self.solveropt.obj.lang = str(value)
        elif key == 'remote':
            self.solveropt.obj.remote = bool(value)
        elif key == 'remote_endpoint':
            self.solveropt.obj.remote_endpoint = str(value)
        elif key == 'stiff':
            self.solveropt.obj.stiff = bool(value)
        elif key == 'init_sol':
            if hasattr(value, '__iter__'):
                from line_solver import jlineMatrixFromArray
                self.solveropt.obj.init_sol = jlineMatrixFromArray(value)
            else:
                self.solveropt.obj.init_sol = value
        else:
            if hasattr(self.solveropt.obj, key):
                try:
                    setattr(self.solveropt.obj, key, value)
                except (AttributeError, TypeError):
                    pass

    def _process_verbose_option(self, value):
        """Process verbose option handling both old and new formats"""
        if isinstance(value, bool):
            if value:
                self.solveropt.obj.verbose(jpype.JPackage('jline').VerboseLevel.STD)
            else:
                self.solveropt.obj.verbose(jpype.JPackage('jline').VerboseLevel.SILENT)
                self._verbose_silent = True
        else:
            if value is False:
                self.solveropt.obj.verbose(
                    jpype.JPackage('jline').VerboseLevel.SILENT)
                self._verbose_silent = True
            elif value is True:
                self.solveropt.obj.verbose(
                    jpype.JPackage('jline').VerboseLevel.STD)
                self._verbose_silent = False
            elif value == VerboseLevel.SILENT:
                self.solveropt.obj.verbose(
                    jpype.JPackage('jline').VerboseLevel.SILENT)
                self._verbose_silent = True
                self._table_silent = True
            elif value == VerboseLevel.STD:
                self.solveropt.obj.verbose(jpype.JPackage('jline').VerboseLevel.STD)
            elif value == VerboseLevel.DEBUG:
                self.solveropt.obj.verbose(jpype.JPackage('jline').VerboseLevel.DEBUG)

    def getName(self):
        return self.obj.getName()

    @staticmethod
    def defaultOptions():
        """Returns default solver options for the base Solver class."""
        java_options = jpype.JPackage('jline').solvers.mva.SolverMVA.defaultOptions()
        python_options = SolverOptions.__new__(SolverOptions)
        python_options.obj = java_options
        return python_options

    def supports(self, model):
        if hasattr(self, 'obj') and hasattr(self.obj, 'supports'):
            return self.obj.supports(model.obj if hasattr(model, 'obj') else model)
        return True

    get_name = getName

class EnsembleSolver(Solver):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        pass

    def getNumberOfModels(self):
        return self.obj.getNumberOfModels()

    def printEnsembleAvgTables(self):
        self.obj.printEnsembleAvgTables()

    def numberOfModels(self):
        """Kotlin-style alias for getNumberOfModels"""
        return self.getNumberOfModels()

    get_number_of_models = getNumberOfModels


class NetworkSolver(Solver):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        pass

    def getAvgNodeTable(self):
        table = self.obj.getAvgNodeTable()


        QLen = np.array(list(table.getQLen()))
        Util = np.array(list(table.getUtil()))
        RespT = np.array(list(table.getRespT()))
        ResidT = np.array(list(table.getResidT()))
        ArvR = np.array(list(table.getArvR()))
        Tput = np.array(list(table.getTput()))

        cols = ['QLen', 'Util', 'RespT', 'ResidT', 'ArvR', 'Tput']
        nodes = list(table.getNodeNames())
        nodenames = []
        for i in range(len(nodes)):
            nodenames.append(str(nodes[i]))
        jobclasses = list(table.getClassNames())

        classnames = []
        for i in range(len(jobclasses)):
            classnames.append(str(jobclasses[i]))
        AvgTable = pd.DataFrame(np.concatenate([[QLen, Util, RespT, ResidT, ArvR, Tput]]).T, columns=cols)
        tokeep = ~(AvgTable <= 0.0).all(axis=1)
        AvgTable.insert(0, "JobClass", classnames)
        AvgTable.insert(0, "Node", nodenames)
        AvgTable = AvgTable.loc[tokeep]
        if not self._table_silent:
            print(AvgTable)

        return AvgTable

    avg_node_table = getAvgNodeTable

    def getAvgChainTable(self):
        table = self.obj.getAvgChainTable()

        QLen = np.array(list(table.getQLen()))
        Util = np.array(list(table.getUtil()))
        RespT = np.array(list(table.getRespT()))
        ResidT = np.array(list(table.getResidT()))
        ArvR = np.array(list(table.getArvR()))
        Tput = np.array(list(table.getTput()))

        cols = ['QLen', 'Util', 'RespT', 'ResidT', 'ArvR', 'Tput']
        stations = list(table.getStationNames())
        statnames = []
        for i in range(len(stations)):
            statnames.append(str(stations[i]))
        jobchains = list(table.getChainNames())
        chainnames = []
        for i in range(len(jobchains)):
            chainnames.append(str(jobchains[i]))
        AvgChainTable = pd.DataFrame(np.concatenate([[QLen, Util, RespT, ResidT, ArvR, Tput]]).T, columns=cols)
        tokeep = ~(AvgChainTable <= 0.0).all(axis=1)
        AvgChainTable.insert(0, "Chain", chainnames)
        AvgChainTable.insert(0, "Station", statnames)
        AvgChainTable = AvgChainTable.loc[tokeep]
        if not self._table_silent:
            print(AvgChainTable)

        return AvgChainTable

    avg_chain_table = getAvgChainTable

    def getAvgNodeChainTable(self):
        table = self.obj.getAvgNodeChainTable()

        QLen = np.array(list(table.getQLen()))
        Util = np.array(list(table.getUtil()))
        RespT = np.array(list(table.getRespT()))
        ResidT = np.array(list(table.getResidT()))
        ArvR = np.array(list(table.getArvR()))
        Tput = np.array(list(table.getTput()))

        cols = ['QLen', 'Util', 'RespT', 'ResidT', 'ArvR', 'Tput']
        nodes = list(table.getNodeNames())
        nodenames = []
        for i in range(len(nodes)):
            nodenames.append(str(nodes[i]))
        jobchains = list(table.getChainNames())
        chainnames = []
        for i in range(len(jobchains)):
            chainnames.append(str(jobchains[i]))
        AvgChainTable = pd.DataFrame(np.concatenate([[QLen, Util, RespT, ResidT, ArvR, Tput]]).T, columns=cols)
        tokeep = ~(AvgChainTable <= 0.0).all(axis=1)
        AvgChainTable.insert(0, "Chain", chainnames)
        AvgChainTable.insert(0, "Node", nodenames)
        AvgChainTable = AvgChainTable.loc[tokeep]
        if not self._table_silent:
            print(AvgChainTable)

        return AvgChainTable

    avg_node_chain_table = getAvgNodeChainTable

    def getAvgTable(self):
        table = self.obj.getAvgTable()


        QLen = np.array(list(table.getQLen()))
        Util = np.array(list(table.getUtil()))
        RespT = np.array(list(table.getRespT()))
        ResidT = np.array(list(table.getResidT()))
        ArvR = np.array(list(table.getArvR()))
        Tput = np.array(list(table.getTput()))

        cols = ['QLen', 'Util', 'RespT', 'ResidT', 'ArvR', 'Tput']

        stations = list(table.getStationNames())
        statnames = []
        for i in range(len(stations)):
            statnames.append(str(stations[i]))
        jobclasses = list(table.getClassNames())
        classnames = []
        for i in range(len(jobclasses)):
            classnames.append(str(jobclasses[i]))
        AvgTable = pd.DataFrame(np.concatenate([[QLen, Util, RespT, ResidT, ArvR, Tput]]).T, columns=cols)
        tokeep = ~(AvgTable <= 0.0).all(axis=1)
        AvgTable.insert(0, "JobClass", classnames)
        AvgTable.insert(0, "Station", statnames)
        AvgTable = AvgTable.loc[tokeep]
        if not self._table_silent:
            print(AvgTable)

        return AvgTable

    avg_table = getAvgTable

    def getAvgSysTable(self):
        table = self.obj.getAvgSysTable()

        SysRespT = np.array(list(table.getSysRespT()))
        SysTput = np.array(list(table.getSysTput()))

        cols = ['SysRespT', 'SysTput']
        jobchains = list(table.getChainNames())
        chains = []
        for i in range(len(jobchains)):
            chains.append(str(jobchains[i]))
        jobinchains = list(table.getInChainNames())
        inchains = []
        for i in range(len(jobinchains)):
            inchains.append(str(jobinchains[i]))
        AvgSysTable = pd.DataFrame(np.concatenate([[SysRespT, SysTput]]).T, columns=cols)
        tokeep = ~(AvgSysTable <= 0.0).all(axis=1)
        AvgSysTable.insert(0, "JobClasses", inchains)
        AvgSysTable.insert(0, "Chain", chains)
        AvgSysTable = AvgSysTable.loc[tokeep]
        if not self._table_silent:
            print(AvgSysTable)
        return AvgSysTable

    avg_sys_table = getAvgSysTable

    def getAvgTput(self):
        Tput = jlineMatrixToArray(self.obj.getAvgTput())
        if not self._table_silent:
                print(Tput)
        return Tput

    avg_tput = getAvgTput

    def getAvgResidT(self):
        ResidT = jlineMatrixToArray(self.obj.getAvgResidT())
        if not self._table_silent:
            print(ResidT)
        return ResidT

    avg_residt = getAvgResidT

    def getAvgArvR(self):
        ArvR = jlineMatrixToArray(self.obj.getAvgArvR())
        if not self._table_silent:
            print(ArvR)
        return ArvR

    avg_arv_r = getAvgArvR

    def getAvgUtil(self):
        Util = jlineMatrixToArray(self.obj.getAvgUtil())
        if not self._table_silent:
            print(Util)
        return Util

    avg_util = getAvgUtil

    def getAvgQLen(self):
        QLen = jlineMatrixToArray(self.obj.getAvgQLen())
        if not self._table_silent:
            print(QLen)
        return QLen

    avg_q_len = getAvgQLen

    def getAvgRespT(self):
        RespT = jlineMatrixToArray(self.obj.getAvgRespT())
        if not self._table_silent:
            print(RespT)
        return RespT

    avg_respt = getAvgRespT

    def getAvgWaitT(self):
        WaitT = jlineMatrixToArray(self.obj.getAvgWaitT())
        if not self._table_silent:
            print(WaitT)
        return WaitT

    avg_waitt = getAvgWaitT

    def getAvgSysTput(self):
        SysTput = jlineMatrixToArray(self.obj.getAvgSysTput())
        if not self._table_silent:
            print(SysTput)
        return SysTput

    avg_sys_tput = getAvgSysTput

    def getAvgSysRespT(self):
        SysRespT = jlineMatrixToArray(self.obj.getAvgSysRespT())
        if not self._table_silent:
            print(SysRespT)
        return SysRespT

    avg_sys_respt = getAvgSysRespT

    def getAvg(self):
        result = self.obj.getAvg()
        if hasattr(result, 'toArray2D'):
            avgRet = jlineMatrixToArray(result)
        else:
            avgRet = jlineMatrixToArray(result.QN)
        if not self._table_silent:
            print(avgRet)
        return avgRet

    avg = getAvg

    def getAvgArvRChain(self):
        ArvRChain = jlineMatrixToArray(self.obj.getAvgArvRChain())
        if not self._table_silent:
            print(ArvRChain)
        return ArvRChain

    avg_arv_r_chain = getAvgArvRChain

    def getAvgNodeArvRChain(self):
        NodeArvRChain = jlineMatrixToArray(self.obj.getAvgNodeArvRChain())
        if not self._table_silent:
            print(NodeArvRChain)
        return NodeArvRChain

    avg_node_arv_r_chain = getAvgNodeArvRChain

    def getAvgNodeQLenChain(self):
        NodeQLenChain = jlineMatrixToArray(self.obj.getAvgNodeQLenChain())
        if not self._table_silent:
            print(NodeQLenChain)
        return NodeQLenChain

    avg_node_q_len_chain = getAvgNodeQLenChain

    def getAvgNodeResidTChain(self):
        NodeResidTChain = jlineMatrixToArray(self.obj.getAvgNodeResidTChain())
        if not self._table_silent:
            print(NodeResidTChain)
        return NodeResidTChain

    avg_node_residt_chain = getAvgNodeResidTChain

    def getAvgNodeRespTChain(self):
        NodeRespTChain = jlineMatrixToArray(self.obj.getAvgNodeRespTChain())
        if not self._table_silent:
            print(NodeRespTChain)
        return NodeRespTChain

    avg_node_respt_chain = getAvgNodeRespTChain

    def getAvgNodeTputChain(self):
        NodeTputChain = jlineMatrixToArray(self.obj.getAvgNodeTputChain())
        if not self._table_silent:
            print(NodeTputChain)
        return NodeTputChain

    avg_node_tput_chain = getAvgNodeTputChain

    def getAvgNodeUtilChain(self):
        NodeUtilChain = jlineMatrixToArray(self.obj.getAvgNodeUtilChain())
        if not self._table_silent:
            print(NodeUtilChain)
        return NodeUtilChain

    avg_node_util_chain = getAvgNodeUtilChain

    def getAvgQLenChain(self):
        QLenChain = jlineMatrixToArray(self.obj.getAvgQLenChain())
        if not self._table_silent:
            print(QLenChain)
        return QLenChain

    avg_q_len_chain = getAvgQLenChain

    def getAvgResidTChain(self):
        ResidTChain = jlineMatrixToArray(self.obj.getAvgResidTChain())
        if not self._table_silent:
            print(ResidTChain)
        return ResidTChain

    avg_residt_chain = getAvgResidTChain

    def getAvgRespTChain(self):
        RespTChain = jlineMatrixToArray(self.obj.getAvgRespTChain())
        if not self._table_silent:
            print(RespTChain)
        return RespTChain

    avg_respt_chain = getAvgRespTChain

    def getAvgTputChain(self):
        TputChain = jlineMatrixToArray(self.obj.getAvgTputChain())
        if not self._table_silent:
            print(TputChain)
        return TputChain

    avg_tput_chain = getAvgTputChain

    def getAvgUtilChain(self):
        UtilChain = jlineMatrixToArray(self.obj.getAvgUtilChain())
        if not self._table_silent:
            print(UtilChain)
        return UtilChain

    avg_util_chain = getAvgUtilChain

    def getCdfRespT(self):
        try:
            table = self.obj.getCdfRespT()
            distribC = self.obj.fluidResult.distribC

            num_stations = self.model.getNumberOfStations()
            num_classes = self.model.getNumberOfClasses()

            CdfRespT = []
            for i in range(num_stations):
                station_cdfs = []
                for c in range(num_classes):
                    if i < distribC.length and c < distribC[i].length:
                        F = jlineMatrixToArray(distribC[i][c])
                        station_cdfs.append(F)
                    else:
                        station_cdfs.append(None)
                CdfRespT.append(station_cdfs)

            return CdfRespT
        except:
            try:
                num_stations = self.model.getNumberOfStations()
                num_classes = self.model.getNumberOfClasses()
                return [[None for _ in range(num_classes)] for _ in range(num_stations)]
            except:
                return [[]]

    cdf_respt = getCdfRespT

    def getProbAggr(self, node, state=None):
        if hasattr(node, 'obj'):
            if state is not None:
                java_result = self.obj.getProbAggr(node.obj, jlineMatrixFromArray(state))
            else:
                java_result = self.obj.getProbAggr(node.obj)
        else:
            if state is not None:
                java_result = self.obj.getProbAggr(int(node), jlineMatrixFromArray(state))
            else:
                java_result = self.obj.getProbAggr(int(node))

        if hasattr(java_result, 'getScalarProbability'):
            return java_result.getScalarProbability()
        elif hasattr(java_result, 'probability'):
            prob_matrix = java_result.probability
            if prob_matrix.getNumRows() == 1 and prob_matrix.getNumCols() == 1:
                return prob_matrix.get(0, 0)
            else:
                return jlineMatrixToArray(prob_matrix)
        else:
            return float(java_result)

    prob_aggr = getProbAggr

    def getProb(self, node, state=None):
        if hasattr(node, 'obj'):
            if state is not None:
                java_result = self.obj.getProb(node.obj, jlineMatrixFromArray(state))
            else:
                java_result = self.obj.getProb(node.obj)
        else:
            if state is not None:
                java_result = self.obj.getProb(int(node), jlineMatrixFromArray(state))
            else:
                java_result = self.obj.getProb(int(node))

        if hasattr(java_result, 'getScalarProbability'):
            return java_result.getScalarProbability()
        elif hasattr(java_result, 'probability'):
            prob_matrix = java_result.probability
            if prob_matrix.getNumRows() == 1 and prob_matrix.getNumCols() == 1:
                return prob_matrix.get(0, 0)
            else:
                return jlineMatrixToArray(prob_matrix)
        else:
            return float(java_result)

    prob = getProb

    def isSolved(self):
        return hasattr(self, 'obj') and self.obj.hasResults()

    def getSolverType(self):
        if hasattr(self, 'obj'):
            return self.obj.getName()
        return self.__class__.__name__.replace('Solver', '')

    def reset(self):
        if hasattr(self, 'obj') and hasattr(self.obj, 'reset'):
            self.obj.reset()

    def javaObj(self):
        return self.obj if hasattr(self, 'obj') else None

    def getUtil(self):
        return self.getAvgUtil()

    def print(self):
        if hasattr(self, 'obj') and self.obj is not None:
            self.obj.print_()
        else:
            raise RuntimeError("No Java solver object available")

    def hasResults(self):
        if hasattr(self, 'obj') and self.obj is not None:
            try:
                return self.obj.hasResults()
            except:
                return False
        else:
            return False

    @classmethod
    def supportsModel(cls, model):
        return True

    def avgNodeTable(self):
        """Kotlin-style alias for getAvgNodeTable"""
        return self.getAvgNodeTable()

    def avgChainTable(self):
        """Kotlin-style alias for getAvgChainTable"""
        return self.getAvgChainTable()

    def avgNodeChainTable(self):
        """Kotlin-style alias for getAvgNodeChainTable"""
        return self.getAvgNodeChainTable()

    def avgTable(self):
        """Kotlin-style alias for getAvgTable"""
        return self.get_avg_table()

    def avgSysTable(self):
        """Kotlin-style alias for getAvgSysTable"""
        return self.getAvgSysTable()

    def avgTput(self):
        """Kotlin-style alias for getAvgTput"""
        return self.getAvgTput()

    def avgResidT(self):
        """Kotlin-style alias for getAvgResidT"""
        return self.getAvgResidT()

    def avgArvR(self):
        """Kotlin-style alias for getAvgArvR"""
        return self.getAvgArvR()

    def avgUtil(self):
        """Kotlin-style alias for getAvgUtil"""
        return self.getAvgUtil()

    def avgQLen(self):
        """Kotlin-style alias for getAvgQLen"""
        return self.getAvgQLen()

    def avgRespT(self):
        """Kotlin-style alias for getAvgRespT"""
        return self.getAvgRespT()

    def avgWaitT(self):
        """Kotlin-style alias for getAvgWaitT"""
        return self.getAvgWaitT()

    def avgSysTput(self):
        """Kotlin-style alias for getAvgSysTput"""
        return self.getAvgSysTput()

    def avgSysRespT(self):
        """Kotlin-style alias for getAvgSysRespT"""
        return self.getAvgSysRespT()

    def avgArvRChain(self):
        """Kotlin-style alias for getAvgArvRChain"""
        return self.getAvgArvRChain()

    def avgNodeArvRChain(self):
        """Kotlin-style alias for getAvgNodeArvRChain"""
        return self.getAvgNodeArvRChain()

    def avgNodeQLenChain(self):
        """Kotlin-style alias for getAvgNodeQLenChain"""
        return self.getAvgNodeQLenChain()

    def avgNodeResidTChain(self):
        """Kotlin-style alias for getAvgNodeResidTChain"""
        return self.getAvgNodeResidTChain()

    def avgNodeRespTChain(self):
        """Kotlin-style alias for getAvgNodeRespTChain"""
        return self.getAvgNodeRespTChain()

    def avgNodeTputChain(self):
        """Kotlin-style alias for getAvgNodeTputChain"""
        return self.getAvgNodeTputChain()

    def avgNodeUtilChain(self):
        """Kotlin-style alias for getAvgNodeUtilChain"""
        return self.getAvgNodeUtilChain()

    def avgQLenChain(self):
        """Kotlin-style alias for getAvgQLenChain"""
        return self.getAvgQLenChain()

    def avgResidTChain(self):
        """Kotlin-style alias for getAvgResidTChain"""
        return self.getAvgResidTChain()

    def avgRespTChain(self):
        """Kotlin-style alias for getAvgRespTChain"""
        return self.getAvgRespTChain()

    def avgTputChain(self):
        """Kotlin-style alias for getAvgTputChain"""
        return self.getAvgTputChain()

    def avgUtilChain(self):
        """Kotlin-style alias for getAvgUtilChain"""
        return self.getAvgUtilChain()

    def util(self):
        """Short alias for getUtil"""
        return self.getUtil()

    def tput(self):
        """Short alias for getAvgTput"""
        return self.getAvgTput()

    def respT(self):
        """Short alias for getAvgRespT"""
        return self.getAvgRespT()

    def qLen(self):
        """Short alias for getAvgQLen"""
        return self.getAvgQLen()

    def residT(self):
        """Short alias for getAvgResidT"""
        return self.getAvgResidT()

    def waitT(self):
        """Short alias for getAvgWaitT"""
        return self.getAvgWaitT()

    def get_util(self):
        """Snake case alias for getUtil"""
        return self.getUtil()

    def get_tput(self):
        """Snake case alias for getAvgTput"""
        return self.getAvgTput()

    def get_resp_t(self):
        """Snake case alias for getAvgRespT"""
        return self.getAvgRespT()

    def get_q_len(self):
        """Snake case alias for getAvgQLen"""
        return self.getAvgQLen()

    def get_resid_t(self):
        """Snake case alias for getAvgResidT"""
        return self.getAvgResidT()

    def get_wait_t(self):
        """Snake case alias for getAvgWaitT"""
        return self.getAvgWaitT()

    def avg_node_table(self):
        """Snake case alias for getAvgNodeTable"""
        return self.getAvgNodeTable()

    def avg_chain_table(self):
        """Snake case alias for getAvgChainTable"""
        return self.getAvgChainTable()

    def avg_node_chain_table(self):
        """Snake case alias for getAvgNodeChainTable"""
        return self.getAvgNodeChainTable()

    def avg_table(self):
        """Snake case alias for getAvgTable"""
        return self.get_avg_table()

    def avg_sys_table(self):
        """Snake case alias for getAvgSysTable"""
        return self.getAvgSysTable()

    def avg_arv_r(self):
        """Snake case alias for getAvgArvR"""
        return self.getAvgArvR()

    def avg_sys_tput(self):
        """Snake case alias for getAvgSysTput"""
        return self.getAvgSysTput()

    def avg_sys_resp_t(self):
        """Snake case alias for getAvgSysRespT"""
        return self.getAvgSysRespT()

    def avg_arv_r_chain(self):
        """Snake case alias for getAvgArvRChain"""
        return self.getAvgArvRChain()

    def avg_node_arv_r_chain(self):
        """Snake case alias for getAvgNodeArvRChain"""
        return self.getAvgNodeArvRChain()

    def avg_node_q_len_chain(self):
        """Snake case alias for getAvgNodeQLenChain"""
        return self.getAvgNodeQLenChain()

    def avg_node_resid_t_chain(self):
        """Snake case alias for getAvgNodeResidTChain"""
        return self.getAvgNodeResidTChain()

    def avg_node_resp_t_chain(self):
        """Snake case alias for getAvgNodeRespTChain"""
        return self.getAvgNodeRespTChain()

    def avg_node_tput_chain(self):
        """Snake case alias for getAvgNodeTputChain"""
        return self.getAvgNodeTputChain()

    def avg_node_util_chain(self):
        """Snake case alias for getAvgNodeUtilChain"""
        return self.getAvgNodeUtilChain()

    def avg_q_len_chain(self):
        """Snake case alias for getAvgQLenChain"""
        return self.getAvgQLenChain()

    def avg_resid_t_chain(self):
        """Snake case alias for getAvgResidTChain"""
        return self.getAvgResidTChain()

    def avg_resp_t_chain(self):
        """Snake case alias for getAvgRespTChain"""
        return self.getAvgRespTChain()

    def avg_tput_chain(self):
        """Snake case alias for getAvgTputChain"""
        return self.getAvgTputChain()

    def avg_util_chain(self):
        """Snake case alias for getAvgUtilChain"""
        return self.getAvgUtilChain()

    def tran_prob(self, node):
        """Snake case alias for getTranProb"""
        return self.getTranProb(node)

    def tran_prob_aggr(self, node):
        """Snake case alias for getTranProbAggr"""
        return self.getTranProbAggr(node)

    def tran_prob_sys(self):
        """Snake case alias for getTranProbSys"""
        return self.getTranProbSys()

    def tran_prob_sys_aggr(self):
        """Snake case alias for getTranProbSysAggr"""
        return self.getTranProbSysAggr()

    def tran_avg(self):
        """Snake case alias for getTranAvg"""
        return self.getTranAvg()

    def tran_cdf_resp_t(self, R=None):
        """Snake case alias for getTranCdfRespT"""
        return self.getTranCdfRespT(R)

    def tran_cdf_pass_t(self, R=None):
        """Snake case alias for getTranCdfPassT"""
        return self.getTranCdfPassT(R)

    def distrib_resp_t(self):
        """Snake case alias for getDistribRespT"""
        return self.getDistribRespT()

    def distrib_resp_t_chain(self):
        """Snake case alias for getDistribRespTChain"""
        return self.getDistribRespTChain()

    def distrib_resp_t_node(self):
        """Snake case alias for getDistribRespTNode"""
        return self.getDistribRespTNode()

    def distrib_resp_t_node_chain(self):
        """Snake case alias for getDistribRespTNodeChain"""
        return self.getDistribRespTNodeChain()

    def tranProb(self, node):
        """Kotlin-style alias for getTranProb"""
        return self.getTranProb(node)

    def tranProbAggr(self, node):
        """Kotlin-style alias for getTranProbAggr"""
        return self.getTranProbAggr(node)

    def tranProbSys(self):
        """Kotlin-style alias for getTranProbSys"""
        return self.getTranProbSys()

    def tranProbSysAggr(self):
        """Kotlin-style alias for getTranProbSysAggr"""
        return self.getTranProbSysAggr()

    def tranAvg(self):
        """Kotlin-style alias for getTranAvg"""
        return self.getTranAvg()

    def tranCdfRespT(self, R=None):
        """Kotlin-style alias for getTranCdfRespT"""
        return self.getTranCdfRespT(R)

    def tranCdfPassT(self, R=None):
        """Kotlin-style alias for getTranCdfPassT"""
        return self.getTranCdfPassT(R)

    def prob(self, node):
        """Kotlin-style alias for getTranProb"""
        return self.getTranProb(node)

    def probAggr(self, node):
        """Kotlin-style alias for getTranProbAggr"""
        return self.getTranProbAggr(node)

    def probSys(self):
        """Kotlin-style alias for getTranProbSys"""
        return self.getTranProbSys()

    def probSysAggr(self):
        """Kotlin-style alias for getTranProbSysAggr"""
        return self.getTranProbSysAggr()

    def name(self):
        """Kotlin-style alias for getName"""
        return self.getName()

    def numberOfModels(self):
        """Kotlin-style alias for getNumberOfModels"""
        return self.getNumberOfModels()

    get_avg_node_table = getAvgNodeTable
    get_avg_chain_table = getAvgChainTable
    get_avg_node_chain_table = getAvgNodeChainTable
    get_avg_table = getAvgTable
    get_avg_sys_table = getAvgSysTable
    get_avg_tput = getAvgTput
    get_avg_resid_t = getAvgResidT
    get_avg_arv_r = getAvgArvR
    get_avg_util = getAvgUtil
    get_avg_q_len = getAvgQLen
    get_avg_resp_t = getAvgRespT
    get_avg_wait_t = getAvgWaitT
    get_avg_sys_tput = getAvgSysTput
    get_avg_sys_resp_t = getAvgSysRespT
    get_avg = getAvg
    get_avg_arv_r_chain = getAvgArvRChain
    get_avg_node_arv_r_chain = getAvgNodeArvRChain
    get_avg_node_q_len_chain = getAvgNodeQLenChain
    get_avg_node_resid_t_chain = getAvgNodeResidTChain
    get_avg_node_resp_t_chain = getAvgNodeRespTChain
    get_avg_node_tput_chain = getAvgNodeTputChain
    get_avg_node_util_chain = getAvgNodeUtilChain
    get_avg_q_len_chain = getAvgQLenChain
    get_avg_resid_t_chain = getAvgResidTChain
    get_avg_resp_t_chain = getAvgRespTChain
    get_avg_tput_chain = getAvgTputChain
    get_avg_util_chain = getAvgUtilChain
    get_cdf_resp_t = getCdfRespT
    get_prob_aggr = getProbAggr
    get_prob = getProb
    get_solver_type = getSolverType
    get_util = getUtil

class SolverCTMC(NetworkSolver):

    def __init__(self, *args, **kwargs):
        if len(args) > 1 and hasattr(args[1], 'obj'):
            options = args[1]
            super().__init__(options, *args[2:], **kwargs)
        else:
            options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.CTMC)
            super().__init__(options, *args[1:], **kwargs)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.ctmc.SolverCTMC(model.obj, self.solveropt.obj)

    def getStateSpace(self):
        StateSpace = self.obj.getStateSpace(self.solveropt.obj)
        return jlineMatrixToArray(StateSpace.stateSpace), jlineMatrixCellToArray(StateSpace.localStateSpace)

    def getGenerator(self):
        generatorResult = self.obj.getGenerator()
        return jlineMatrixToArray(generatorResult.infGen), jlineMapMatrixToArray(generatorResult.eventFilt.toMap())

    @staticmethod
    def printInfGen(infGen, stateSpace):
        jpype.JPackage('jline').solvers.ctmc.SolverCTMC.printInfGen(jlineMatrixFromArray(infGen), jlineMatrixFromArray(stateSpace))

    def getTranProb(self, node):
        try:
            java_result = self.obj.getTranProb(node.obj if hasattr(node, 'obj') else node)
            return ProbabilityResult(java_result)
        except Exception as e:
            if not self._verbose_silent:
                print(f"CTMC getTranProb failed: {e}")
            return None

    tran_prob = getTranProb

    def getTranProbAggr(self, node):
        try:
            java_result = self.obj.getTranProbAggr(node.obj if hasattr(node, 'obj') else node)
            return ProbabilityResult(java_result)
        except Exception as e:
            if not self._verbose_silent:
                print(f"CTMC getTranProbAggr failed: {e}")
            return None

    tran_prob_aggr = getTranProbAggr

    def getTranProbSys(self):
        try:
            java_result = self.obj.getTranProbSys()
            return ProbabilityResult(java_result)
        except Exception as e:
            if not self._verbose_silent:
                print(f"CTMC getTranProbSys failed: {e}")
            return None

    tran_prob_sys = getTranProbSys

    def getTranProbSysAggr(self):
        try:
            java_result = self.obj.getTranProbSysAggr()
            return ProbabilityResult(java_result)
        except Exception as e:
            if not self._verbose_silent:
                print(f"CTMC getTranProbSysAggr failed: {e}")
            return None

    tran_prob_sys_aggr = getTranProbSysAggr

    def getProbSysAggr(self):
        try:
            java_result = self.obj.getProbSysAggr()
            return ProbabilityResult(java_result)
        except Exception as e:
            if not self._verbose_silent:
                print(f"CTMC getProbSysAggr failed: {e}")
            return None

    prob_sys_aggr = getProbSysAggr

    def sample(self, node, numSamples):
        java_result = self.obj.sample(node.obj, numSamples)
        return SampleResult(java_result) if java_result is not None else None

    def sampleAggr(self, node, numSamples):
        java_result = self.obj.sampleAggr(node.obj, numSamples)
        return SampleResult(java_result) if java_result is not None else None

    def sampleSys(self, numEvents):
        java_result = self.obj.sampleSys(numEvents)
        return SampleResult(java_result) if java_result is not None else None

    def sampleSysAggr(self, numEvents):
        java_result = self.obj.sampleSysAggr(numEvents)
        return SampleResult(java_result) if java_result is not None else None

    @staticmethod
    def defaultOptions():
        """Returns default solver options for the CTMC solver."""
        java_options = jpype.JPackage('jline').solvers.ctmc.SolverCTMC.defaultOptions()
        python_options = SolverOptions.__new__(SolverOptions)
        python_options.obj = java_options
        return python_options

    @staticmethod
    def supportsModel(model):
        java_solver_class = jpype.JPackage('jline').solvers.ctmc.SolverCTMC
        return java_solver_class.supports(model.obj if hasattr(model, 'obj') else model)

    get_state_space = getStateSpace
    get_generator = getGenerator
    get_tran_prob = getTranProb
    get_tran_prob_aggr = getTranProbAggr
    get_tran_prob_sys = getTranProbSys
    get_tran_prob_sys_aggr = getTranProbSysAggr
    get_prob_sys_aggr = getProbSysAggr
    sample_sys_aggr = sampleSysAggr
    sample_sys = sampleSys

class SolverEnv(EnsembleSolver):
    def __init__(self, *args, **kwargs):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.ENV)
        super().__init__(options, **kwargs)
        model = args[0]
        solvers = jpype.JPackage('jline').solvers.NetworkSolver[len(args[1])]
        for i in range(len(solvers)):
            solvers[i] = args[1][i].obj
        self.obj = jpype.JPackage('jline').solvers.env.SolverEnv(model.obj, solvers, self.solveropt.obj)

    def getEnsembleAvg(self):
        return self.obj.getEnsembleAvg()

    def printAvgTable(self):
        self.obj.printAvgTable()

    def runAnalyzer(self):
        self.obj.runAnalyzer()

    def getName(self):
        return self.obj.getName()

    @staticmethod
    def defaultOptions():
        """Returns default solver options for the Env solver."""
        java_options = jpype.JPackage('jline').solvers.env.SolverEnv.defaultOptions()
        python_options = SolverOptions.__new__(SolverOptions)
        python_options.obj = java_options
        return python_options

    get_ensemble_avg = getEnsembleAvg
    get_name = getName


class SolverFluid(NetworkSolver):
    def __init__(self, *args, **kwargs):
        if len(args) > 1 and hasattr(args[1], 'obj'):
            options = args[1]
            super().__init__(options, *args[2:], **kwargs)
        else:
            options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.FLUID)
            super().__init__(options, *args[1:], **kwargs)
        self.model = args[0]
        self.obj = jpype.JPackage('jline').solvers.fluid.SolverFluid(self.model.obj, self.solveropt.obj)

    def getTranAvg(self):

        result = self.obj.result

        M = result.QNt.length
        K = result.QNt[0].length

        def extract(metrics):
            return [[jlineMatrixToArray(metrics[i][k]) for k in range(K)] for i in range(M)]

        return {
            'QNt': extract(result.QNt),
            'UNt': extract(result.UNt),
            'TNt': extract(result.TNt),
        }

    tran_avg = getTranAvg

    def getCdfRespT(self, R=None):
        try:
            java_result = self.obj.getCdfRespT()

            if hasattr(self.obj, 'result') and self.obj.result is not None:
                fluid_result = self.obj.result
                if hasattr(fluid_result, 'distribC') and fluid_result.distribC is not None:
                    distribC = fluid_result.distribC

                    num_stations = self.model.getNumberOfStations()
                    num_classes = self.model.getNumberOfClasses()

                    CdfRespT = []
                    for i in range(num_stations):
                        station_cdfs = []
                        for c in range(num_classes):
                            if (i < distribC.length and
                                distribC[i] is not None and
                                c < distribC[i].length and
                                distribC[i][c] is not None):
                                cdf_array = jlineMatrixToArray(distribC[i][c])
                                station_cdfs.append(cdf_array)
                            else:
                                station_cdfs.append(None)
                        CdfRespT.append(station_cdfs)

                    return CdfRespT

            num_stations = self.model.getNumberOfStations()
            num_classes = self.model.getNumberOfClasses()
            return [[None for _ in range(num_classes)] for _ in range(num_stations)]

        except Exception as e:
            if not self._verbose_silent:
                print(f"Fluid getCdfRespT failed: {e}")
            try:
                num_stations = self.model.getNumberOfStations()
                num_classes = self.model.getNumberOfClasses()
                return [[None for _ in range(num_classes)] for _ in range(num_stations)]
            except:
                return [[]]

    cdf_respt = getCdfRespT

    @staticmethod
    def defaultOptions():
        """Returns default solver options for the Fluid solver."""
        java_options = jpype.JPackage('jline').solvers.fluid.SolverFluid.defaultOptions()
        python_options = SolverOptions.__new__(SolverOptions)
        python_options.obj = java_options
        return python_options

    @staticmethod
    def supportsModel(model):
        java_solver_class = jpype.JPackage('jline').solvers.fluid.SolverFluid
        return java_solver_class.supports(model.obj if hasattr(model, 'obj') else model)

    get_tran_avg = getTranAvg
    get_cdf_resp_t = getCdfRespT


class SolverJMT(NetworkSolver):
    def __init__(self, *args, **kwargs):
        if len(args) > 1 and hasattr(args[1], 'obj'):
            options = args[1]
            super().__init__(options, *args[2:], **kwargs)
        else:
            options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.JMT)
            super().__init__(options, *args[1:], **kwargs)
        self.model = args[0]

        package_dir = os.path.dirname(os.path.abspath(__file__))
        python_dir = os.path.dirname(package_dir)
        root_dir = os.path.dirname(python_dir)
        common_dir = os.path.join(root_dir, 'common')
        jmt_jar_path = os.path.join(common_dir, 'JMT.jar')

        if not os.path.isfile(jmt_jar_path):
            print("JMT.jar not found in", common_dir)
            print("Attempting to download JMT.jar...")
            try:
                from urllib.request import urlretrieve
                jmt_url = 'https://line-solver.sourceforge.net/latest/JMT.jar'
                urlretrieve(jmt_url, jmt_jar_path)
                print("Successfully downloaded JMT.jar to", common_dir)
            except Exception as e:
                raise RuntimeError(f"Failed to download JMT.jar: {e}\n"
                                 f"Please manually download https://line-solver.sourceforge.net/latest/JMT.jar "
                                 f"and place it in {common_dir}")

        self.jmtPath = jpype.JPackage('java').lang.String(jmt_jar_path)
        self.obj = jpype.JPackage('jline').solvers.jmt.SolverJMT(self.model.obj, self.solveropt.obj, self.jmtPath)

    def jsimwView(self):
        self.obj.jsimwView(self.jmtPath)

    def jsimgView(self):
        self.obj.jsimgView(self.jmtPath)

    def sampleAggr(self, node, numEvents=None, markActivePassive=False):
        """Sample from a specific node using aggregated states"""
        try:
            if numEvents is None:
                java_result = self.obj.sampleAggr(node.obj)
            else:
                java_result = self.obj.sampleAggr(node.obj, numEvents, markActivePassive)
            return java_result
        except Exception as e:
            if not self._verbose_silent:
                print(f"JMT aggregated sampling failed: {e}")
            return None

    def sampleSysAggr(self, numEvents=None, markActivePassive=False):
        """Sample system-wide using aggregated states"""
        try:
            if numEvents is None:
                java_result = self.obj.sampleSysAggr()
            else:
                java_result = self.obj.sampleSysAggr(numEvents, markActivePassive)
            return java_result
        except Exception as e:
            if not self._verbose_silent:
                print(f"JMT system aggregated sampling failed: {e}")
            return None

    def getProbSysAggr(self):
        try:
            java_result = self.obj.getProbSysAggr()
            return ProbabilityResult(java_result)
        except Exception as e:
            if not self._verbose_silent:
                print(f"JMT getProbSysAggr failed: {e}")
            return None

    def getCdfRespT(self, R=None):
        try:
            if R is None:
                java_result = self.obj.getCdfRespT()
            else:
                java_result = self.obj.getCdfRespT(R.obj if hasattr(R, 'obj') else R)

            if java_result is None:
                num_stations = self.model.getNumberOfStations()
                num_classes = self.model.getNumberOfClasses()
                return [[None for _ in range(num_classes)] for _ in range(num_stations)]

            num_stations = java_result.numStations
            num_classes = java_result.numClasses

            CdfRespT = []
            for i in range(num_stations):
                station_cdfs = []
                for c in range(num_classes):
                    if java_result.hasCdf(i, c):
                        cdf_matrix = java_result.getCdf(i, c)
                        if cdf_matrix is not None:
                            cdf_array = jlineMatrixToArray(cdf_matrix)
                            station_cdfs.append(cdf_array)
                        else:
                            station_cdfs.append(None)
                    else:
                        station_cdfs.append(None)
                CdfRespT.append(station_cdfs)

            return CdfRespT
        except Exception as e:
            if not self._verbose_silent:
                print(f"JMT getCdfRespT failed: {e}")
            try:
                num_stations = self.model.getNumberOfStations()
                num_classes = self.model.getNumberOfClasses()
                return [[None for _ in range(num_classes)] for _ in range(num_stations)]
            except:
                return [[]]

    def getTranCdfRespT(self, R=None):
        try:
            if R is None:
                java_result = self.obj.getTranCdfRespT()
            else:
                java_result = self.obj.getTranCdfRespT(R.obj if hasattr(R, 'obj') else R)

            if java_result is None:
                num_stations = self.model.getNumberOfStations()
                num_classes = self.model.getNumberOfClasses()
                return [[None for _ in range(num_classes)] for _ in range(num_stations)]

            num_stations = java_result.numStations
            num_classes = java_result.numClasses

            CdfRespT = []
            for i in range(num_stations):
                station_cdfs = []
                for c in range(num_classes):
                    if java_result.hasCdf(i, c):
                        cdf_matrix = java_result.getCdf(i, c)
                        if cdf_matrix is not None:
                            cdf_array = jlineMatrixToArray(cdf_matrix)
                            station_cdfs.append(cdf_array)
                        else:
                            station_cdfs.append(None)
                    else:
                        station_cdfs.append(None)
                CdfRespT.append(station_cdfs)

            return CdfRespT
        except Exception as e:
            if not self._verbose_silent:
                print(f"JMT getTranCdfRespT failed: {e}")
            try:
                num_stations = self.model.getNumberOfStations()
                num_classes = self.model.getNumberOfClasses()
                return [[None for _ in range(num_classes)] for _ in range(num_stations)]
            except:
                return [[]]

    tran_cdf_respt = getTranCdfRespT

    def getTranCdfPassT(self, R=None):
        try:
            if R is None:
                java_result = self.obj.getTranCdfPassT()
            else:
                java_result = self.obj.getTranCdfPassT(R.obj if hasattr(R, 'obj') else R)
            return DistributionResult(java_result)
        except Exception as e:
            if not self._verbose_silent:
                print(f"JMT getTranCdfPassT failed: {e}")
            return None

    tran_cdf_passt = getTranCdfPassT

    def getTranAvg(self, Qt=None, Ut=None, Tt=None):
        """Get transient average station metrics.
        
        Args:
            Qt: Optional queue length handles 
            Ut: Optional utilization handles
            Tt: Optional throughput handles
            
        Returns:
            Tuple of (QNclass_t, UNclass_t, TNclass_t) containing transient metrics
            Each element is a list of lists [station][class] containing time series data
        """
        try:
            # Check that timespan is finite for transient analysis
            options = self.obj.getOptions()
            timespan_end = options.timespan[1]
            if timespan_end == float('inf'):
                raise RuntimeError("Transient analysis requires finite timespan. "
                                 "Use SolverJMT(model, timespan=[0, T]) to specify timespan.")
            
            # Call Java getTranAvg method to populate transient results
            self.obj.getTranAvg()
            
            # Check if transient results are available
            if not hasattr(self.obj, 'result') or self.obj.result is None:
                print("Warning: Transient results not available. Check solver execution.")
                return None, None, None
            
            result = self.obj.result
            if not hasattr(result, 'QNt') or result.QNt is None:
                print("Warning: Transient data not available. Check solver execution.")
                return None, None, None
            
            # Get network dimensions
            M = self.model.getNumberOfStations()
            K = self.model.getNumberOfClasses()
            
            # Initialize output lists
            QNclass_t = [[None for _ in range(K)] for _ in range(M)]
            UNclass_t = [[None for _ in range(K)] for _ in range(M)]
            TNclass_t = [[None for _ in range(K)] for _ in range(M)]
            
            # Extract transient results from Java solver
            for k in range(K):
                for ist in range(M):
                    # Queue length transients
                    try:
                        java_result = self.obj.getTranQLen()
                        if java_result is not None and len(java_result) > ist and len(java_result[ist]) > k:
                            if java_result[ist][k] is not None:
                                ret = jlineMatrixToArray(java_result[ist][k])
                                if ret is not None and len(ret) > 0 and len(ret[0]) >= 2:
                                    QNclass_t[ist][k] = {
                                        'handle': (self.model.getStations()[ist], self.model.getClasses()[k]),
                                        't': [row[1] for row in ret],  # time points
                                        'metric': [row[0] for row in ret],  # queue length values
                                        'isaggregate': True
                                    }
                    except:
                        pass
                    
                    # Utilization transients
                    try:
                        java_result = self.obj.getTranUtil()
                        if java_result is not None and len(java_result) > ist and len(java_result[ist]) > k:
                            if java_result[ist][k] is not None:
                                ret = jlineMatrixToArray(java_result[ist][k])
                                if ret is not None and len(ret) > 0 and len(ret[0]) >= 2:
                                    UNclass_t[ist][k] = {
                                        'handle': (self.model.getStations()[ist], self.model.getClasses()[k]),
                                        't': [row[1] for row in ret],  # time points  
                                        'metric': [row[0] for row in ret],  # utilization values
                                        'isaggregate': True
                                    }
                    except:
                        pass
                    
                    # Throughput transients
                    try:
                        java_result = self.obj.getTranTput()
                        if java_result is not None and len(java_result) > ist and len(java_result[ist]) > k:
                            if java_result[ist][k] is not None:
                                ret = jlineMatrixToArray(java_result[ist][k])
                                if ret is not None and len(ret) > 0 and len(ret[0]) >= 2:
                                    TNclass_t[ist][k] = {
                                        'handle': (self.model.getStations()[ist], self.model.getClasses()[k]),
                                        't': [row[1] for row in ret],  # time points
                                        'metric': [row[0] for row in ret],  # throughput values
                                        'isaggregate': True
                                    }
                    except:
                        pass
            
            return QNclass_t, UNclass_t, TNclass_t
            
        except Exception as e:
            raise RuntimeError(f"Failed to compute transient metrics: {e}")

    @staticmethod
    def defaultOptions():
        """Returns default solver options for the JMT solver."""
        java_options = jpype.JPackage('jline').solvers.jmt.SolverJMT.defaultOptions()
        python_options = SolverOptions.__new__(SolverOptions)
        python_options.obj = java_options
        return python_options

    @staticmethod
    def supportsModel(model):
        java_solver_class = jpype.JPackage('jline').solvers.jmt.SolverJMT
        return java_solver_class.supports(model.obj if hasattr(model, 'obj') else model)

    get_prob_sys_aggr = getProbSysAggr
    get_cdf_resp_t = getCdfRespT
    get_tran_cdf_resp_t = getTranCdfRespT
    get_tran_cdf_pass_t = getTranCdfPassT
    sample_sys_aggr = sampleSysAggr
    #sample_sys = sampleSys

class SolverMAM(NetworkSolver):
    def __init__(self, *args, **kwargs):
        if len(args) > 1 and hasattr(args[1], 'obj'):
            options = args[1]
            super().__init__(options, *args[2:], **kwargs)
        else:
            options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.MAM)
            super().__init__(options, *args[1:], **kwargs)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.mam.SolverMAM(model.obj, self.solveropt.obj)

    @staticmethod
    def defaultOptions():
        """Returns default solver options for the MAM solver."""
        java_options = jpype.JPackage('jline').solvers.mam.SolverMAM.defaultOptions()
        python_options = SolverOptions.__new__(SolverOptions)
        python_options.obj = java_options
        return python_options

    @staticmethod
    def supportsModel(model):
        java_solver_class = jpype.JPackage('jline').solvers.mam.SolverMAM
        return java_solver_class.supports(model.obj if hasattr(model, 'obj') else model)

class SolverMVA(NetworkSolver):
    def __init__(self, *args, **kwargs):
        if len(args) > 1 and hasattr(args[1], 'obj'):
            options = args[1]
            super().__init__(options, *args[2:], **kwargs)
        else:
            try:
                options = SolverMVA.defaultOptions()
            except:
                import line_solver
                options = line_solver.lineDefaults()
            super().__init__(options, *args[1:], **kwargs)
        model = args[0]

        try:
            self.obj = jpype.JPackage('jline').solvers.mva.SolverMVA(model.obj, self.solveropt.obj)
        except jpype.JException as e:
            if "Outside of matrix bounds" in str(e):
                import line_solver
                working_options = line_solver.lineDefaults()
                self.solveropt = working_options
                self.obj = jpype.JPackage('jline').solvers.mva.SolverMVA(model.obj, self.solveropt.obj)
            else:
                raise

    @staticmethod
    def defaultOptions():
        """Returns default solver options for the MVA solver."""
        java_options = jpype.JPackage('jline').solvers.mva.SolverMVA.defaultOptions()
        python_options = SolverOptions.__new__(SolverOptions)
        python_options.obj = java_options
        return python_options

    @staticmethod
    def supportsModel(model):
        java_solver_class = jpype.JPackage('jline').solvers.mva.SolverMVA
        return java_solver_class.supports(model.obj if hasattr(model, 'obj') else model)

class SolverQNS(NetworkSolver):
    def __init__(self, *args, **kwargs):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.QNS)
        super().__init__(options, *args[1:], **kwargs)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.qns.SolverQNS(model.obj, self.solveropt.obj)

    def listValidMethods(self):
        """List valid methods for the QNS solver"""
        return ['default', 'conway', 'rolia', 'zhou', 'suri', 'reiser', 'schmidt']

    @staticmethod
    def isAvailable():
        """Check if the QNS solver is available"""
        return jpype.JPackage('jline').solvers.qns.SolverQNS.isAvailable()

    @staticmethod
    def defaultOptions():
        """Returns default solver options for the QNS solver."""
        java_options = jpype.JPackage('jline').solvers.qns.SolverQNS.defaultOptions()
        python_options = SolverOptions.__new__(SolverOptions)
        python_options.obj = java_options
        return python_options

    @staticmethod
    def supportsModel(model):
        java_solver_class = jpype.JPackage('jline').solvers.qns.SolverQNS
        return java_solver_class.supports(model.obj if hasattr(model, 'obj') else model)

class SolverLQNS(Solver):
    def __init__(self, *args, **kwargs):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.LQNS)
        super().__init__(options, *args[1:], **kwargs)
        model = args[0]
        try:
            self.obj = jpype.JPackage('jline').solvers.lqns.SolverLQNS(model.obj, self.solveropt.obj)
        except Exception as e:
            error_msg = str(e)
            if "lqns" in error_msg.lower() and "lqsim" in error_msg.lower():
                raise RuntimeError(
                    "SolverLQNS requires the 'lqns' and 'lqsim' commands to be available in your system PATH.\n"
                    "You can install them from: http://www.sce.carleton.ca/rads/lqns/\n\n"
                    "To skip this solver in advanced, check if LQNS is available before creating the solver:\n"
                    "if SolverLQNS.isAvailable():\n"
                    "    solver = SolverLQNS(model)"
                ) from e
            else:
                raise e

    @staticmethod
    def isAvailable():
        try:
            return jpype.JPackage('jline').solvers.lqns.SolverLQNS.isAvailable()
        except Exception:
            return False

    def getAvgTable(self):
        table = self.obj.getAvgTable()

        QLen = np.array(list(table.getQLen()))
        Util = np.array(list(table.getUtil()))
        RespT = np.array(list(table.getRespT()))
        ResidT = np.array(list(table.getResidT()))
        ArvR = np.array(list(table.getArvR()))
        Tput = np.array(list(table.getTput()))

        cols = ['QLen', 'Util', 'RespT', 'ResidT', 'ArvR', 'Tput']
        nodenames = list(table.getNodeNames())
        mynodenames = []
        for i in range(len(nodenames)):
            mynodenames.append(str(nodenames[i]))
        nodetypes = list(table.getNodeTypes())
        mynodetypes = []
        for i in range(len(nodetypes)):
            mynodetypes.append(str(nodetypes[i]))
        AvgTable = pd.DataFrame(np.concatenate([[QLen, Util, RespT, ResidT, ArvR, Tput]]).T, columns=cols)
        tokeep = ~(AvgTable <= 0.0).all(axis=1)
        AvgTable.insert(0, "NodeType", mynodetypes)
        AvgTable.insert(0, "Node", mynodenames)
        AvgTable = AvgTable.loc[tokeep]
        if not self._table_silent:
            print(AvgTable)

        return AvgTable

    avg_table = getAvgTable

    @staticmethod
    def defaultOptions():
        """Returns default solver options for the LQNS solver."""
        java_options = jpype.JPackage('jline').solvers.lqns.SolverLQNS.defaultOptions()
        python_options = SolverOptions.__new__(SolverOptions)
        python_options.obj = java_options
        return python_options

    @staticmethod
    def supportsModel(model):
        java_solver_class = jpype.JPackage('jline').solvers.lqns.SolverLQNS
        return java_solver_class.supports(model.obj if hasattr(model, 'obj') else model)

    get_avg_table = getAvgTable

class SolverLN(EnsembleSolver):
    def __init__(self, *args, **kwargs):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.LN)
        super().__init__(options, *args[1:], **kwargs)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.ln.SolverLN(model.obj, self.solveropt.obj)


    def getAvgTable(self):
        table = self.obj.getAvgTable()

        QLen = np.array(list(table.getQLen()))
        Util = np.array(list(table.getUtil()))
        RespT = np.array(list(table.getRespT()))
        ResidT = np.array(list(table.getResidT()))
        ArvR = np.array(list(table.getArvR()))
        Tput = np.array(list(table.getTput()))

        cols = ['QLen', 'Util', 'RespT', 'ResidT', 'ArvR', 'Tput']
        nodenames = list(table.getNodeNames())
        mynodenames = []
        for i in range(len(nodenames)):
            mynodenames.append(str(nodenames[i]))
        nodetypes = list(table.getNodeTypes())
        mynodetypes = []
        for i in range(len(nodetypes)):
            mynodetypes.append(str(nodetypes[i]))
        AvgTable = pd.DataFrame(np.concatenate([[QLen, Util, RespT, ResidT, ArvR, Tput]]).T, columns=cols)
        tokeep = ~(AvgTable <= 0.0).all(axis=1)
        AvgTable.insert(0, "NodeType", mynodetypes)
        AvgTable.insert(0, "Node", mynodenames)
        AvgTable = AvgTable.loc[tokeep]
        if not self._table_silent:
            print(AvgTable)

        return AvgTable

    avg_table = getAvgTable

    @staticmethod
    def defaultOptions():
        """Returns default solver options for the LN solver."""
        java_options = jpype.JPackage('jline').solvers.ln.SolverLN.defaultOptions()
        python_options = SolverOptions.__new__(SolverOptions)
        python_options.obj = java_options
        return python_options

    @staticmethod
    def supportsModel(model):
        java_solver_class = jpype.JPackage('jline').solvers.ln.SolverLN
        return java_solver_class.supports(model.obj if hasattr(model, 'obj') else model)

    get_avg_table = getAvgTable

class SolverNC(NetworkSolver):
    def __init__(self, *args, **kwargs):
        if len(args) > 1 and hasattr(args[1], 'obj'):
            options = args[1]
            super().__init__(options, *args[2:], **kwargs)
        else:
            options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.NC)
            super().__init__(options, *args[1:], **kwargs)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.nc.SolverNC(model.obj, self.solveropt.obj)

    def getProbSysAggr(self):
        try:
            java_result = self.obj.getProbSysAggr()
            return ProbabilityResult(java_result)
        except Exception as e:
            if not self._verbose_silent:
                print(f"NC getProbSysAggr failed: {e}")
            return None

    @staticmethod
    def defaultOptions():
        """Returns default solver options for the NC solver."""
        java_options = jpype.JPackage('jline').solvers.nc.SolverNC.defaultOptions()
        python_options = SolverOptions.__new__(SolverOptions)
        python_options.obj = java_options
        return python_options

    @staticmethod
    def supportsModel(model):
        java_solver_class = jpype.JPackage('jline').solvers.nc.SolverNC
        return java_solver_class.supports(model.obj if hasattr(model, 'obj') else model)

    get_prob_sys_aggr = getProbSysAggr

class SolverSSA(NetworkSolver):
    def __init__(self, *args, **kwargs):
        if len(args) > 1 and hasattr(args[1], 'obj'):
            options = args[1]
            super().__init__(options, *args[2:], **kwargs)
        else:
            options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.SSA)
            super().__init__(options, *args[1:], **kwargs)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.ssa.SolverSSA(model.obj, self.solveropt.obj)

    def sample(self, node, numSamples=10000, markActivePassive=False):
        """Sample from a specific node"""
        try:
            if numSamples is None:
                java_result = self.obj.sample(node.obj)
            else:
                java_result = self.obj.sample(node.obj, numSamples, markActivePassive)
            return SampleResult(java_result) if java_result is not None else None
        except Exception as e:
            if not self._verbose_silent:
                print(f"SSA sampling failed: {e}")
            return None

    def sampleAggr(self, node, numSamples=10000, markActivePassive=False):
        """Sample from a specific node using aggregated states"""
        try:
            if numSamples is None:
                java_result = self.obj.sampleAggr(node.obj)
            else:
                java_result = self.obj.sampleAggr(node.obj, numSamples, markActivePassive)
            return SampleResult(java_result) if java_result is not None else None
        except Exception as e:
            if not self._verbose_silent:
                print(f"SSA aggregated sampling failed: {e}")
            return None

    def sampleSys(self, numSamples=10000):
        """Sample system-wide"""
        try:
            if numSamples is None:
                java_result = self.obj.sampleSys()
            else:
                java_result = self.obj.sampleSys(numSamples)
            return SampleResult(java_result) if java_result is not None else None
        except Exception as e:
            if not self._verbose_silent:
                print(f"SSA system sampling failed: {e}")
            return None

    def sampleSysAggr(self, numSamples=10000):
        """Sample system-wide using aggregated states"""
        try:
            if numSamples is None:
                java_result = self.obj.sampleSysAggr()
            else:
                java_result = self.obj.sampleSysAggr(numSamples)
            return SampleResult(java_result) if java_result is not None else None
        except Exception as e:
            if not self._verbose_silent:
                print(f"SSA system aggregated sampling failed: {e}")
            return None

    @staticmethod
    def defaultOptions():
        """Returns default solver options for the SSA solver."""
        java_options = jpype.JPackage('jline').solvers.ssa.SolverSSA.defaultOptions()
        python_options = SolverOptions.__new__(SolverOptions)
        python_options.obj = java_options
        return python_options

    @staticmethod
    def supportsModel(model):
        java_solver_class = jpype.JPackage('jline').solvers.ssa.SolverSSA
        return java_solver_class.supports(model.obj if hasattr(model, 'obj') else model)

    sample_sys_aggr = sampleSysAggr
    sample_sys = sampleSys

class SolverAuto(NetworkSolver):
    def __init__(self, *args, **kwargs):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.MVA)
        super().__init__(options, *args[1:], **kwargs)
        model = args[0]
        SolverAutoClass = jpype.JClass('jline.solvers.auto.SolverAuto')
        self.obj = SolverAutoClass(model.obj)

    def getSelectedSolverName(self):
        """Get the name of the solver that was automatically selected"""
        return self.obj.getSelectedSolverName()

    def getCandidateSolverNames(self):
        """Get list of candidate solver names that could be used for this model"""
        names = self.obj.getCandidateSolverNames()
        return [str(name) for name in names]

    def setSelectionMethod(self, method):
        """Set the solver selection method: 'default', 'heur', 'ai', or 'nn'"""
        self.solveropt.obj.method = method

    def setForcedSolver(self, solver_name):
        """Force a specific solver: 'mva', 'nc', 'mam', 'fluid', 'jmt', 'ssa', 'ctmc'"""
        auto_opts = AutoOptions()
        auto_opts.setForcedSolver(solver_name)

    @staticmethod
    def supportsModel(model):
        SolverAutoClass = jpype.JClass('jline.solvers.auto.SolverAuto')
        return SolverAutoClass.supports(model.obj if hasattr(model, 'obj') else model)

    get_selected_solver_name = getSelectedSolverName
    get_candidate_solver_names = getCandidateSolverNames
    set_selection_method = setSelectionMethod
    set_forced_solver = setForcedSolver


class LINE(SolverAuto):
    """Alias for SolverAuto - automatic solver selection."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SolverConfig():
    """Python wrapper for SolverOptions.Config class"""
    def __init__(self, java_config):
        self.obj = java_config

    @property
    def multiserver(self):
        return self.obj.multiserver

    @multiserver.setter
    def multiserver(self, value):
        self.obj.multiserver = value

    @property
    def highvar(self):
        return self.obj.highvar

    @highvar.setter
    def highvar(self, value):
        self.obj.highvar = value

    @property
    def np_priority(self):
        return self.obj.np_priority

    @np_priority.setter
    def np_priority(self, value):
        self.obj.np_priority = value

    @property
    def fork_join(self):
        return self.obj.fork_join

    @fork_join.setter
    def fork_join(self, value):
        self.obj.fork_join = value

    @property
    def eventcache(self):
        return self.obj.eventcache

    @eventcache.setter
    def eventcache(self, value):
        self.obj.eventcache = value

class SolverOptions():
    def __init__(self, solvertype):
        self.obj = jpype.JPackage('jline').solvers.SolverOptions(solvertype)
        self._config = None

    def method(self, value):
        self.obj.method(value)

    def samples(self, value):
        self.obj.samples(value)

    def seed(self, value):
        self.obj.seed(value)

    def verbose(self, value):
        if hasattr(value, 'value'):
            self.obj.verbose(value.value)
        else:
            self.obj.verbose(value)

    @property
    def config(self):
        """Access to advanced configuration options"""
        if not hasattr(self, '_config') or self._config is None:
            self._config = SolverConfig(self.obj.config)
        return self._config

    @property
    def iter_max(self):
        return self.obj.iter_max

    @iter_max.setter
    def iter_max(self, value):
        self.obj.iter_max = value

    @property
    def iter_tol(self):
        return self.obj.iter_tol

    @iter_tol.setter
    def iter_tol(self, value):
        self.obj.iter_tol = value

    @property
    def tol(self):
        return self.obj.tol

    @tol.setter
    def tol(self, value):
        self.obj.tol = value

    def __setitem__(self, key, value):
        """Support dictionary-style assignment for solver options."""
        if key == 'keep':
            self.obj.keep(bool(value))
        elif key == 'verbose':
            if hasattr(value, 'value'):
                self.obj.verbose(value.value)
            else:
                self.obj.verbose(value)
        elif key == 'cutoff':
            if hasattr(value, '__iter__') and not isinstance(value, str):
                from line_solver import jlineMatrixFromArray
                self.obj.cutoff(jlineMatrixFromArray(value))
            else:
                self.obj.cutoff(value)
        elif key == 'seed':
            self.obj.seed(int(value))
        elif key == 'samples':
            self.obj.samples(int(value))
        elif key == 'method':
            self.obj.method(str(value))
        elif key == 'force':
            self.obj.force(bool(value))
        elif key in ['iter_max', 'iter_tol', 'tol']:
            setattr(self.obj, key, value)
        elif key == 'timespan':
            if hasattr(value, '__iter__'):
                from jpype import JArray, JDouble
                self.obj.timespan = JArray(JDouble)(value)
            else:
                self.obj.timespan = value
        elif key == 'timestep':
            from jpype import JDouble
            self.obj.timestep = JDouble(value) if value is not None else None
        elif hasattr(self.obj, key):
            try:
                setattr(self.obj, key, value)
            except AttributeError:
                raise KeyError(f"Solver option '{key}' is not settable")
        else:
            raise KeyError(f"Unknown solver option: '{key}'")

    def __getitem__(self, key):
        """Support dictionary-style access for solver options."""
        if hasattr(self.obj, key):
            value = getattr(self.obj, key)

            if hasattr(value, '__call__'):
                raise KeyError(f"Cannot read solver option '{key}' - use property-style access instead (options.{key})")

            if hasattr(value, 'value'):
                return value.value
            elif str(type(value)).startswith('<java'):
                try:
                    if hasattr(value, 'toString'):
                        return value.toString()
                    else:
                        return str(value)
                except:
                    return value
            else:
                return value
        else:
            raise KeyError(f"Unknown solver option: '{key}'")

class CTMCOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.CTMCOptions()

class EnvOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.EnvOptions()

class FluidOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.FluidOptions()

class JMTOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.JMTOptions()

class LNOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.LNOptions()

class LQNSOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.LQNSOptions()

class MAMOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.MAMOptions()

class MVAOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.MVAOptions()

class NCOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.NCOptions()

class QNSOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.qns.SolverQNS.defaultOptions()

class SSAOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.SSAOptions()

class AutoOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.auto.AutoOptions()

    def setSelectionMethod(self, method):
        """Set the solver selection method: 'default', 'heur', 'ai', or 'nn'"""
        self.obj.selectionMethod = method

    def setForcedSolver(self, solver_name):
        """Force a specific solver: 'mva', 'nc', 'mam', 'fluid', 'jmt', 'ssa', 'ctmc'"""
        self.obj.forceSolver = solver_name

    set_selection_method = setSelectionMethod
    set_forced_solver = setForcedSolver
