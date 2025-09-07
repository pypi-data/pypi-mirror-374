
import jpype
import jpype.imports
import numpy as np
from pprint import pprint, pformat
from types import SimpleNamespace
from . import jlineMatrixZeros, jlineMatrixSingleton

from . import jlineMatrixToArray, jlineMapMatrixToArray, jlineMatrixFromArray
from .constants import *


class JobClass:
    def __init__(self):
        pass

    def __index__(self):
        return int(self.obj.getIndex()) - 1

    def getIndex(self):
        return int(self.obj.getIndex())

    def getNumberOfJobs(self):
        return self.obj.getNumberOfJobs()

    def getName(self):
        return self.obj.getName()

    def getPriority(self):
        return self.obj.getPriority()

    def index(self):
        """Kotlin-style alias for getIndex"""
        return self.getIndex()

    def numberOfJobs(self):
        """Kotlin-style alias for getNumberOfJobs"""
        return self.getNumberOfJobs()

    def name(self):
        """Kotlin-style alias for getName"""
        return self.getName()

    def priority(self):
        """Kotlin-style alias for getPriority"""
        return self.getPriority()

    get_index = getIndex
    get_number_of_jobs = getNumberOfJobs
    get_name = getName
    get_priority = getPriority


class Node:
    def __init__(self):
        pass

    def setRouting(self, jobclass, strategy, destination=None, probability=None):
        if destination is not None and probability is not None:
            self.obj.setRouting(jobclass.obj, strategy.value, destination.obj, probability)
        else:
            self.obj.setRouting(jobclass.obj, strategy.value)

    def setProbRouting(self, jobclass, node, prob):
        self.obj.setProbRouting(jobclass.obj, node.obj, prob)

    def getName(self):
        return self.obj.getName()

    def __index__(self):
        return int(self.obj.getNodeIndex())

    def name(self):
        """Kotlin-style alias for getName"""
        return self.getName()

    set_routing = setRouting
    set_prob_routing = setProbRouting
    get_name = getName
    name = getName

class Station(Node):
    def __init__(self):
        super().__init__()

    def setState(self, state):
        """Set initial state for this station."""
        if hasattr(state, 'obj'):
            self.obj.setState(state.obj)
        else:
            from . import jlineMatrixFromArray
            self.obj.setState(jlineMatrixFromArray(state))

    set_state = setState


class RoutingMatrix:
    def __init__(self, rt, network=None):
        self.obj = rt
        self.network = network
        self._nodes_cache = None

    def _get_node_by_index(self, index):
        """Convert node index to node object."""
        if self.network is None:
            raise ValueError("Network reference not available for node index conversion")

        if self._nodes_cache is None:
            self._nodes_cache = self.network.getNodes()

        if isinstance(index, int):
            if 0 <= index < len(self._nodes_cache):
                return self._nodes_cache[index]
            else:
                raise IndexError(f"Node index {index} out of range (0-{len(self._nodes_cache)-1})")
        else:
            return index

    def set(self, *argv):
        if len(argv) == 5:
            class_source = argv[0]
            class_dest = argv[1]
            stat_source = argv[2]
            stat_dest = argv[3]
            prob = argv[4]

            stat_source_node = self._get_node_by_index(stat_source)
            stat_dest_node = self._get_node_by_index(stat_dest)

            return self.obj.set(class_source.obj, class_dest.obj, stat_source_node.obj, stat_dest_node.obj, prob)
        elif len(argv) == 3:
            class_source = argv[0]
            class_dest = argv[1]
            rt = argv[2]
            if isinstance(rt, RoutingMatrix):
                self.obj.set(class_source.obj, class_dest.obj, rt.obj)
            else:
                self.obj.set(class_source.obj, class_dest.obj, jlineMatrixFromArray(rt))
            return self.obj
        elif len(argv) == 2:
            jobclass = argv[0]
            rt = argv[1]
            if isinstance(rt, RoutingMatrix):
                return self.obj.set(jobclass.obj, rt.obj)
            else:
                return self.obj.set(jobclass.obj, jlineMatrixFromArray(rt))
        else:
            raise ValueError(f"Unsupported number of arguments: {len(argv)}. Expected 2, 3, or 5 arguments.")

    def setRoutingMatrix(self, jobclass, node, pmatrix):
        if isinstance(jobclass, JobClass):
            for i in range(len(node)):
                for j in range(len(node)):
                    self.set(jobclass, jobclass, node[i], node[j], pmatrix[i][j])
        else:
            for i in range(len(node)):
                for j in range(len(node)):
                    for k in range(len(jobclass)):
                        self.set(jobclass[k], jobclass[k], node[i], node[j], pmatrix[k][i][j])

    def __setitem__(self, key, value):
        if isinstance(key, tuple) and len(key) == 1:
            source_jobclass = dest_jobclass = key[0]
        elif isinstance(key, tuple) and len(key) == 2:
            source_jobclass, dest_jobclass = key
        elif not isinstance(key, tuple):
            source_jobclass = dest_jobclass = key
        else:
            raise ValueError("Key must be a single jobclass or tuple of (source_jobclass, dest_jobclass)")

        if not (hasattr(source_jobclass, 'obj') and hasattr(dest_jobclass, 'obj')):
            raise ValueError("Key elements must be JobClass objects")

        import numpy as np
        if not isinstance(value, np.ndarray):
            value = np.array(value)

        if len(value.shape) != 2:
            raise ValueError("Value must be a 2D array representing routing probabilities")

        if self.network is None:
            raise ValueError("Network reference not available for node index conversion")

        if self._nodes_cache is None:
            self._nodes_cache = self.network.getNodes()

        num_nodes = len(self._nodes_cache)

        if value.shape[0] != num_nodes or value.shape[1] != num_nodes:
            raise ValueError(f"Routing matrix must be {num_nodes}x{num_nodes} to match network topology")

        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                if value[i, j] != 0:
                    source_node = self._nodes_cache[i]
                    dest_node = self._nodes_cache[j]
                    self.set(source_jobclass, dest_jobclass, source_node, dest_node, float(value[i, j]))

    def addRoute(self, jobclass, *args):
        if len(args) < 2:
            raise ValueError("addRoute requires at least 2 nodes (source and destination)")

        if len(args) >= 2 and isinstance(args[-1], (int, float)) and not hasattr(args[-1], 'obj'):
            nodes = args[:-1]
            probability = args[-1]
        else:
            nodes = args
            probability = 1.0

        if len(nodes) < 2:
            raise ValueError("addRoute requires at least 2 nodes (source and destination)")

        for i in range(len(nodes) - 1):
            self.set(jobclass, jobclass, nodes[i], nodes[i + 1], probability)

    set_routing_matrix = setRoutingMatrix
    add_route = addRoute


class Model:
    def __init__(self):
        pass

    def getName(self):
        return self.obj.getName()

    def setName(self, name):
        self.obj.setName(name)

    def getVersion(self):
        return self.obj.getVersion()

    get_name = getName
    set_name = setName
    get_version = getVersion
    name = getName
    version = getVersion


