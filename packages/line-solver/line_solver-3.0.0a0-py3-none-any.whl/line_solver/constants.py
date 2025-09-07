
from enum_tools import Enum
import jpype
import jpype.imports
from line_solver.distributions import *

class ActivityPrecedenceType(Enum):
    def __repr__(self):
        return str(self.value)
    PRE_SEQ = jpype.JPackage('jline').lang.constant.ActivityPrecedenceType.PRE_SEQ
    PRE_AND = jpype.JPackage('jline').lang.constant.ActivityPrecedenceType.PRE_AND
    PRE_OR = jpype.JPackage('jline').lang.constant.ActivityPrecedenceType.PRE_OR
    POST_SEQ = jpype.JPackage('jline').lang.constant.ActivityPrecedenceType.POST_SEQ
    POST_AND = jpype.JPackage('jline').lang.constant.ActivityPrecedenceType.POST_AND
    POST_OR = jpype.JPackage('jline').lang.constant.ActivityPrecedenceType.POST_OR
    POST_LOOP = jpype.JPackage('jline').lang.constant.ActivityPrecedenceType.POST_LOOP
    POST_CACHE = jpype.JPackage('jline').lang.constant.ActivityPrecedenceType.POST_CACHE

class CallType(Enum):
    def __repr__(self):
        return str(self.value)
    SYNC = jpype.JPackage('jline').lang.constant.CallType.SYNC
    ASYNC = jpype.JPackage('jline').lang.constant.CallType.ASYNC
    FWD = jpype.JPackage('jline').lang.constant.CallType.FWD

class DropStrategy(Enum):
    def __repr__(self):
        return str(self.value)
    WaitingQueue = jpype.JPackage('jline').lang.constant.DropStrategy.WaitingQueue
    Drop = jpype.JPackage('jline').lang.constant.DropStrategy.Drop
    BlockingAfterService = jpype.JPackage('jline').lang.constant.DropStrategy.BlockingAfterService

class EventType(Enum):
    def __repr__(self):
        return str(self.value)
    INIT = jpype.JPackage('jline').lang.constant.EventType.INIT
    LOCAL = jpype.JPackage('jline').lang.constant.EventType.LOCAL
    ARV = jpype.JPackage('jline').lang.constant.EventType.ARV
    DEP = jpype.JPackage('jline').lang.constant.EventType.DEP
    PHASE = jpype.JPackage('jline').lang.constant.EventType.PHASE
    READ = jpype.JPackage('jline').lang.constant.EventType.READ
    STAGE = jpype.JPackage('jline').lang.constant.EventType.STAGE

class JobClassType(Enum):
    def __repr__(self):
        return str(self.value)
    OPEN = jpype.JPackage('jline').lang.constant.JobClassType.OPEN
    CLOSED = jpype.JPackage('jline').lang.constant.JobClassType.CLOSED
    DISABLED = jpype.JPackage('jline').lang.constant.JobClassType.DISABLED

class JoinStrategy(Enum):
    def __repr__(self):
        return str(self.value)
    STD = jpype.JPackage('jline').lang.constant.JoinStrategy.STD
    PARTIAL = jpype.JPackage('jline').lang.constant.JoinStrategy.PARTIAL
    Quorum = jpype.JPackage('jline').lang.constant.JoinStrategy.Quorum
    Guard = jpype.JPackage('jline').lang.constant.JoinStrategy.Guard

class MetricType(Enum):
    def __repr__(self):
        return str(self.value)
    ResidT = jpype.JPackage('jline').lang.constant.MetricType.ResidT
    RespT = jpype.JPackage('jline').lang.constant.MetricType.RespT
    DropRate = jpype.JPackage('jline').lang.constant.MetricType.DropRate
    QLen = jpype.JPackage('jline').lang.constant.MetricType.QLen
    QueueT = jpype.JPackage('jline').lang.constant.MetricType.QueueT
    FCRWeight = jpype.JPackage('jline').lang.constant.MetricType.FCRWeight
    FCRMemOcc = jpype.JPackage('jline').lang.constant.MetricType.FCRMemOcc
    FJQLen = jpype.JPackage('jline').lang.constant.MetricType.FJQLen
    FJRespT = jpype.JPackage('jline').lang.constant.MetricType.FJRespT
    RespTSink = jpype.JPackage('jline').lang.constant.MetricType.RespTSink
    SysDropR = jpype.JPackage('jline').lang.constant.MetricType.SysDropR
    SysQLen = jpype.JPackage('jline').lang.constant.MetricType.SysQLen
    SysPower = jpype.JPackage('jline').lang.constant.MetricType.SysPower
    SysRespT = jpype.JPackage('jline').lang.constant.MetricType.SysRespT
    SysTput = jpype.JPackage('jline').lang.constant.MetricType.SysTput
    Tput = jpype.JPackage('jline').lang.constant.MetricType.Tput
    ArvR = jpype.JPackage('jline').lang.constant.MetricType.ArvR
    TputSink = jpype.JPackage('jline').lang.constant.MetricType.TputSink
    Util = jpype.JPackage('jline').lang.constant.MetricType.Util
    TranQLen = jpype.JPackage('jline').lang.constant.MetricType.TranQLen
    TranUtil = jpype.JPackage('jline').lang.constant.MetricType.TranUtil
    TranTput = jpype.JPackage('jline').lang.constant.MetricType.TranTput
    TranRespT = jpype.JPackage('jline').lang.constant.MetricType.TranRespT