class NetworkStruct():
    def __str__(self):
        return pformat(vars(self))

    def fromJline(self, jsn):
        self.obj = jsn

        self.nstations = int(jsn.nstations)
        self.nstateful = int(jsn.nstateful)
        self.nnodes = int(jsn.nnodes)
        self.nclasses = int(jsn.nclasses)
        self.nclosedjobs = int(jsn.nclosedjobs)
        self.nchains = int(jsn.nchains)
        self.refstat = jlineMatrixToArray(jsn.refstat)
        self.njobs = jlineMatrixToArray(jsn.njobs)
        self.nservers = jlineMatrixToArray(jsn.nservers)
        self.connmatrix = jlineMatrixToArray(jsn.connmatrix)
        self.scv = jlineMatrixToArray(jsn.scv)
        self.isstation = jlineMatrixToArray(jsn.isstation)
        self.isstateful = jlineMatrixToArray(jsn.isstateful)
        self.isstatedep = jlineMatrixToArray(jsn.isstatedep)
        self.nodeToStateful = jlineMatrixToArray(jsn.nodeToStateful)
        self.nodeToStation = jlineMatrixToArray(jsn.nodeToStation)
        self.stationToNode = jlineMatrixToArray(jsn.stationToNode)
        self.stationToStateful = jlineMatrixToArray(jsn.stationToStateful)
        self.statefulToStation = jlineMatrixToArray(jsn.statefulToStation)
        self.statefulToNode = jlineMatrixToArray(jsn.statefulToNode)
        self.rates = jlineMatrixToArray(jsn.rates)
        self.classprio = jlineMatrixToArray(jsn.classprio)
        self.phases = jlineMatrixToArray(jsn.phases)
        self.phasessz = jlineMatrixToArray(jsn.phasessz)
        self.phaseshift = jlineMatrixToArray(jsn.phaseshift)
        self.schedparam = jlineMatrixToArray(jsn.schedparam)
        self.chains = jlineMatrixToArray(jsn.chains)
        self.rt = jlineMatrixToArray(jsn.rt)
        self.nvars = jlineMatrixToArray(jsn.nvars)
        self.rtnodes = jlineMatrixToArray(jsn.rtnodes)
        self.csmask = jlineMatrixToArray(jsn.csmask)
        self.isslc = jlineMatrixToArray(jsn.isslc)
        self.cap = jlineMatrixToArray(jsn.cap)
        self.refclass = jlineMatrixToArray(jsn.refclass)
        self.lldscaling = jlineMatrixToArray(jsn.lldscaling)
        self.fj = jlineMatrixToArray(jsn.fj)
        self.classcap = jlineMatrixToArray(jsn.classcap)
        self.inchain = jlineMapMatrixToArray(jsn.inchain)
        self.visits = jlineMapMatrixToArray(jsn.visits)
        self.nodevisits = jlineMapMatrixToArray(jsn.nodevisits)
        self.classnames = tuple(jsn.classnames)
        self.nodetype = tuple(map(lambda x: NodeType.fromJLine(x), jsn.nodetype))
        self.nodenames = tuple(jsn.nodenames)

        sched = np.empty(int(jsn.nstations), dtype=object)
        space = np.empty(int(jsn.nstations), dtype=object)
        mu = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses)), dtype=object)
        phi = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses)), dtype=object)
        pie = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses)), dtype=object)
        proctype = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses)), dtype=object)
        droprule = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses)), dtype=object)
        proc = np.empty(shape=(int(jsn.nstations), int(jsn.nclasses), 2), dtype=object)
        routing = np.empty(shape=(int(jsn.nnodes), int(jsn.nclasses)), dtype=object)
        nodeparam = np.empty(int(jsn.nnodes), dtype=object)
        for ist in range(int(jsn.nstations)):
            sched[ist] = SchedStrategy(jsn.sched.get(jsn.stations[ist])).name
            space[ist] = jlineMatrixToArray(jsn.space.get(jsn.stations[ist]))
            for jcl in range(int(jsn.nclasses)):
                mu[ist, jcl] = jlineMatrixToArray(jsn.mu.get(jsn.stations[ist]).get(jsn.jobclasses[jcl]))
                phi[ist, jcl] = jlineMatrixToArray(jsn.phi.get(jsn.stations[ist]).get(jsn.jobclasses[jcl]))
                pie[ist, jcl] = jlineMatrixToArray(jsn.pie.get(jsn.stations[ist]).get(jsn.jobclasses[jcl]))
                proctype[ist, jcl] = ProcessType(jsn.proctype.get(jsn.stations[ist]).get(jsn.jobclasses[jcl])).name
                droprule[ist, jcl] = DropStrategy(jsn.droprule.get(jsn.stations[ist]).get(jsn.jobclasses[jcl])).name
                proc[ist, jcl, 0] = jlineMatrixToArray(jsn.proc.get(jsn.stations[ist]).get(jsn.jobclasses[jcl]).get(0))
                proc[ist, jcl, 1] = jlineMatrixToArray(jsn.proc.get(jsn.stations[ist]).get(jsn.jobclasses[jcl]).get(1))

        for ind in range(int(jsn.nnodes)):
            nodeparam[ind] = NodeParam(jsn.nodeparam.get(jsn.nodes[ind]))
            for jcl in range(int(jsn.nclasses)):
                routing[ind, jcl] = RoutingStrategy(jsn.routing.get(jsn.nodes[ind]).get(jsn.jobclasses[jcl])).name

        self.nodeparam = nodeparam
        self.sched = sched
        self.space = space
        self.mu = mu
        self.phi = phi
        self.pie = pie
        self.proctype = proctype
        self.routing = routing
        self.droprule = droprule
        self.proc = proc

        self.state = np.empty(int(jsn.nstateful), dtype=object)
        self.stateprior = np.empty(int(jsn.nstateful), dtype=object)
        for isf in range(int(jsn.nstateful)):
            self.state[isf] = jlineMatrixToArray(jsn.state.get(jsn.stateful.get(isf)))
            if jsn.stateprior is not None and jsn.stateprior.get(jsn.stateful.get(isf)) is not None:
                self.stateprior[isf] = jlineMatrixToArray(jsn.stateprior.get(jsn.stateful.get(isf)))
        
        # Additional Java fields not previously exposed in Python
        self.varsparam = jlineMatrixToArray(jsn.varsparam) if hasattr(jsn, 'varsparam') and jsn.varsparam is not None else None
        
        # Map fields that need special handling
        self.cdscaling = {}
        if hasattr(jsn, 'cdscaling') and jsn.cdscaling is not None:
            for station in jsn.stations:
                if jsn.cdscaling.get(station) is not None:
                    self.cdscaling[station.getName()] = jsn.cdscaling.get(station)
        
        self.gsync = {}
        if hasattr(jsn, 'gsync') and jsn.gsync is not None:
            for key in jsn.gsync.keySet():
                self.gsync[int(key)] = jsn.gsync.get(key)
        
        self.lst = {}
        if hasattr(jsn, 'lst') and jsn.lst is not None:
            for station in jsn.stations:
                if jsn.lst.get(station) is not None:
                    self.lst[station.getName()] = {}
                    for jobclass in jsn.jobclasses:
                        if jsn.lst.get(station).get(jobclass) is not None:
                            self.lst[station.getName()][jobclass.getName()] = jsn.lst.get(station).get(jobclass)
        
        self.rtorig = {}
        if hasattr(jsn, 'rtorig') and jsn.rtorig is not None:
            for jc1 in jsn.jobclasses:
                if jsn.rtorig.get(jc1) is not None:
                    self.rtorig[jc1.getName()] = {}
                    for jc2 in jsn.jobclasses:
                        if jsn.rtorig.get(jc1).get(jc2) is not None:
                            self.rtorig[jc1.getName()][jc2.getName()] = jlineMatrixToArray(jsn.rtorig.get(jc1).get(jc2))
        
        self.sync = {}
        if hasattr(jsn, 'sync') and jsn.sync is not None:
            for key in jsn.sync.keySet():
                self.sync[int(key)] = jsn.sync.get(key)
        
        self.rtfun = jsn.rtfun if hasattr(jsn, 'rtfun') and jsn.rtfun is not None else None


    def print(self):
        if hasattr(self, 'obj') and self.obj is not None:
            self.obj.print_()
        else:
            raise RuntimeError("No Java NetworkStruct object available")

def NodeParam(jnodeparam):
    if jnodeparam is None or jnodeparam.isEmpty():
        return None

    typename = jnodeparam.getClass().getSimpleName()

    if typename == 'CacheNodeParam':
        return CacheNodeParam(jnodeparam)
    elif typename == 'ForkNodeParam':
        return ForkNodeParam(jnodeparam)
    elif typename == 'JoinNodeParam':
        return JoinNodeParam(jnodeparam)
    elif typename == 'RoutingNodeParam':
        return RoutingNodeParam(jnodeparam)
    elif typename == 'TransitionNodeParam':
        return TransitionNodeParam(jnodeparam)
    elif typename == 'ReplayerNodeParam':
        return ReplayerNodeParam(jnodeparam)
    elif typename == 'LoggerNodeParam':
        return LoggerNodeParam(jnodeparam)
    else:
        raise NotImplementedError(f'Unrecognized NodeParam type: {typename}')

class NodeParamBase:
    def __init__(self, jnodeparam, jclasses=None):
        self.jnodeparam = jnodeparam

        self.weights = self._extract_class_matrix_map(jnodeparam.weights, jclasses)
        self.outlinks = self._extract_class_matrix_map(jnodeparam.outlinks, jclasses)
        self.withMemory = self._extract_class_matrix_map(jnodeparam.withMemory, jclasses)
        self.k = self._extract_class_int_map(jnodeparam.k, jclasses)

    def _extract_class_matrix_map(self, jmap, jclasses):
        if jmap is None or jclasses is None:
            return None
        result = {}
        for i in range(jclasses.size()):
            jclass = jclasses.get(i)
            if jmap.containsKey(jclass):
                result[str(jclass.getName())] = jlineMatrixToArray(jmap.get(jclass))
        return result if result else None

    def _extract_class_int_map(self, jmap, jclasses):
        if jmap is None or jclasses is None:
            return None
        result = {}
        for i in range(jclasses.size()):
            jclass = jclasses.get(i)
            if jmap.containsKey(jclass):
                result[str(jclass.getName())] = int(jmap.get(jclass))
        return result if result else None


class CacheNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)

        self.nitems = jnodeparam.nitems
        self.hitclass = jlineMatrixToArray(jnodeparam.hitclass)
        self.missclass = jlineMatrixToArray(jnodeparam.missclass)
        self.itemcap = jlineMatrixToArray(jnodeparam.itemcap)

        self.accost = [
            [jlineMatrixToArray(cell) if cell is not None else None for cell in row]
            for row in jnodeparam.accost
        ] if jnodeparam.accost is not None else None

        self.pread = {
            int(key): [float(v) for v in jnodeparam.pread.get(key)]
            for key in jnodeparam.pread.keySet()
        } if jnodeparam.pread is not None else None

        self.rpolicy = jnodeparam.rpolicy.name() if jnodeparam.rpolicy else None
        self.actualhitprob = jlineMatrixToArray(jnodeparam.actualhitprob)
        self.actualmissprob = jlineMatrixToArray(jnodeparam.actualmissprob)


class ForkNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)
        self.fanOut = jnodeparam.fanOut


class JoinNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)
        self.joinStrategy = jnodeparam.joinStrategy
        self.fanIn = jnodeparam.fanIn
        self.joinRequired = jnodeparam.joinRequired


class RoutingNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)
        self.weights = jnodeparam.weights
        self.outlinks = jnodeparam.outlinks
        self.withMemory = jnodeparam.withMemory
        self.k = jnodeparam.k


class TransitionNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)
        self.nmodes = jnodeparam.nmodes
        self.enabling = jnodeparam.enabling
        self.inhibiting = jnodeparam.inhibiting
        self.modenames = jnodeparam.modenames
        self.nmodeservers = jnodeparam.nmodeservers
        self.firing = jnodeparam.firing
        self.firingphases = jnodeparam.firingphases
        self.firingpie = jnodeparam.firingpie
        self.firingprocid = jnodeparam.firingprocid
        self.firingproc = jnodeparam.firingproc
        self.firingprio = jnodeparam.firingprio
        self.fireweight = jnodeparam.fireweight

class ReplayerNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)
        self.fileName = jnodeparam.fileName
        self.filePath = jnodeparam.filePath

class LoggerNodeParam(NodeParamBase):
    def __init__(self, jnodeparam):
        super().__init__(jnodeparam)
        self.fileName = jnodeparam.fileName
        self.filePath = jnodeparam.filePath
        self.startTime = jnodeparam.startTime
        self.loggerName = jnodeparam.loggerName
        self.timestamp = jnodeparam.timestamp
        self.jobID = jnodeparam.jobID
        self.jobClass = jnodeparam.jobClass
        self.timeSameClass = jnodeparam.timeSameClass
        self.timeAnyClass = jnodeparam.timeAnyClass