class NodeType(Enum):
    def __repr__(self):
        return str(self.value)
    Transition = jpype.JPackage('jline').lang.constant.NodeType.Transition
    Place = jpype.JPackage('jline').lang.constant.NodeType.Place
    Fork = jpype.JPackage('jline').lang.constant.NodeType.Fork
    Router = jpype.JPackage('jline').lang.constant.NodeType.Router
    Cache = jpype.JPackage('jline').lang.constant.NodeType.Cache
    Logger = jpype.JPackage('jline').lang.constant.NodeType.Logger
    ClassSwitch = jpype.JPackage('jline').lang.constant.NodeType.ClassSwitch
    Delay = jpype.JPackage('jline').lang.constant.NodeType.Delay
    Source = jpype.JPackage('jline').lang.constant.NodeType.Source
    Sink = jpype.JPackage('jline').lang.constant.NodeType.Sink
    Join = jpype.JPackage('jline').lang.constant.NodeType.Join
    Queue = jpype.JPackage('jline').lang.constant.NodeType.Queue

    @staticmethod
    def fromJLine(obj):
        obj_str = str(obj)
        if obj_str == 'Transition':
            return NodeType.Transition
        elif obj_str == 'Place':
            return NodeType.Place
        elif obj_str == 'Fork':
            return NodeType.Fork
        elif obj_str == 'Router':
            return NodeType.Router
        elif obj_str == 'Cache':
            return NodeType.Cache
        elif obj_str == 'Logger':
            return NodeType.Logger
        elif obj_str == 'ClassSwitch':
            return NodeType.ClassSwitch
        elif obj_str == 'Delay':
            return NodeType.Delay
        elif obj_str == 'Source':
            return NodeType.Source
        elif obj_str == 'Sink':
            return NodeType.Sink
        elif obj_str == 'Join':
            return NodeType.Join
        elif obj_str == 'Queue':
            return NodeType.Queue