class Network(Model):

    def __init__(self, *argv):
        super().__init__()
        if isinstance(argv[0], jpype.JPackage('jline').lang.Network):
            self.obj = argv[0]
        else:
            name = argv[0]
            self.obj = jpype.JPackage('jline').lang.Network(name)

    def serialRouting(*argv):
        ctr = 0
        if len(argv) == 1:
            rtlist = jpype.JPackage('jline').lang.nodes.Node[len(argv[0])]
            for arg in argv[0]:
                rtlist[ctr] = jpype.JObject(arg.obj, 'jline.lang.nodes.Node')
                ctr += 1
        else:
            rtlist = jpype.JPackage('jline').lang.nodes.Node[len(argv)]
            for arg in argv:
                rtlist[ctr] = jpype.JObject(arg.obj, 'jline.lang.nodes.Node')
                ctr += 1

        return RoutingMatrix(jpype.JPackage('jline').lang.Network.serialRouting(rtlist))

    def reset(self, hard=True):
        self.obj.reset(hard)

    def link(self, routing):
        if isinstance(routing, dict):
            rt = self.init_routing_matrix()
            for (class_src, class_dst), prob_matrix in routing.items():
                rt.set(class_src, class_dst, prob_matrix)
            self.obj.link(rt.obj)
        else:
            self.obj.link(routing.obj)

    def relink(self, routing):
        self.obj.relink(routing.obj)

    def addLink(self, source, dest):
        self.obj.addLink(source.obj, dest.obj)

    add_link = addLink

    def initRoutingMatrix(self):
        rt = self.obj.initRoutingMatrix()
        return RoutingMatrix(rt, self)

    init_routing_matrix = initRoutingMatrix

    def getNumberOfNodes(self):
        return self.obj.getNumberOfNodes()

    def getNumberOfStations(self):
        return self.obj.getNumberOfStations()

    def getNumberOfClasses(self):
        return self.obj.getNumberOfClasses()

    def getClasses(self):
        try:
            java_classes = self.obj.getClasses()
            python_classes = []

            for java_class in java_classes:
                class_type = java_class.getJobClassType()

                if str(class_type) == 'OPEN':
                    py_class = OpenClass.__new__(OpenClass)
                    py_class.obj = java_class
                elif str(class_type) == 'CLOSED':
                    py_class = ClosedClass.__new__(ClosedClass)
                    py_class.obj = java_class
                else:
                    py_class = JobClass.__new__(JobClass)
                    py_class.obj = java_class

                python_classes.append(py_class)

            return python_classes

        except Exception as e:
            print(f"Warning: Could not get job classes from Java: {e}")
            return []

    def getNodeIndex(self, node):
        return self.obj.getNodeIndex(node.obj)

    def getStationIndex(self, station):
        return self.obj.getStationIndex(station.obj)

    def getStatefulIndex(self, stateful):
        return self.obj.getStatefulIndex(stateful.obj)

    def getJobClassIndex(self, jobclass):
        return self.obj.getJobClassIndex(jobclass.obj)

    def getChainIndex(self, chain):
        if isinstance(chain, int):
            return self.obj.getChainIndex(chain)
        else:
            return self.obj.getChainIndex(chain.obj)

    def getNumberOfJobs(self):
        """Get the number of jobs for each class as a matrix/array."""
        from . import jlineMatrixToArray
        return jlineMatrixToArray(self.obj.getNumberOfJobs())

    def getNodes(self):
        """Get all nodes in the network as a list."""
        jnodes = self.obj.getNodes()
        nodes = []
        for i in range(jnodes.size()):
            jnode = jnodes.get(i)
            node_type = str(jnode.getClass().getSimpleName())
            if node_type == "Queue":
                queue = Queue.__new__(Queue)
                queue.obj = jnode
                nodes.append(queue)
            elif node_type == "Delay":
                delay = Delay.__new__(Delay)
                delay.obj = jnode
                nodes.append(delay)
            elif node_type == "Source":
                source = Source.__new__(Source)
                source.obj = jnode
                nodes.append(source)
            elif node_type == "Sink":
                sink = Sink.__new__(Sink)
                sink.obj = jnode
                nodes.append(sink)
            elif node_type == "ClassSwitch":
                classswitch = ClassSwitch.__new__(ClassSwitch)
                classswitch.obj = jnode
                nodes.append(classswitch)
            elif node_type == "Fork":
                fork = Fork.__new__(Fork)
                fork.obj = jnode
                nodes.append(fork)
            elif node_type == "Join":
                join = Join.__new__(Join)
                join.obj = jnode
                nodes.append(join)
            else:
                node = Node()
                node.obj = jnode
                nodes.append(node)
        return nodes

    @property
    def nodes(self):
        """Property to access nodes like test_qnet.nodes"""
        return self.getNodes()

    def getTranHandles(self):
        Qt, Ut, Tt = self.obj.getTranHandles()
        return Qt, Ut, Tt

    def jsimgView(self):
        from line_solver import SolverJMT
        SolverJMT(self).jsimgView()

    def jsimwView(self):
        from line_solver import SolverJMT
        SolverJMT(self).jsimgView()

    def addLinks(self, linkPairs):
        for i in range(len(linkPairs)):
            self.obj.addLink(linkPairs[i][0].obj, linkPairs[i][1].obj)

    def getStruct(self, force=True):
        jsn = self.obj.getStruct(force)
        sn = NetworkStruct()
        sn.fromJline(jsn)
        return sn

    def printStruct(self, force=True):
        sn = self.getStruct(force)
        sn.print()

    def getState(self):
        """Get the initial state of the network"""
        return State(self.obj.getState())

    def refreshStruct(self, hard=True):
        self.obj.refreshStruct(hard)

    def printRoutingMatrix(self):
        self.obj.printRoutingMatrix()

    def getProductFormParameters(self):
        ret = self.obj.getProductFormParameters()
        return jlineMatrixToArray(ret.lambda_), jlineMatrixToArray(ret.D), jlineMatrixToArray(
            ret.N), jlineMatrixToArray(ret.Z), jlineMatrixToArray(ret.mu), jlineMatrixToArray(
            ret.S), jlineMatrixToArray(ret.V)

    def getGraph(self):
        try:
            import networkx as nx
        except ImportError:
            raise ImportError("NetworkX is required for graph functionality. Install with: pip install networkx")

        sn = self.getStruct()

        P, Pnodes = self._getRoutingMatrix()

        G = {'nodes': [], 'edges': []}

        for ist in range(sn.nnodes):
            node_info = {
                'id': ist,
                'name': sn.nodenames[ist] if ist < len(sn.nodenames) else f'Node{ist}',
                'type': sn.nodetype[ist].name if ist < len(sn.nodetype) else 'Unknown',
                'servers': int(sn.nservers[ist]) if ist < len(sn.nservers) else 0
            }
            G['nodes'].append(node_info)

        for ist in range(sn.nnodes):
            for jst in range(sn.nnodes):
                for k in range(sn.nclasses):
                    idx1 = ist * sn.nclasses + k
                    idx2 = jst * sn.nclasses + k
                    if idx1 < Pnodes.shape[0] and idx2 < Pnodes.shape[1] and Pnodes[idx1, idx2] > 0:
                        edge_info = {
                            'source': ist,
                            'target': jst,
                            'weight': float(Pnodes[idx1, idx2]),
                            'class': k
                        }
                        G['edges'].append(edge_info)

        H = {'nodes': [], 'edges': []}

        for ind in range(sn.nstations):
            jobs = 0
            for k in range(sn.nclasses):
                if k < len(sn.refstat) and sn.refstat[k] == ind + 1:
                    if k < len(sn.njobs):
                        jobs += sn.njobs[k]

            node_info = {
                'id': ind,
                'name': sn.nodenames[ind] if ind < len(sn.nodenames) else f'Station{ind}',
                'type': sn.nodetype[ind].name if ind < len(sn.nodetype) else 'Unknown',
                'jobs': int(jobs),
                'servers': int(sn.nservers[ind]) if ind < len(sn.nservers) else 0
            }
            H['nodes'].append(node_info)

        for ind in range(sn.nstations):
            for jnd in range(sn.nstations):
                for k in range(sn.nclasses):
                    idx1 = ind * sn.nclasses + k
                    idx2 = jnd * sn.nclasses + k
                    if idx1 < P.shape[0] and idx2 < P.shape[1] and P[idx1, idx2] > 0:
                        edge_info = {
                            'source': ind,
                            'target': jnd,
                            'weight': float(P[idx1, idx2]),
                            'rate': float(sn.rates[ind, k]) if ind < sn.rates.shape[0] and k < sn.rates.shape[1] else 0.0,
                            'class': sn.classnames[k] if k < len(sn.classnames) else f'Class{k}'
                        }
                        H['edges'].append(edge_info)

        return H, G

    def _getRoutingMatrix(self):
        try:
            classes = self.getClasses()
            if not classes:
                return np.array([[]]), np.array([[]])

            arvRates = jlineMatrixZeros(1, len(classes))

            result = self.obj.getRoutingMatrix(arvRates, 4)

            P = jlineMatrixToArray(result.rt) if result.rt is not None else np.array([[]])
            Pnodes = jlineMatrixToArray(result.rtnodes) if result.rtnodes is not None else np.array([[]])

            return P, Pnodes

        except Exception as e:
            print(f"Warning: Could not get routing matrix from Java: {e}")
            return np.array([[]]), np.array([[]])

    def plot(self, graph_type='station', method='names', **kwargs):
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
        except ImportError:
            raise ImportError("Matplotlib and NetworkX are required for plotting. Install with: pip install matplotlib networkx")

        H, G = self.getGraph()

        graph_data = H if graph_type == 'station' else G

        nx_graph = nx.DiGraph()

        node_labels = {}
        for node in graph_data['nodes']:
            nx_graph.add_node(node['id'])
            if method == 'names':
                node_labels[node['id']] = node['name']
            elif method == 'types':
                node_labels[node['id']] = node['type']
            else:
                node_labels[node['id']] = str(node['id'])

        for edge in graph_data['edges']:
            nx_graph.add_edge(edge['source'], edge['target'], weight=edge['weight'])

        plt.figure(figsize=kwargs.get('figsize', (12, 8)))

        try:
            pos = nx.nx_agraph.graphviz_layout(nx_graph, prog='dot')
        except:
            pos = nx.spring_layout(nx_graph, k=3, iterations=50)

        nx.draw(nx_graph, pos,
                with_labels=True,
                labels=node_labels,
                node_color=kwargs.get('node_color', 'lightblue'),
                node_size=kwargs.get('node_size', 1000),
                font_size=kwargs.get('font_size', 8),
                font_weight=kwargs.get('font_weight', 'bold'),
                arrows=True,
                edge_color=kwargs.get('edge_color', 'gray'),
                arrowsize=kwargs.get('arrowsize', 20))

        plt.title(f'{graph_type.capitalize()} Graph - {self.getName()}',
                 fontsize=kwargs.get('title_fontsize', 14))
        plt.axis('off')

        if kwargs.get('show', True):
            plt.show()

        return plt.gcf()


    @staticmethod
    def tandemPsInf(lam, D, Z):
        return Network(
            jpype.JPackage('jline').lang.Network.tandemPsInf(jlineMatrixFromArray(lam), jlineMatrixFromArray(D),
                                                             jlineMatrixFromArray(Z)))

    @staticmethod
    def tandemFcfsInf(lam, D, Z):
        return Network(
            jpype.JPackage('jline').lang.Network.tandemFcfsInf(jlineMatrixFromArray(lam), jlineMatrixFromArray(D),
                                                               jlineMatrixFromArray(Z)))

    @staticmethod
    def tandemPs(lam, D):
        return Network(
            jpype.JPackage('jline').lang.Network.tandemPs(jlineMatrixFromArray(lam), jlineMatrixFromArray(D)))

    @staticmethod
    def tandemFcfs(lam, D):
        return Network(
            jpype.JPackage('jline').lang.Network.tandemFcfs(jlineMatrixFromArray(lam), jlineMatrixFromArray(D)))

    @staticmethod
    def cyclicPsInf(N, D, Z, S=None):
        if S is None:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicPsInf(jlineMatrixFromArray(N), jlineMatrixFromArray(D),
                                                                jlineMatrixFromArray(Z)))
        else:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicPsInf(jlineMatrixFromArray(N), jlineMatrixFromArray(D),
                                                                jlineMatrixFromArray(Z), jlineMatrixFromArray(S)))

    @staticmethod
    def cyclicFcfsInf(N, D, Z, S=None):
        if S is None:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicFcfsInf(jlineMatrixFromArray(N), jlineMatrixFromArray(D),
                                                                   jlineMatrixFromArray(Z)))
        else:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicFcfsInf(jlineMatrixFromArray(N), jlineMatrixFromArray(D),
                                                                   jlineMatrixFromArray(Z), jlineMatrixFromArray(S)))

    @staticmethod
    def cyclicPs(N, D, S=None):
        if S is None:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicPs(jlineMatrixFromArray(N), jlineMatrixFromArray(D)))
        else:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicPs(jlineMatrixFromArray(N), jlineMatrixFromArray(D),
                                                              jlineMatrixFromArray(S)))

    @staticmethod
    def cyclicFcfs(N, D, S=None):
        if S is None:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicFcfs(jlineMatrixFromArray(N), jlineMatrixFromArray(D)))
        else:
            return Network(
                jpype.JPackage('jline').lang.Network.cyclicFcfs(jlineMatrixFromArray(N), jlineMatrixFromArray(D),
                                                                jlineMatrixFromArray(S)))

    def initDefault(self, nodes=None):
        if nodes is None:
            self.obj.initDefault()
        else:
            from . import jlineMatrixFromArray
            node_array = jlineMatrixFromArray([nodes]) if isinstance(nodes, list) else nodes
            self.obj.initDefault(node_array)

    init_default = initDefault

    def initFromMarginal(self, n, options=None):
        from . import jlineMatrixFromArray
        from .solvers import SolverOptions

        if options is None:
            from .solvers import Solver
            options = Solver.defaultOptions()

        n_matrix = jlineMatrixFromArray(n)
        self.obj.initFromMarginal(n_matrix, options.obj if hasattr(options, 'obj') else options)

    def initFromMarginalAndStarted(self, n, s, options=None):
        from . import jlineMatrixFromArray
        from .solvers import SolverOptions

        if options is None:
            from .solvers import Solver
            options = Solver.defaultOptions()

        n_matrix = jlineMatrixFromArray(n)
        s_matrix = jlineMatrixFromArray(s)
        self.obj.initFromMarginalAndStarted(n_matrix, s_matrix, options.obj if hasattr(options, 'obj') else options)

    def numberOfNodes(self):
        """Kotlin-style alias for getNumberOfNodes"""
        return self.getNumberOfNodes()

    def numberOfStations(self):
        """Kotlin-style alias for getNumberOfStations"""
        return self.getNumberOfStations()

    def numberOfClasses(self):
        """Kotlin-style alias for getNumberOfClasses"""
        return self.getNumberOfClasses()

    def classes(self):
        """Kotlin-style alias for getClasses"""
        return self.getClasses()

    def nodeIndex(self, node):
        """Kotlin-style alias for getNodeIndex"""
        return self.getNodeIndex(node)

    def stationIndex(self, station):
        """Kotlin-style alias for getStationIndex"""
        return self.getStationIndex(station)

    def statefulIndex(self, stateful):
        """Kotlin-style alias for getStatefulIndex"""
        return self.getStatefulIndex(stateful)

    def jobClassIndex(self, jobclass):
        """Kotlin-style alias for getJobClassIndex"""
        return self.getJobClassIndex(jobclass)

    def chainIndex(self, chain):
        """Kotlin-style alias for getChainIndex"""
        return self.getChainIndex(chain)

    def numberOfJobs(self):
        """Kotlin-style alias for getNumberOfJobs"""
        return self.getNumberOfJobs()

    def nodes(self):
        """Kotlin-style alias for getNodes"""
        return self.getNodes()

    def struct(self, force=True):
        """Kotlin-style alias for getStruct"""
        return self.getStruct(force)

    def state(self):
        """Kotlin-style alias for getState"""
        return self.getState()

    def graph(self):
        """Kotlin-style alias for getGraph"""
        return self.getGraph()

    get_number_of_nodes = getNumberOfNodes
    get_number_of_stations = getNumberOfStations
    get_number_of_classes = getNumberOfClasses
    get_classes = getClasses
    get_node_index = getNodeIndex
    get_station_index = getStationIndex
    get_stateful_index = getStatefulIndex
    get_job_class_index = getJobClassIndex
    get_chain_index = getChainIndex
    get_number_of_jobs = getNumberOfJobs
    get_nodes = getNodes
    get_tran_handles = getTranHandles
    get_struct = getStruct
    get_state = getState
    get_product_form_parameters = getProductFormParameters
    get_graph = getGraph


class Cache(Node):
    def __init__(self, model, name, nitems, itemLevelCap, replPolicy, graph=()):
        super().__init__()
        from .constants import GlobalConstants
        import math
        if nitems == float('inf') or nitems == float('-inf') or (isinstance(nitems, (int, float)) and math.isinf(nitems)):
            nitems_value = GlobalConstants.MaxInt
        else:
            nitems_value = int(nitems)

        if isinstance(itemLevelCap, int):
            if len(graph) == 0:
                self.obj = jpype.JPackage('jline').lang.nodes.Cache(model.obj, name, nitems_value,
                                                                    jlineMatrixSingleton(itemLevelCap),
                                                                    replPolicy.value)
            else:
                self.obj = jpype.JPackage('jline').lang.nodes.Cache(model.obj, name, nitems_value,
                                                                    jlineMatrixSingleton(itemLevelCap),
                                                                    replPolicy.value, graph)
        else:
            itemLevelCap = np.array(itemLevelCap, dtype=np.float64)
            if len(graph) == 0:
                self.obj = jpype.JPackage('jline').lang.nodes.Cache(model.obj, name, nitems_value,
                                                                    jpype.JPackage('jline').util.matrix.Matrix(
                                                                        itemLevelCap).colon().transpose(),
                                                                    replPolicy.value)
            else:
                self.obj = jpype.JPackage('jline').lang.nodes.Cache(model.obj, name, nitems_value,
                                                                    jpype.JPackage('jline').util.matrix.Matrix(
                                                                        itemLevelCap).colon().transpose(),
                                                                    replPolicy.value, graph)

    def setRead(self, jobclass, distrib):
        self.obj.setRead(jobclass.obj, distrib.obj)

    def setHitClass(self, jobclass1, jobclass2):
        self.obj.setHitClass(jobclass1.obj, jobclass2.obj)

    def setMissClass(self, jobclass1, jobclass2):
        self.obj.setMissClass(jobclass1.obj, jobclass2.obj)

    def getHitRatio(self):
        r = self.obj.getHitRatio()
        return jlineMatrixToArray(r)

    def getMissRatio(self):
        r = self.obj.getMissRatio()
        return jlineMatrixToArray(r)

    set_read = setRead
    set_hit_class = setHitClass
    set_miss_class = setMissClass
    get_hit_ratio = getHitRatio
    get_miss_ratio = getMissRatio
    hit_ratio = getHitRatio
    miss_ratio = getMissRatio



class Ensemble:
    def __init__(self):
        pass

    def getModel(self, stagenum):
        return Network(self.obj.getModel(stagenum))

    def getEnsemble(self):
        jensemble = self.obj.getEnsemble()
        ensemble = np.empty(jensemble.size(), dtype=object)
        for i in range(len(ensemble)):
            ensemble[i] = Network(jensemble.get(i))
        return ensemble

    get_model = getModel
    get_ensemble = getEnsemble
    model = getModel
    ensemble = getEnsemble


class Env(Ensemble):
    def __init__(self, name, nstages):
        super().__init__()
        from .constants import GlobalConstants
        import math
        if nstages == float('inf') or nstages == float('-inf') or (isinstance(nstages, (int, float)) and math.isinf(nstages)):
            nstages_value = GlobalConstants.MaxInt
        else:
            nstages_value = int(nstages)
        self.obj = jpype.JPackage('jline').lang.Env(name, nstages_value)

    def addStage(self, stage, envname, envtype, envmodel):
        self.obj.addStage(stage, envname, envtype, envmodel.obj)

    def addTransition(self, envname0, envname1, rate):
        self.obj.addTransition(envname0, envname1, rate.obj)

    def getStageTable(self):
        return self.obj.printStageTable()

    get_stage_table = getStageTable
    stage_table = getStageTable
    add_stage = addStage
    add_transition = addTransition