class ProcessType(Enum):
    def __repr__(self):
        return str(self.value)

    EXP = jpype.JPackage('jline').lang.constant.ProcessType.EXP
    ERLANG = jpype.JPackage('jline').lang.constant.ProcessType.ERLANG
    DISABLED = jpype.JPackage('jline').lang.constant.ProcessType.DISABLED
    IMMEDIATE = jpype.JPackage('jline').lang.constant.ProcessType.IMMEDIATE
    HYPEREXP = jpype.JPackage('jline').lang.constant.ProcessType.HYPEREXP
    APH = jpype.JPackage('jline').lang.constant.ProcessType.APH
    COXIAN = jpype.JPackage('jline').lang.constant.ProcessType.COXIAN
    PH = jpype.JPackage('jline').lang.constant.ProcessType.PH
    MAP = jpype.JPackage('jline').lang.constant.ProcessType.MAP
    UNIFORM = jpype.JPackage('jline').lang.constant.ProcessType.UNIFORM
    DET = jpype.JPackage('jline').lang.constant.ProcessType.DET
    GAMMA = jpype.JPackage('jline').lang.constant.ProcessType.GAMMA
    PARETO = jpype.JPackage('jline').lang.constant.ProcessType.PARETO
    WEIBULL = jpype.JPackage('jline').lang.constant.ProcessType.WEIBULL
    LOGNORMAL = jpype.JPackage('jline').lang.constant.ProcessType.LOGNORMAL
    MMPP2 = jpype.JPackage('jline').lang.constant.ProcessType.MMPP2
    REPLAYER = jpype.JPackage('jline').lang.constant.ProcessType.REPLAYER
    TRACE = jpype.JPackage('jline').lang.constant.ProcessType.TRACE
    COX2 = jpype.JPackage('jline').lang.constant.ProcessType.COX2
    BINOMIAL = jpype.JPackage('jline').lang.constant.ProcessType.BINOMIAL
    POISSON = jpype.JPackage('jline').lang.constant.ProcessType.POISSON

    @staticmethod
    def fromString(obj):
        obj_str = str(obj)
        if obj_str == "Exp":
            return ProcessType.EXP
        elif obj_str == "Erlang":
            return ProcessType.ERLANG
        elif obj_str == "HyperExp":
            return ProcessType.HYPEREXP
        elif obj_str == "PH":
            return ProcessType.PH
        elif obj_str == "APH":
            return ProcessType.APH
        elif obj_str == "MAP":
            return ProcessType.MAP
        elif obj_str == "Uniform":
            return ProcessType.UNIFORM
        elif obj_str == "Det":
            return ProcessType.DET
        elif obj_str == "Coxian":
            return ProcessType.COXIAN
        elif obj_str == "Gamma":
            return ProcessType.GAMMA
        elif obj_str == "Pareto":
            return ProcessType.PARETO
        elif obj_str == "MMPP2":
            return ProcessType.MMPP2
        elif obj_str == "Replayer":
            return ProcessType.REPLAYER
        elif obj_str == "Trace":
            return ProcessType.TRACE
        elif obj_str == "Immediate":
            return ProcessType.IMMEDIATE
        elif obj_str == "Disabled":
            return ProcessType.DISABLED
        elif obj_str == "Cox2":
            return ProcessType.COX2
        elif obj_str == "Weibull":
            return ProcessType.WEIBULL
        elif obj_str == "Lognormal":
            return ProcessType.LOGNORMAL
        elif obj_str == "Poisson":
            return ProcessType.POISSON
        elif obj_str == "Binomial":
            return ProcessType.BINOMIAL
        else:
            raise ValueError(f"Unsupported ProcessType: {obj}")

    def toDistribution(process_type, *args):
        if process_type == ProcessType.EXP:
            return Exp
        elif process_type == ProcessType.DET:
            return Det
        elif process_type == ProcessType.ERLANG:
            return Erlang
        elif process_type == ProcessType.HYPEREXP:
            return HyperExp
        elif process_type == ProcessType.UNIFORM:
            return Uniform
        elif process_type == ProcessType.IMMEDIATE:
            return Immediate
        elif process_type == ProcessType.DISABLED:
            return Disabled
        else:
            raise ValueError(f"Unsupported ProcessType: {process_type}")

class ReplacementStrategy(Enum):
    def __repr__(self):
        return str(self.value)
    RR = jpype.JPackage('jline').lang.constant.ReplacementStrategy.RR
    FIFO = jpype.JPackage('jline').lang.constant.ReplacementStrategy.FIFO
    SFIFO = jpype.JPackage('jline').lang.constant.ReplacementStrategy.SFIFO
    LRU = jpype.JPackage('jline').lang.constant.ReplacementStrategy.LRU

    def ordinal(self):
        return self.value.ordinal()

class RoutingStrategy(Enum):
    def __repr__(self):
        return str(self.value)
    RAND = jpype.JPackage('jline').lang.constant.RoutingStrategy.RAND
    PROB = jpype.JPackage('jline').lang.constant.RoutingStrategy.PROB
    RROBIN = jpype.JPackage('jline').lang.constant.RoutingStrategy.RROBIN
    WRROBIN = jpype.JPackage('jline').lang.constant.RoutingStrategy.WRROBIN
    JSQ = jpype.JPackage('jline').lang.constant.RoutingStrategy.JSQ
    DISABLED = jpype.JPackage('jline').lang.constant.RoutingStrategy.DISABLED
    FIRING = jpype.JPackage('jline').lang.constant.RoutingStrategy.FIRING
    KCHOICES = jpype.JPackage('jline').lang.constant.RoutingStrategy.KCHOICES