class Source(Station):
    def __init__(self, model, name):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Source(model.obj, name)

    def setArrival(self, jobclass, distribution):
        self.obj.setArrival(jobclass.obj, distribution.obj)

    def getArrivalProcess(self, jobclass):
        from line_solver import jlineFromDistribution
        return jlineFromDistribution(self.obj.getArrivalProcess(jobclass.obj))

    set_arrival = setArrival
    get_arrival_process = getArrivalProcess
    arrival_process = getArrivalProcess


class Logger(Node):
    def __init__(self, model, name, logfile):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Logger(model.obj, name, logfile)

    def setStartTime(self, activate):
        self.obj.setStartTime(activate)

    def setJobID(self, activate):
        self.obj.setJobID(activate)

    def setJobClass(self, activate):
        self.obj.setJobClass(activate)

    def setTimestamp(self, activate):
        self.obj.setTimestamp(activate)

    def setTimeSameClass(self, activate):
        self.obj.setTimeSameClass(activate)

    def setTimeAnyClass(self, activate):
        self.obj.setTimeAnyClass(activate)

    set_start_time = setStartTime
    set_job_id = setJobID
    set_job_class = setJobClass
    set_timestamp = setTimestamp
    set_time_same_class = setTimeSameClass
    set_time_any_class = setTimeAnyClass


class ClassSwitch(Node):
    def __init__(self, *argv):
        model = argv[0]
        name = argv[1]
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.ClassSwitch(model.obj, name)
        if len(argv) > 2:
            csmatrix = argv[2]
            self.setClassSwitchingMatrix(csmatrix)

    def initClassSwitchMatrix(self):
        return jlineMatrixToArray(self.obj.initClassSwitchMatrix())

    def setClassSwitchingMatrix(self, csmatrix):
        self.obj.setClassSwitchingMatrix(jpype.JPackage('jline').lang.ClassSwitchMatrix(jlineMatrixFromArray(csmatrix)))

    init_class_switch_matrix = initClassSwitchMatrix
    set_class_switching_matrix = setClassSwitchingMatrix


class Sink(Node):
    def __init__(self, model, name):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Sink(model.obj, name)


class Fork(Node):
    def __init__(self, model, name):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Fork(model.obj, name)

    def setTasksPerLink(self, tasks):
        self.obj.setTasksPerLink(tasks)

    set_tasks_per_link = setTasksPerLink

class Join(Station):
    def __init__(self, model, name, forknode):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Join(model.obj, name, forknode.obj)


class Queue(Station):

    def __init__(self, model, name, strategy):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Queue(model.obj, name, strategy.value)

    def setService(self, jobclass, distribution, weight=1.0):
        self.obj.setService(jobclass.obj, distribution.obj, weight)

    def setNumberOfServers(self, nservers):
        from .constants import GlobalConstants
        import math
        if nservers == float('inf') or nservers == float('-inf') or (isinstance(nservers, (int, float)) and math.isinf(nservers)):
            nservers_value = GlobalConstants.MaxInt
        else:
            nservers_value = int(nservers)
        self.obj.setNumberOfServers(nservers_value)

    def setLoadDependence(self, ldscaling):
        self.obj.setLoadDependence(jlineMatrixFromArray(ldscaling))

    def getServiceProcess(self, jobclass):
        from line_solver import jlineFromDistribution
        return jlineFromDistribution(self.obj.getServiceProcess(jobclass.obj))

    def setPollingType(self, polling_type, k=None):
        if k is not None:
            self.obj.setPollingType(polling_type.value, k)
        else:
            self.obj.setPollingType(polling_type.value)

    def setPollingK(self, k):
        self.obj.setPollingK(k)

    def setSwitchover(self, *args):
        if len(args) == 2:
            jobclass, distribution = args
            self.obj.setSwitchover(jobclass.obj, distribution.obj)
        elif len(args) == 3:
            jobclass_from, jobclass_to, distribution = args
            self.obj.setSwitchover(jobclass_from.obj, jobclass_to.obj, distribution.obj)
        else:
            raise ValueError("setSwitchover() takes 2 or 3 arguments")

    def getSwitchover(self, *args):
        if len(args) == 1:
            jobclass = args[0]
            java_dist = self.obj.getSwitchover(jobclass.obj)
            if java_dist is None:
                return None
            from line_solver import jlineFromDistribution
            return jlineFromDistribution(java_dist)
        elif len(args) == 2:
            jobclass_from, jobclass_to = args
            java_dist = self.obj.getSwitchover(jobclass_from.obj, jobclass_to.obj)
            if java_dist is None:
                return None
            from line_solver import jlineFromDistribution
            return jlineFromDistribution(java_dist)
        else:
            raise ValueError("getSwitchover() takes 1 or 2 arguments")

    def getSchedStrategy(self):
        return self.obj.getSchedStrategy()

    set_service = setService
    set_number_of_servers = setNumberOfServers
    set_load_dependence = setLoadDependence
    get_service_process = getServiceProcess
    set_polling_type = setPollingType
    set_polling_k = setPollingK
    set_switchover = setSwitchover
    get_switchover = getSwitchover
    get_sched_strategy = getSchedStrategy
    service_process = getServiceProcess
    sched_strategy = getSchedStrategy


class QueueingStation(Queue):
    def __init__(self, model, name, strategy):
        super().__init__(model, name, strategy)


class Delay(Station):
    def __init__(self, model, name):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Delay(model.obj, name)

    def setService(self, jobclass, distribution):
        self.obj.setService(jobclass.obj, distribution.obj)

    set_service = setService


class Router(Node):
    def __init__(self, model, name):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Router(model.obj, name)


class Place(Station):
    def __init__(self, model, name, schedStrategy=None):
        super().__init__()
        if schedStrategy is not None:
            self.obj = jpype.JPackage('jline').lang.nodes.Place(model.obj, name, schedStrategy.value)
        else:
            self.obj = jpype.JPackage('jline').lang.nodes.Place(model.obj, name)

    def setClassCapacity(self, jobclass, capacity):
        """Set capacity for a specific job class"""
        self.obj.setClassCapacity(jobclass.obj, capacity)

    def setSchedStrategy(self, jobclass, strategy):
        """Set scheduling strategy for a job class"""
        self.obj.setSchedStrategy(jobclass.obj, strategy.value)

    def setState(self, state):
        """Set initial state (number of tokens)"""
        if hasattr(state, 'obj'):
            self.obj.setState(state.obj)
        else:
            from . import jlineMatrixFromArray
            self.obj.setState(jlineMatrixFromArray(state))

    def setCap(self, cap):
        """Set overall capacity"""
        self.obj.setCap(cap)

    def setNumberOfServers(self, numberOfServers):
        """Set number of servers"""
        from .constants import GlobalConstants
        import math
        if numberOfServers == float('inf') or numberOfServers == float('-inf') or (isinstance(numberOfServers, (int, float)) and math.isinf(numberOfServers)):
            numberOfServers_value = GlobalConstants.MaxInt
        else:
            numberOfServers_value = int(numberOfServers)
        self.obj.setNumberOfServers(numberOfServers_value)

    def setDropRule(self, jobclass, dropStrategy):
        """Set drop strategy for a job class"""
        self.obj.setDropRule(jobclass.obj, dropStrategy.value)

    set_class_capacity = setClassCapacity
    set_sched_strategy = setSchedStrategy
    set_cap = setCap
    set_drop_rule = setDropRule
    class_capacity = setClassCapacity
    cap = setCap


class Mode:
    def __init__(self, transition_obj, name):
        """Create a mode - usually called via Transition.add_mode()"""
        self.obj = jpype.JPackage('jline').lang.Mode(transition_obj, name)

    def getIndex(self):
        """Get the index of this mode"""
        return int(self.obj.getIndex())

    def getTransition(self):
        """Get the parent transition"""
        return self.obj.getTransition()

    def printSummary(self):
        """Print summary of this mode"""
        self.obj.printSummary()

    get_index = getIndex
    get_transition = getTransition
    print_summary = printSummary
    index = getIndex
    transition = getTransition


class Transition(Node):
    def __init__(self, model, name):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.nodes.Transition(model.obj, name)

    def addMode(self, modename):
        """Add a new mode to this transition"""
        mode_obj = self.obj.addMode(modename)
        mode = Mode.__new__(Mode)
        mode.obj = mode_obj
        return mode

    add_mode = addMode

    def getModes(self):
        """Get list of all modes"""
        java_modes = self.obj.getModes()
        modes = []
        for java_mode in java_modes:
            mode = Mode.__new__(Mode)
            mode.obj = java_mode
            modes.append(mode)
        return modes

    def getModeNames(self):
        """Get list of mode names"""
        return list(self.obj.getModeNames())

    def getNumberOfModes(self):
        """Get number of modes"""
        return self.obj.getNumberOfModes()

    def setDistribution(self, mode, distribution):
        """Set firing distribution for a mode"""
        self.obj.setDistribution(mode.obj, distribution.obj)

    def setTimingStrategy(self, mode, timingStrategy):
        """Set timing strategy for a mode"""
        self.obj.setTimingStrategy(mode.obj, timingStrategy.value)

    def getFiringDistribution(self, mode):
        """Get firing distribution for a mode"""
        from line_solver import jlineFromDistribution
        return jlineFromDistribution(self.obj.getFiringDistribution(mode.obj))

    def setEnablingConditions(self, mode, jobclass, inputPlace, enablingCondition):
        """Set enabling conditions for a mode"""
        self.obj.setEnablingConditions(mode.obj, jobclass.obj, inputPlace.obj, enablingCondition)

    def setInhibitingConditions(self, mode, jobclass, inputPlace, inhibitingCondition):
        """Set inhibiting conditions for a mode"""
        self.obj.setInhibitingConditions(mode.obj, jobclass.obj, inputPlace.obj, inhibitingCondition)

    def setFiringOutcome(self, mode, jobclass, node, firingOutcome):
        """Set firing outcome for a mode"""
        self.obj.setFiringOutcome(mode.obj, jobclass.obj, node.obj, firingOutcome)

    def setFiringPriorities(self, mode, firingPriority):
        """Set firing priority for a mode"""
        self.obj.setFiringPriorities(mode.obj, firingPriority)

    def setFiringWeights(self, mode, firingWeight):
        """Set firing weight for a mode"""
        self.obj.setFiringWeights(mode.obj, firingWeight)

    def setNumberOfServers(self, mode, numberOfServers):
        """Set number of servers for a mode"""
        if numberOfServers == float('inf'):
            numberOfServers = jpype.java.lang.Integer.MAX_VALUE
        self.obj.setNumberOfServers(mode.obj, numberOfServers)

    def getNumberOfModeServers(self, mode):
        """Get number of servers for a mode"""
        return self.obj.getNumberOfModeServers(mode.obj)

    add_mode = addMode
    get_modes = getModes
    get_mode_names = getModeNames
    get_number_of_modes = getNumberOfModes
    set_distribution = setDistribution
    set_timing_strategy = setTimingStrategy
    get_firing_distribution = getFiringDistribution
    set_enabling_conditions = setEnablingConditions
    set_inhibiting_conditions = setInhibitingConditions
    set_firing_outcome = setFiringOutcome
    set_firing_priorities = setFiringPriorities
    set_firing_weights = setFiringWeights
    set_number_of_servers = setNumberOfServers
    get_number_of_mode_servers = getNumberOfModeServers
    modes = getModes
    mode_names = getModeNames
    number_of_modes = getNumberOfModes
    firing_distribution = getFiringDistribution
    number_of_mode_servers = getNumberOfModeServers



class OpenClass(JobClass):
    def __init__(self, model, name, prio=0):
        super().__init__()
        self.obj = jpype.JPackage('jline').lang.OpenClass(model.obj, name, prio)
        self.obj.setCompletes(True)

    @property
    def completes(self):
        """Whether jobs can complete and depart from the network."""
        return self.obj.getCompletes()

    @completes.setter
    def completes(self, value):
        """Set whether jobs can complete and depart from the network."""
        self.obj.setCompletes(bool(value))


class ClosedClass(JobClass):
    def __init__(self, model, name, njobs, refstat, prio=0):
        super().__init__()
        from .constants import GlobalConstants
        import math
        if njobs == float('inf') or njobs == float('-inf') or (isinstance(njobs, (int, float)) and math.isinf(njobs)):
            njobs_value = GlobalConstants.MaxInt
        else:
            njobs_value = int(njobs)
        self.obj = jpype.JPackage('jline').lang.ClosedClass(model.obj, name, njobs_value, refstat.obj, prio)
        self.obj.setCompletes(True)

    @property
    def completes(self):
        """Whether jobs can complete and depart from the network."""
        return self.obj.getCompletes()

    @completes.setter
    def completes(self, value):
        """Set whether jobs can complete and depart from the network."""
        self.obj.setCompletes(bool(value))

    def getPopulation(self):
        return self.obj.getPopulation()

    def getNumberOfJobs(self):
        return self.obj.getNumberOfJobs()

    get_population = getPopulation
    get_number_of_jobs = getNumberOfJobs
    population = getPopulation
    number_of_jobs = getNumberOfJobs


class SelfLoopingClass(JobClass):
    def __init__(self, model, name, njobs, refstat, prio=0):
        super().__init__()
        from .constants import GlobalConstants
        import math
        if njobs == float('inf') or njobs == float('-inf') or (isinstance(njobs, (int, float)) and math.isinf(njobs)):
            njobs_value = GlobalConstants.MaxInt
        else:
            njobs_value = int(njobs)
        self.obj = jpype.JPackage('jline').lang.SelfLoopingClass(model.obj, name, njobs_value, refstat.obj, prio)
        self.obj.setCompletes(True)

    @property
    def completes(self):
        """Whether jobs can complete and depart from the network."""
        return self.obj.getCompletes()

    @completes.setter
    def completes(self, value):
        """Set whether jobs can complete and depart from the network."""
        self.obj.setCompletes(bool(value))