class SchedStrategy(Enum):

    def __repr__(self):
        return str(self.value)

    INF = jpype.JPackage('jline').lang.constant.SchedStrategy.INF
    FCFS = jpype.JPackage('jline').lang.constant.SchedStrategy.FCFS
    LCFS = jpype.JPackage('jline').lang.constant.SchedStrategy.LCFS
    LCFSPR = jpype.JPackage('jline').lang.constant.SchedStrategy.LCFSPR
    SIRO = jpype.JPackage('jline').lang.constant.SchedStrategy.SIRO
    SJF = jpype.JPackage('jline').lang.constant.SchedStrategy.SJF
    LJF = jpype.JPackage('jline').lang.constant.SchedStrategy.LJF
    PS = jpype.JPackage('jline').lang.constant.SchedStrategy.PS
    DPS = jpype.JPackage('jline').lang.constant.SchedStrategy.DPS
    GPS = jpype.JPackage('jline').lang.constant.SchedStrategy.GPS
    SEPT = jpype.JPackage('jline').lang.constant.SchedStrategy.SEPT
    LEPT = jpype.JPackage('jline').lang.constant.SchedStrategy.LEPT
    HOL = jpype.JPackage('jline').lang.constant.SchedStrategy.HOL
    FORK = jpype.JPackage('jline').lang.constant.SchedStrategy.FORK
    EXT = jpype.JPackage('jline').lang.constant.SchedStrategy.EXT
    REF = jpype.JPackage('jline').lang.constant.SchedStrategy.REF
    POLLING = jpype.JPackage('jline').lang.constant.SchedStrategy.POLLING
    PSPRIO = jpype.JPackage('jline').lang.constant.SchedStrategy.PSPRIO
    DPSPRIO = jpype.JPackage('jline').lang.constant.SchedStrategy.DPSPRIO
    GPSPRIO = jpype.JPackage('jline').lang.constant.SchedStrategy.GPSPRIO

    @staticmethod
    def fromString(obj):
        obj_str = str(obj)
        if obj_str == 'INF':
            return SchedStrategy.INF
        elif obj_str == 'FCFS':
            return SchedStrategy.FCFS
        elif obj_str == 'LCFS':
            return SchedStrategy.LCFS
        elif obj_str == 'LCFSPR':
            return SchedStrategy.LCFSPR
        elif obj_str == 'SIRO':
            return SchedStrategy.SIRO
        elif obj_str == 'SJF':
            return SchedStrategy.SJF
        elif obj_str == 'LJF':
            return SchedStrategy.LJF
        elif obj_str == 'PS':
            return SchedStrategy.PS
        elif obj_str == 'DPS':
            return SchedStrategy.DPS
        elif obj_str == 'GPS':
            return SchedStrategy.GPS
        elif obj_str == 'SEPT':
            return SchedStrategy.SEPT
        elif obj_str == 'LEPT':
            return SchedStrategy.LEPT
        elif obj_str == 'HOL':
            return SchedStrategy.HOL
        elif obj_str == 'FORK':
            return SchedStrategy.FORK
        elif obj_str == 'EXT':
            return SchedStrategy.EXT
        elif obj_str == 'REF':
            return SchedStrategy.REF
        elif obj_str == 'POLLING':
            return SchedStrategy.POLLING
        elif obj_str == 'PSPRIO':
            return SchedStrategy.PSPRIO
        elif obj_str == 'DPSPRIO':
            return SchedStrategy.DPSPRIO
        elif obj_str == 'GPSPRIO':
            return SchedStrategy.GPSPRIO
        else:
            raise ValueError(f"Unsupported SchedStrategy: {obj}")

    @staticmethod
    def fromLINEString(sched: str):
        return jpype.JPackage('jline').lang.constant.SchedStrategy.fromLINEString(sched.lower())

    @staticmethod
    def toID(sched):
        return int(jpype.JPackage('jline').lang.constant.SchedStrategy.toID(sched))

class SchedStrategyType(Enum):
    def __repr__(self):
        return str(self.value)
    PR = jpype.JPackage('jline').lang.constant.SchedStrategyType.PR
    PNR = jpype.JPackage('jline').lang.constant.SchedStrategyType.PNR
    NP = jpype.JPackage('jline').lang.constant.SchedStrategyType.NP
    NPPrio = jpype.JPackage('jline').lang.constant.SchedStrategyType.NPPrio

class ServiceStrategy(Enum):
    def __repr__(self):
        return str(self.value)
    LI = jpype.JPackage('jline').lang.constant.ServiceStrategy.LI
    LD = jpype.JPackage('jline').lang.constant.ServiceStrategy.LD
    CD = jpype.JPackage('jline').lang.constant.ServiceStrategy.CD
    SD = jpype.JPackage('jline').lang.constant.ServiceStrategy.SD