class State:
    def __init__(self, initialState=None, priorInitialState=None):
        if initialState is not None and priorInitialState is not None:
            self.obj = jpype.JPackage('jline').lang.state.State(initialState, priorInitialState)
        else:
            self.obj = None

    @staticmethod
    def toMarginal(sn, ind, state_i, phasesz=None, phaseshift=None, space_buf=None, space_srv=None, space_var=None):
        StateJava = jpype.JPackage('jline').lang.state.State
        result = StateJava.toMarginal(
            sn.obj if hasattr(sn, 'obj') else sn,
            int(ind),
            state_i.obj if hasattr(state_i, 'obj') else state_i,
            phasesz.obj if phasesz is not None and hasattr(phasesz, 'obj') else phasesz,
            phaseshift.obj if phaseshift is not None and hasattr(phaseshift, 'obj') else phaseshift,
            space_buf.obj if space_buf is not None and hasattr(space_buf, 'obj') else space_buf,
            space_srv.obj if space_srv is not None and hasattr(space_srv, 'obj') else space_srv,
            space_var.obj if space_var is not None and hasattr(space_var, 'obj') else space_var,
        )
        return result

    @staticmethod
    def fromMarginalAndStarted(sn, ind, n, s, optionsForce=True):
        from . import jlineMatrixFromArray
        FromMarginalJava = jpype.JPackage('jline').lang.state.FromMarginal

        sn_obj = sn.obj if hasattr(sn, 'obj') else sn
        n_matrix = n.obj if hasattr(n, 'obj') else jlineMatrixFromArray(n)
        s_matrix = s.obj if hasattr(s, 'obj') else jlineMatrixFromArray(s)

        if optionsForce is not True:
            if hasattr(sn_obj, 'getStruct'):
                sn_struct = sn_obj.getStruct(True)
            else:
                sn_struct = sn_obj
            result = FromMarginalJava.fromMarginalAndStarted(
                sn_struct,
                int(ind),
                n_matrix,
                s_matrix,
                bool(optionsForce)
            )
        else:
            result = FromMarginalJava.fromMarginalAndStarted(
                sn_obj,
                int(ind),
                n_matrix,
                s_matrix
            )
        result = jlineMatrixToArray(result)
        return result


    @staticmethod
    def toMarginalAggr(sn, ind, state_i, K, Ks, space_buf=None, space_srv=None, space_var=None):
        StateJava = jpype.JPackage('jline').lang.state.State
        result = StateJava.toMarginalAggr(
            sn.obj if hasattr(sn, 'obj') else sn,
            int(ind),
            state_i.obj if hasattr(state_i, 'obj') else state_i,
            K.obj if hasattr(K, 'obj') else K,
            Ks.obj if hasattr(Ks, 'obj') else Ks,
            space_buf.obj if space_buf is not None and hasattr(space_buf, 'obj') else space_buf,
            space_srv.obj if space_srv is not None and hasattr(space_srv, 'obj') else space_srv,
            space_var.obj if space_var is not None and hasattr(space_var, 'obj') else space_var,
        )
        return result

    @staticmethod
    def fromMarginalAndRunning(sn, ind, n, s, optionsForce=False):
        from . import jlineMatrixFromArray
        FromMarginalJava = jpype.JPackage('jline').lang.state.FromMarginal

        sn_obj = sn.obj if hasattr(sn, 'obj') else sn
        n_matrix = n.obj if hasattr(n, 'obj') else jlineMatrixFromArray(n)
        s_matrix = s.obj if hasattr(s, 'obj') else jlineMatrixFromArray(s)

        if optionsForce is not False:
            if hasattr(sn_obj, 'getStruct'):
                sn_struct = sn_obj.getStruct(True)
            else:
                sn_struct = sn_obj
            result = FromMarginalJava.fromMarginalAndRunning(
                sn_struct,
                int(ind),
                n_matrix,
                s_matrix,
                bool(optionsForce)
            )
        else:
            result = FromMarginalJava.fromMarginalAndRunning(
                sn_obj,
                int(ind),
                n_matrix,
                s_matrix
            )

        result = jlineMatrixToArray(result)
        return result

    @staticmethod
    def isValid(sn, n, s):
        from . import jlineMatrixFromArray
        StateJava = jpype.JPackage('jline').lang.state.State
        return StateJava.isValid(
            sn.obj if hasattr(sn, 'obj') else sn,
            n.obj if hasattr(n, 'obj') else jlineMatrixFromArray(n),
            s.obj if hasattr(s, 'obj') else jlineMatrixFromArray(s)
        )

    @staticmethod
    def fromMarginal(sn, ind, n):
        from . import jlineMatrixFromArray
        FromMarginalJava = jpype.JPackage('jline').lang.state.FromMarginal

        sn_obj = sn.obj if hasattr(sn, 'obj') else sn
        n_matrix = n.obj if hasattr(n, 'obj') else jlineMatrixFromArray(n)

        if hasattr(sn_obj, 'getStruct'):
            sn_struct = sn_obj.getStruct(True)
        else:
            sn_struct = sn_obj

        result = FromMarginalJava.fromMarginal(
            sn_struct,
            int(ind),
            n_matrix
        )
        result = jlineMatrixToArray(result)
        return result

    @staticmethod
    def afterEvent(sn, ind, inspace, event, jobClass, isSimulation=False, eventCache=None):
        StateJava = jpype.JPackage('jline').lang.state.State
        if eventCache is not None:
            result = StateJava.afterEvent(
                sn.obj if hasattr(sn, 'obj') else sn,
                int(ind),
                inspace.obj if hasattr(inspace, 'obj') else inspace,
                event,
                int(jobClass),
                bool(isSimulation),
                eventCache
            )
        else:
            result = StateJava.afterEvent(
                sn.obj if hasattr(sn, 'obj') else sn,
                int(ind),
                inspace.obj if hasattr(inspace, 'obj') else inspace,
                event,
                int(jobClass),
                bool(isSimulation)
            )
        return result

    @staticmethod
    def isinf(matrix):
        StateJava = jpype.JPackage('jline').lang.state.State
        return StateJava.isinf(
            matrix.obj if hasattr(matrix, 'obj') else matrix
        )

    @staticmethod
    def cpos(matrix, i, j):
        StateJava = jpype.JPackage('jline').lang.state.State
        return StateJava.cpos(
            matrix.obj if hasattr(matrix, 'obj') else matrix,
            int(i),
            int(j)
        )

    @staticmethod
    def afterEventHashed(sn, ind, inspacehash, event, jobclass, isSimulation=False, options=None):
        StateJava = jpype.JPackage('jline').lang.state.State
        if options is not None:
            result = StateJava.afterEventHashed(
                sn.obj if hasattr(sn, 'obj') else sn,
                int(ind),
                float(inspacehash),
                event,
                int(jobclass),
                bool(isSimulation),
                options
            )
        else:
            result = StateJava.afterEventHashed(
                sn.obj if hasattr(sn, 'obj') else sn,
                int(ind),
                float(inspacehash),
                event,
                int(jobclass),
                bool(isSimulation)
            )
        return result

    @staticmethod
    def spaceGenerator(sn, cutoff=None, options=None):
        StateJava = jpype.JPackage('jline').lang.state.State
        if cutoff is not None and options is not None:
            result = StateJava.spaceGenerator(
                sn.obj if hasattr(sn, 'obj') else sn,
                cutoff.obj if hasattr(cutoff, 'obj') else cutoff,
                options.obj if hasattr(options, 'obj') else options
            )
        elif cutoff is not None:
            result = StateJava.spaceGenerator(
                sn.obj if hasattr(sn, 'obj') else sn,
                cutoff.obj if hasattr(cutoff, 'obj') else cutoff
            )
        else:
            result = StateJava.spaceGenerator(
                sn.obj if hasattr(sn, 'obj') else sn
            )
        return result

    @staticmethod
    def spaceClosedMultiCS(M, N, chains):
        StateJava = jpype.JPackage('jline').lang.state.State
        result = StateJava.spaceClosedMultiCS(
            int(M),
            N.obj if hasattr(N, 'obj') else N,
            chains.obj if hasattr(chains, 'obj') else chains
        )
        result = jlineMatrixToArray(result)
        return result

    @staticmethod
    def spaceClosedMulti(M, N):
        StateJava = jpype.JPackage('jline').lang.state.State
        result = StateJava.spaceClosedMulti(
            int(M),
            N.obj if hasattr(N, 'obj') else N
        )
        result = jlineMatrixToArray(result)
        return result

    @staticmethod
    def spaceGeneratorNodes(sn, cutoff=None, options=None):
        StateJava = jpype.JPackage('jline').lang.state.State
        if cutoff is not None and options is not None:
            result = StateJava.spaceGeneratorNodes(
                sn.obj if hasattr(sn, 'obj') else sn,
                cutoff.obj if hasattr(cutoff, 'obj') else cutoff,
                options.obj if hasattr(options, 'obj') else options
            )
        elif cutoff is not None:
            result = StateJava.spaceGeneratorNodes(
                sn.obj if hasattr(sn, 'obj') else sn,
                cutoff.obj if hasattr(cutoff, 'obj') else cutoff
            )
        else:
            result = StateJava.spaceGeneratorNodes(
                sn.obj if hasattr(sn, 'obj') else sn
            )
        return result

    @staticmethod
    def fromMarginalBounds(sn, ind, n, nmax, s, smax):
        from . import jlineMatrixFromArray
        FromMarginalJava = jpype.JPackage('jline').lang.state.FromMarginal
        result = FromMarginalJava.fromMarginalBounds(
            sn.obj if hasattr(sn, 'obj') else sn,
            int(ind),
            n.obj if hasattr(n, 'obj') else jlineMatrixFromArray(n),
            nmax.obj if hasattr(nmax, 'obj') else jlineMatrixFromArray(nmax),
            s.obj if hasattr(s, 'obj') else jlineMatrixFromArray(s),
            smax.obj if hasattr(smax, 'obj') else jlineMatrixFromArray(smax)
        )
        result = jlineMatrixToArray(result)
        return result