class SolverType(Enum):
    def __repr__(self):
        return str(self.value)
    AUTO = jpype.JPackage('jline').lang.constant.SolverType.AUTO
    CTMC = jpype.JPackage('jline').lang.constant.SolverType.CTMC
    ENV = jpype.JPackage('jline').lang.constant.SolverType.ENV
    FLUID = jpype.JPackage('jline').lang.constant.SolverType.FLUID
    JMT = jpype.JPackage('jline').lang.constant.SolverType.JMT
    LN = jpype.JPackage('jline').lang.constant.SolverType.LN
    LQNS = jpype.JPackage('jline').lang.constant.SolverType.LQNS
    MAM = jpype.JPackage('jline').lang.constant.SolverType.MAM
    MVA = jpype.JPackage('jline').lang.constant.SolverType.MVA
    NC = jpype.JPackage('jline').lang.constant.SolverType.NC
    QNS = jpype.JPackage('jline').lang.constant.SolverType.QNS
    SSA = jpype.JPackage('jline').lang.constant.SolverType.SSA

class TimingStrategy(Enum):
    def __repr__(self):
        return str(self.value)
    TIMED = jpype.JPackage('jline').lang.constant.TimingStrategy.TIMED
    IMMEDIATE = jpype.JPackage('jline').lang.constant.TimingStrategy.IMMEDIATE

class VerboseLevel(Enum):
    def __repr__(self):
        return str(self.value)
    SILENT = jpype.JPackage('jline').VerboseLevel.SILENT
    STD = jpype.JPackage('jline').VerboseLevel.STD
    DEBUG = jpype.JPackage('jline').VerboseLevel.DEBUG

class PollingType(Enum):
    def __repr__(self):
        return str(self.value)
    GATED = jpype.JPackage('jline').lang.constant.PollingType.GATED
    EXHAUSTIVE = jpype.JPackage('jline').lang.constant.PollingType.EXHAUSTIVE
    KLIMITED = jpype.JPackage('jline').lang.constant.PollingType.KLIMITED

    @staticmethod
    def fromString(obj):
        obj_str = str(obj).upper()
        if obj_str == 'GATED':
            return PollingType.GATED
        elif obj_str == 'EXHAUSTIVE':
            return PollingType.EXHAUSTIVE
        elif obj_str == 'KLIMITED' or obj_str == 'K-LIMITED':
            return PollingType.KLIMITED
        else:
            raise ValueError(f"Unsupported PollingType: {obj}")

class GlobalConstants:

    def __repr__(self):
        return f"GlobalConstants(Version={self.Version}, Verbose={self.getVerbose()})"

    Zero = jpype.JPackage('jline').GlobalConstants.Zero
    CoarseTol = jpype.JPackage('jline').GlobalConstants.CoarseTol
    FineTol = jpype.JPackage('jline').GlobalConstants.FineTol
    Immediate = jpype.JPackage('jline').GlobalConstants.Immediate
    MaxInt = jpype.JPackage('jline').GlobalConstants.MaxInt
    Version = jpype.JPackage('jline').GlobalConstants.Version
    DummyMode = jpype.JPackage('jline').GlobalConstants.DummyMode

    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    get_instance = getInstance

    @staticmethod
    def getVerbose():
        java_gc = jpype.JPackage('jline').GlobalConstants.getInstance()
        java_verbose = java_gc.getVerbose()

        if java_verbose == jpype.JPackage('jline').VerboseLevel.STD:
            return VerboseLevel.STD
        elif java_verbose == jpype.JPackage('jline').VerboseLevel.DEBUG:
            return VerboseLevel.DEBUG
        elif java_verbose == jpype.JPackage('jline').VerboseLevel.SILENT:
            return VerboseLevel.SILENT
        else:
            return VerboseLevel.STD

    get_verbose = getVerbose

    @staticmethod
    def setVerbose(verbosity):
        java_gc = jpype.JPackage('jline').GlobalConstants.getInstance()

        if verbosity == VerboseLevel.STD:
            java_gc.setVerbose(jpype.JPackage('jline').VerboseLevel.STD)
        elif verbosity == VerboseLevel.DEBUG:
            java_gc.setVerbose(jpype.JPackage('jline').VerboseLevel.DEBUG)
        elif verbosity == VerboseLevel.SILENT:
            java_gc.setVerbose(jpype.JPackage('jline').VerboseLevel.SILENT)
        else:
            raise ValueError(f"Invalid verbosity level: {verbosity}. Must be one of VerboseLevel.SILENT, VerboseLevel.STD, or VerboseLevel.DEBUG")

    set_verbose = setVerbose

    @classmethod
    def getConstants(cls):
        return {
            'Zero': cls.Zero,
            'CoarseTol': cls.CoarseTol,
            'FineTol': cls.FineTol,
            'Immediate': cls.Immediate,
            'MaxInt': cls.MaxInt,
            'Version': cls.Version,
            'DummyMode': cls.DummyMode,
            'Verbose': cls.getVerbose()
        }

    get_constants = getConstants
