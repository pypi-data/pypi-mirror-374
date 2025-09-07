
import jpype
import jpype.imports
import numpy as np
from pprint import pformat
from . import SchedStrategy, jlineFromDistribution, SchedStrategyType, CallType, ReplacementStrategy
from .lang import jlineMatrixToArray


class LayeredNetwork:

    def __init__(self, name):
        self.obj = jpype.JPackage('jline').lang.layered.LayeredNetwork(name)

    def parseXML(self, filename, verbose=False):
        self.obj.parseXML(filename, verbose)

    def writeXML(self, filename, abstractNames=False):
        self.obj.writeXML(filename, abstractNames)

    def getNodeIndex(self, node):
        return self.obj.getNodeIndex(node.obj)

    def getNodeNames(self):
        return self.obj.getNodeNames()

    def getEnsemble(self):
        return self.obj.getEnsemble()

    def getLayers(self):
        return self.obj.getLayers()

    def getNumberOfLayers(self):
        return self.obj.getNumberOfLayers()

    def getNumberOfModels(self):
        return self.obj.getNumberOfModels()

    def summary(self):
        return self.obj.summary()

    def parseXML(self, filename, verbose):
        return self.obj.parseXML(filename, verbose)

    def getStruct(self):
        jsn = self.obj.getStruct()
        lsn = LayeredNetworkStruct()
        lsn.fromJline(jsn)
        return lsn

    def plot(self, showTaskGraph=False, **kwargs):
        self.plotGraph(**kwargs)
        if showTaskGraph:
            self.plotTaskGraph(**kwargs)

    def plotGraph(self, method='nodes', **kwargs):
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
            import numpy as np
        except ImportError:
            raise ImportError("Matplotlib and NetworkX are required for plotting. Install with: pip install matplotlib networkx")

        lqn = self.getStruct()

        G = nx.DiGraph()

        adj_matrix = lqn.graph

        node_labels = {}
        node_colors = []
        node_shapes = []
        node_sizes = []

        for i in range(adj_matrix.shape[0]):
            G.add_node(i)

            if method == 'hashnames':
                label = lqn.hashnames[i] if i < len(lqn.hashnames) else f'Node{i}'
                label = label.replace('_', '\\_')
            elif method == 'names':
                label = lqn.names[i] if i < len(lqn.names) else f'Node{i}'
                label = label.replace('_', '\\_')
            elif method == 'ids':
                label = str(i)
            else:
                label = lqn.hashnames[i] if i < len(lqn.hashnames) else f'Node{i}'
                label = label.replace('_', '\\_')

            node_labels[i] = label

            node_type = int(lqn.type[i]) if i < len(lqn.type) else 0

            HOST = 1; TASK = 2; ENTRY = 3; ACTIVITY = 4

            if node_type == HOST:
                node_colors.append('black')
                node_shapes.append('h')
                node_sizes.append(1200)
            elif node_type == ACTIVITY:
                node_colors.append('blue')
                node_shapes.append('o')
                node_sizes.append(800)
            elif node_type == TASK:
                if i < len(lqn.isref) and lqn.isref[i]:
                    node_colors.append('#EDB120')
                    node_shapes.append('^')
                else:
                    node_colors.append('magenta')
                    node_shapes.append('v')
                node_sizes.append(1000)
            elif node_type == ENTRY:
                node_colors.append('red')
                node_shapes.append('s')
                node_sizes.append(900)
            else:
                node_colors.append('lightgray')
                node_shapes.append('o')
                node_sizes.append(600)

        for i in range(adj_matrix.shape[0]):
            for j in range(adj_matrix.shape[1]):
                if adj_matrix[i, j] > 0:
                    G.add_edge(i, j, weight=adj_matrix[i, j])

        plt.figure(figsize=kwargs.get('figsize', (14, 10)))

        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except:
            pos = nx.spring_layout(G, k=2, iterations=50, seed=23000)

        unique_shapes = list(set(node_shapes))
        for shape in unique_shapes:
            shape_nodes = [i for i, s in enumerate(node_shapes) if s == shape]
            shape_colors = [node_colors[i] for i in shape_nodes]
            shape_sizes = [node_sizes[i] for i in shape_nodes]

            marker_map = {'o': 'o', 's': 's', '^': '^', 'v': 'v', 'h': 'h'}
            marker = marker_map.get(shape, 'o')

            nx.draw_networkx_nodes(G, pos,
                                 nodelist=shape_nodes,
                                 node_color=shape_colors,
                                 node_size=shape_sizes,
                                 node_shape=marker,
                                 alpha=0.8)

        nx.draw_networkx_edges(G, pos,
                             edge_color='gray',
                             arrows=True,
                             arrowsize=20,
                             arrowstyle='->',
                             alpha=0.6,
                             width=1.0)

        nx.draw_networkx_labels(G, pos,
                              labels=node_labels,
                              font_size=kwargs.get('font_size', 8),
                              font_weight='bold')

        plt.title(f'Model: {self.obj.getName()}', fontsize=kwargs.get('title_fontsize', 14))
        plt.axis('off')

        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='black', label='Host'),
            Patch(facecolor='blue', label='Activity'),
            Patch(facecolor='#EDB120', label='Reference Task'),
            Patch(facecolor='magenta', label='Task'),
            Patch(facecolor='red', label='Entry')
        ]
        plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))

        plt.tight_layout()

        if kwargs.get('show', True):
            plt.show()

        return plt.gcf()

    def plotGraphSimple(self, method='nodes', **kwargs):
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
        except ImportError:
            raise ImportError("Matplotlib and NetworkX are required for plotting. Install with: pip install matplotlib networkx")

        lqn = self.getStruct()

        G = nx.DiGraph()

        adj_matrix = lqn.graph

        node_labels = {}
        for i in range(adj_matrix.shape[0]):
            G.add_node(i)

            if method in ['nodes', 'hashnames']:
                label = lqn.hashnames[i] if i < len(lqn.hashnames) else f'Node{i}'
                label = label.replace('_', '\\_')
            elif method == 'names':
                label = lqn.names[i] if i < len(lqn.names) else f'Node{i}'
                label = label.replace('_', '\\_')
            elif method == 'hashids':
                if i < len(lqn.hashnames):
                    prefix = lqn.hashnames[i][:2] if len(lqn.hashnames[i]) >= 2 else 'XX'
                    label = f'{prefix}{i}'
                else:
                    label = f'N{i}'
            else:
                label = str(i)

            node_labels[i] = label

        for i in range(adj_matrix.shape[0]):
            for j in range(adj_matrix.shape[1]):
                if adj_matrix[i, j] > 0:
                    G.add_edge(i, j, weight=adj_matrix[i, j])

        plt.figure(figsize=kwargs.get('figsize', (12, 8)))

        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except:
            pos = nx.spring_layout(G, k=2, iterations=50, seed=23000)

        nx.draw_networkx_nodes(G, pos,
                             node_color='white',
                             edgecolors='black',
                             node_size=kwargs.get('node_size', 800),
                             linewidths=2)

        nx.draw_networkx_edges(G, pos,
                             edge_color='black',
                             arrows=True,
                             arrowsize=20,
                             arrowstyle='->',
                             width=1.5)

        nx.draw_networkx_labels(G, pos,
                              labels=node_labels,
                              font_size=kwargs.get('font_size', 8),
                              font_weight='bold')

        plt.title(f'Model: {self.obj.getName()}', fontsize=kwargs.get('title_fontsize', 14))
        plt.axis('off')
        plt.tight_layout()

        if kwargs.get('show', True):
            plt.show()

        return plt.gcf()

    def plotTaskGraph(self, method='nodes', **kwargs):
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
            import numpy as np
        except ImportError:
            raise ImportError("Matplotlib and NetworkX are required for plotting. Install with: pip install matplotlib networkx")

        lqn = self.getStruct()

        T = np.zeros((lqn.nhosts + lqn.ntasks, lqn.nhosts + lqn.ntasks))

        for h in range(lqn.nhosts):
            hidx = h
            if h < len(lqn.tasksof) and lqn.tasksof[h] is not None:
                for tidx in lqn.tasksof[h]:
                    if tidx < T.shape[0] and hidx < T.shape[1]:
                        T[tidx, hidx] = 1

        for t in range(lqn.ntasks):
            tidx = lqn.tshift + t
            if tidx < len(lqn.entriesof) and lqn.entriesof[tidx] is not None:
                for entry_idx in lqn.entriesof[tidx]:
                    if entry_idx < lqn.iscaller.shape[1]:
                        calling_indices = np.where(lqn.iscaller[:, entry_idx] > 0)[0]
                        task_range = range(lqn.tshift, lqn.tshift + lqn.ntasks)
                        callers = [idx for idx in calling_indices if idx in task_range]

                        for caller_idx in callers:
                            if caller_idx < T.shape[0] and tidx < T.shape[1]:
                                T[caller_idx, tidx] = 1

        G = nx.DiGraph()

        node_labels = {}
        node_colors = []

        for i in range(lqn.nhosts + lqn.ntasks):
            G.add_node(i)

            if method == 'nodes':
                label = lqn.hashnames[i] if i < len(lqn.hashnames) else f'Node{i}'
            elif method == 'names':
                label = lqn.names[i] if i < len(lqn.names) else f'Node{i}'
            else:
                label = str(i)

            node_labels[i] = label

            if i < lqn.nhosts:
                node_colors.append('lightgray')
            else:
                node_colors.append('lightblue')

        for i in range(T.shape[0]):
            for j in range(T.shape[1]):
                if T[i, j] > 0:
                    G.add_edge(i, j)

        plt.figure(figsize=kwargs.get('figsize', (10, 8)))

        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except:
            pos = nx.spring_layout(G, k=2, iterations=50, seed=23000)

        nx.draw_networkx_nodes(G, pos,
                             node_color=node_colors,
                             node_size=kwargs.get('node_size', 1000),
                             alpha=0.8)

        nx.draw_networkx_edges(G, pos,
                             edge_color='gray',
                             arrows=True,
                             arrowsize=20,
                             arrowstyle='->',
                             alpha=0.6)

        nx.draw_networkx_labels(G, pos,
                              labels=node_labels,
                              font_size=kwargs.get('font_size', 10),
                              font_weight='bold')

        plt.title('Task Graph', fontsize=kwargs.get('title_fontsize', 14))
        plt.axis('off')

        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='lightgray', label='Host'),
            Patch(facecolor='lightblue', label='Task')
        ]
        plt.legend(handles=legend_elements, loc='upper right')

        plt.tight_layout()

        if kwargs.get('show', True):
            plt.show()

        return plt.gcf()

    def writeJLQN(self, filename, abstractNames=False):
        self.obj.writeJLQN(filename, abstractNames)

    def sendModel(self, outputPath, *args):
        if len(args) == 1:
            portNumber = args[0]
            self.obj.sendModel(outputPath, portNumber)
        elif len(args) == 2:
            ipNumber, portNumber = args
            self.obj.sendModel(outputPath, ipNumber, portNumber)
        else:
            raise ValueError("sendModel requires either (outputPath, portNumber) or (outputPath, ipNumber, portNumber)")

    def generateGraph(self):
        """Generate internal graph representation."""
        self.obj.generateGraph()

    @staticmethod
    def load(filename, verbose=False):
        java_model = jpype.JPackage('jline').lang.layered.LayeredNetwork.load(filename, verbose)
        model = LayeredNetwork('')
        model.obj = java_model
        return model

    @staticmethod
    def parseXML(filename, verbose=False):
        java_model = jpype.JPackage('jline').lang.layered.LayeredNetwork.parseXML(filename, verbose)
        model = LayeredNetwork('')
        model.obj = java_model
        return model

    @staticmethod
    def readXML(filename, verbose=False):
        java_model = jpype.JPackage('jline').lang.layered.LayeredNetwork.readXML(filename, verbose)
        model = LayeredNetwork('')
        model.obj = java_model
        return model

    @staticmethod
    def viewModel(filename, jlqnPath=None):
        if jlqnPath is None:
            jpype.JPackage('jline').lang.layered.LayeredNetwork.viewModel(filename)
        else:
            jpype.JPackage('jline').lang.layered.LayeredNetwork.viewModel(jlqnPath, filename)

    get_node_index = getNodeIndex
    get_node_names = getNodeNames
    get_ensemble = getEnsemble
    get_layers = getLayers
    get_number_of_layers = getNumberOfLayers
    get_number_of_models = getNumberOfModels
    get_struct = getStruct
    write_jlqn = writeJLQN
    send_model = sendModel
    generate_graph = generateGraph
    view_model = viewModel


class LayeredNetworkStruct():
    def __str__(self):
        return pformat(vars(self))

    def fromJline(self, jsn):
        self.nidx = int(jsn.nidx)
        self.nhosts = int(jsn.nhosts)
        self.ntasks = int(jsn.ntasks)
        self.nentries = int(jsn.nentries)
        self.nacts = int(jsn.nacts)
        self.ncalls = int(jsn.ncalls)

        self.hshift = int(jsn.hshift)
        self.tshift = int(jsn.tshift)
        self.eshift = int(jsn.eshift)
        self.ashift = int(jsn.ashift)
        self.cshift = int(jsn.cshift)

        self.schedid = jlineMatrixToArray(jsn.schedid)
        self.mult = jlineMatrixToArray(jsn.mult)
        self.repl = jlineMatrixToArray(jsn.repl)
        self.type = jlineMatrixToArray(jsn.type)
        self.graph = jlineMatrixToArray(jsn.graph)
        self.replygraph = jlineMatrixToArray(jsn.replygraph)
        self.nitems = jlineMatrixToArray(jsn.nitems)
        self.replacement = jlineMatrixToArray(jsn.replacement)
        self.parent = jlineMatrixToArray(jsn.parent)
        self.iscaller = jlineMatrixToArray(jsn.iscaller)
        self.issynccaller = jlineMatrixToArray(jsn.issynccaller)
        self.isasynccaller = jlineMatrixToArray(jsn.isasynccaller)
        self.callpair = jlineMatrixToArray(jsn.callpair)
        self.taskgraph = jlineMatrixToArray(jsn.taskgraph)
        self.actpretype = jlineMatrixToArray(jsn.actpretype)
        self.actposttype = jlineMatrixToArray(jsn.actposttype)
        self.isref = jlineMatrixToArray(jsn.isref)

        self.names = np.empty(self.nidx, dtype=object)
        self.hashnames = np.empty(self.nidx, dtype=object)
        for i in range(int(self.nidx)):
            self.names[i] = jsn.names.get(jpype.JPackage('java').lang.Integer(1 + i))
            self.hashnames[i] = jsn.hashnames.get(jpype.JPackage('java').lang.Integer(1 + i))

        self.callnames = np.empty(self.ncalls, dtype=object)
        self.callhashnames = np.empty(self.ncalls, dtype=object)
        for i in range(int(self.ncalls)):
            self.callnames[i] = jsn.callnames.get(jpype.JPackage('java').lang.Integer(1 + i))
            self.callhashnames[i] = jsn.callhashnames.get(jpype.JPackage('java').lang.Integer(1 + i))

        self.hostdem = np.empty(self.nidx, dtype=object)
        for i in range(len(jsn.hostdem)):
            distrib = jsn.hostdem.get(jpype.JPackage('java').lang.Integer(1 + i))
            self.hostdem[i] = jlineFromDistribution(distrib)

        self.think = np.empty(self.nidx, dtype=object)
        for i in range(len(jsn.think)):
            distrib = jsn.think.get(jpype.JPackage('java').lang.Integer(1 + i))
            self.think[i] = jlineFromDistribution(distrib)

        self.callproc = np.empty(self.nidx, dtype=object)
        for i in range(len(jsn.callproc)):
            distrib = jsn.callproc.get(jpype.JPackage('java').lang.Integer(1 + i))
            self.callproc[i] = jlineFromDistribution(distrib)

        self.itemproc = np.empty(self.nidx, dtype=object)
        for i in range(len(jsn.itemproc)):
            distrib = jsn.itemproc.get(jpype.JPackage('java').lang.Integer(1 + i))
            self.itemproc[i] = jlineFromDistribution(distrib)

        self.itemcap = np.zeros(len(jsn.itemproc), dtype=object)
        for i in range(len(jsn.itemproc)):
            self.itemcap[i] = jsn.itemproc.get(jpype.JPackage('java').lang.Integer(1 + i)).intValue()

        self.sched = np.empty(len(jsn.sched), dtype=object)
        for i in range(len(jsn.sched)):
            sched_i = jsn.sched.get(jpype.JPackage('java').lang.Integer(1 + i))
            if sched_i is not None:
                self.sched[i] = SchedStrategy(sched_i).name
            else:
                self.sched[i] = None

        self.calltype = np.empty(self.ncalls, dtype=object)
        for i in range(len(jsn.calltype)):
            calltype_i = jsn.calltype.get(jpype.JPackage('java').lang.Integer(1 + i))
            if calltype_i is not None:
                self.calltype[i] = CallType(calltype_i).name
            else:
                self.calltype[i] = None

        self.entriesof = np.empty(len(jsn.entriesof), dtype=object)
        for i in range(len(jsn.entriesof)):
            arrayList = jsn.entriesof.get(jpype.JPackage('java').lang.Integer(1 + i))
            if arrayList is not None:
                self.entriesof[i] = list(arrayList)

        self.tasksof = np.empty(len(jsn.tasksof), dtype=object)
        for i in range(len(jsn.tasksof)):
            arrayList = jsn.tasksof.get(jpype.JPackage('java').lang.Integer(1 + i))
            if arrayList is not None:
                self.tasksof[i] = list(arrayList)

        self.actsof = np.empty(len(jsn.actsof), dtype=object)
        for i in range(len(jsn.actsof)):
            arrayList = jsn.actsof.get(jpype.JPackage('java').lang.Integer(1 + i))
            if arrayList is not None:
                self.actsof[i] = list(arrayList)

        self.callsof = np.empty(len(jsn.callsof), dtype=object)
        for i in range(len(jsn.callsof)):
            arrayList = jsn.callsof.get(jpype.JPackage('java').lang.Integer(1 + i))
            if arrayList is not None:
                self.callsof[i] = list(arrayList)

class Processor:
    def __init__(self, model, name, mult, schedStrategy):
        from .constants import GlobalConstants
        import math
        if mult == float('inf') or mult == float('-inf') or (isinstance(mult, (int, float)) and math.isinf(mult)):
            mult_value = GlobalConstants.MaxInt
        else:
            mult_value = int(mult)
        self.obj = jpype.JPackage('jline').lang.layered.Processor(model.obj, name, mult_value, schedStrategy.value)


class Task:
    def __init__(self, model, name, mult, schedStrategy):
        from .constants import GlobalConstants
        import math
        if mult == float('inf') or mult == float('-inf') or (isinstance(mult, (int, float)) and math.isinf(mult)):
            mult_value = GlobalConstants.MaxInt
        else:
            mult_value = int(mult)
        self.obj = jpype.JPackage('jline').lang.layered.Task(model.obj, name, mult_value, schedStrategy.value)

    def on(self, proc):
        self.obj.on(proc.obj)
        return self

    def setThinkTime(self, distrib):
        self.obj.setThinkTime(distrib.obj)
        return self

    def addPrecedence(self, prec):
        self.obj.addPrecedence(prec)

    set_think_time = setThinkTime


class FunctionTask:
    def __init__(self, model, name, mult, schedStrategy):
        from .constants import GlobalConstants
        import math
        if mult == float('inf') or mult == float('-inf') or (isinstance(mult, (int, float)) and math.isinf(mult)):
            mult_value = GlobalConstants.MaxInt
        else:
            mult_value = int(mult)
        self.obj = jpype.JPackage('jline').lang.layered.FunctionTask(model.obj, name, mult_value, schedStrategy.value)

    def on(self, proc):
        self.obj.on(proc.obj)
        return self

    def setThinkTime(self, distrib):
        self.obj.setThinkTime(distrib.obj)
        return self

    def setSetupTime(self, distrib):
        if hasattr(distrib, 'obj'):
            self.obj.setSetupTime(distrib.obj)
        else:
            self.obj.setSetupTime(float(distrib))
        return self

    def setDelayOffTime(self, distrib):
        if hasattr(distrib, 'obj'):
            self.obj.setDelayOffTime(distrib.obj)
        else:
            self.obj.setDelayOffTime(float(distrib))
        return self

    def addPrecedence(self, prec):
        self.obj.addPrecedence(prec)

    set_think_time = setThinkTime
    set_setup_time = setSetupTime
    set_delay_off_time = setDelayOffTime


class Entry:
    def __init__(self, model, name):
        self.obj = jpype.JPackage('jline').lang.layered.Entry(model.obj, name)

    def on(self, proc):
        self.obj.on(proc.obj)
        return self


class Activity:
    def __init__(self, model, name, distrib):
        self.obj = jpype.JPackage('jline').lang.layered.Activity(model.obj, name, distrib.obj)

    def on(self, proc):
        self.obj.on(proc.obj)
        return self

    def boundTo(self, proc):
        self.obj.boundTo(proc.obj)
        return self

    def repliesTo(self, entry):
        self.obj.repliesTo(entry.obj)
        return self

    def synchCall(self, entry, callmult=1.0):
        self.obj.synchCall(entry.obj, callmult)
        return self


class ActivityPrecedence:
    def __init__(self, name):
        self.obj = jpype.JPackage('jline').lang.layered.ActivityPrecedence(name)

    @staticmethod
    def Serial(act0, act1):
        return jpype.JPackage('jline').lang.layered.ActivityPrecedence.Serial(
            act0.obj.getName(), act1.obj.getName())

    @staticmethod
    def AndFork(preAct, postActs):
        preActName = preAct.obj.getName() if hasattr(preAct, 'obj') else str(preAct)
        postActNames = []
        for act in postActs:
            if hasattr(act, 'obj'):
                postActNames.append(act.obj.getName())
            else:
                postActNames.append(str(act))

        java_list = jpype.java.util.ArrayList()
        for name in postActNames:
            java_list.add(name)

        return jpype.JPackage('jline').lang.layered.ActivityPrecedence.AndFork(preActName, java_list)

    @staticmethod
    def AndJoin(preActs, postAct, quorum=None):
        preActNames = []
        for act in preActs:
            if hasattr(act, 'obj'):
                preActNames.append(act.obj.getName())
            else:
                preActNames.append(str(act))

        postActName = postAct.obj.getName() if hasattr(postAct, 'obj') else str(postAct)

        java_list = jpype.java.util.ArrayList()
        for name in preActNames:
            java_list.add(name)

        if quorum is not None:
            from .lang import jlineMatrixFromArray
            return jpype.JPackage('jline').lang.layered.ActivityPrecedence.AndJoin(
                java_list, postActName, jlineMatrixFromArray(quorum))
        else:
            return jpype.JPackage('jline').lang.layered.ActivityPrecedence.AndJoin(java_list, postActName)

    @staticmethod
    def OrFork(preAct, postActs, probs):
        preActName = preAct.obj.getName() if hasattr(preAct, 'obj') else str(preAct)
        postActNames = []
        for act in postActs:
            if hasattr(act, 'obj'):
                postActNames.append(act.obj.getName())
            else:
                postActNames.append(str(act))

        java_list = jpype.java.util.ArrayList()
        for name in postActNames:
            java_list.add(name)

        from .lang import jlineMatrixFromArray
        import numpy as np
        prob_matrix = jlineMatrixFromArray(np.array(probs).reshape(1, -1))

        return jpype.JPackage('jline').lang.layered.ActivityPrecedence.OrFork(
            preActName, java_list, prob_matrix)

    @staticmethod
    def OrJoin(preActs, postAct):
        preActNames = []
        for act in preActs:
            if hasattr(act, 'obj'):
                preActNames.append(act.obj.getName())
            else:
                preActNames.append(str(act))

        postActName = postAct.obj.getName() if hasattr(postAct, 'obj') else str(postAct)

        java_list = jpype.java.util.ArrayList()
        for name in preActNames:
            java_list.add(name)

        return jpype.JPackage('jline').lang.layered.ActivityPrecedence.OrJoin(java_list, postActName)

    @staticmethod
    def Loop(preAct, postActs, counts):
        preActName = preAct.obj.getName() if hasattr(preAct, 'obj') else str(preAct)
        postActNames = []
        for act in postActs:
            if hasattr(act, 'obj'):
                postActNames.append(act.obj.getName())
            else:
                postActNames.append(str(act))

        java_list = jpype.java.util.ArrayList()
        for name in postActNames:
            java_list.add(name)

        return jpype.JPackage('jline').lang.layered.ActivityPrecedence.Loop(
            preActName, java_list, float(counts))

    @staticmethod
    def CacheAccess(preAct, postActs):
        preActName = preAct.obj.getName() if hasattr(preAct, 'obj') else str(preAct)
        postActNames = []
        for act in postActs:
            if hasattr(act, 'obj'):
                postActNames.append(act.obj.getName())
            else:
                postActNames.append(str(act))

        java_list = jpype.java.util.ArrayList()
        for name in postActNames:
            java_list.add(name)

        return jpype.JPackage('jline').lang.layered.ActivityPrecedence.CacheAccess(preActName, java_list)

    @staticmethod
    def fromActivities(preActs, postActs, preType, postType=None, preParams=None, postParams=None):
        preActList = jpype.java.util.ArrayList()
        for act in preActs:
            if hasattr(act, 'obj'):
                preActList.add(act.obj)
            else:
                raise ValueError("preActs must contain Activity objects")

        postActList = jpype.java.util.ArrayList()
        for act in postActs:
            if hasattr(act, 'obj'):
                postActList.add(act.obj)
            else:
                raise ValueError("postActs must contain Activity objects")

        if postParams is not None:
            from .lang import jlineMatrixFromArray
            return jpype.JPackage('jline').lang.layered.ActivityPrecedence.fromActivities(
                preActList, postActList, preType, postType,
                jlineMatrixFromArray(preParams), jlineMatrixFromArray(postParams))
        elif preParams is not None:
            from .lang import jlineMatrixFromArray
            return jpype.JPackage('jline').lang.layered.ActivityPrecedence.fromActivities(
                preActList, postActList, preType, postType, jlineMatrixFromArray(preParams))
        elif postType is not None:
            return jpype.JPackage('jline').lang.layered.ActivityPrecedence.fromActivities(
                preActList, postActList, preType, postType)
        else:
            return jpype.JPackage('jline').lang.layered.ActivityPrecedence.fromActivities(
                preActList, postActList, preType)

    @staticmethod
    def getPrecedenceId(precedence):
        return jpype.JPackage('jline').lang.layered.ActivityPrecedence.getPrecedenceId(precedence)


class CacheTask:
    def __init__(self, model, name, items=1, itemLevelCap=1, replacementStrategy=None, multiplicity=1, schedStrategy=None, thinkTime=None):
        from .constants import GlobalConstants
        import math

        if replacementStrategy is None:
            replacementStrategy = ReplacementStrategy.FIFO
        if schedStrategy is None:
            schedStrategy = SchedStrategy.FCFS

        if multiplicity == float('inf') or multiplicity == float('-inf') or (isinstance(multiplicity, (int, float)) and math.isinf(multiplicity)):
            mult_value = GlobalConstants.MaxInt
        else:
            mult_value = int(multiplicity)

        if thinkTime is not None:
            self.obj = jpype.JPackage('jline').lang.layered.CacheTask(
                model.obj, name, int(items), int(itemLevelCap),
                replacementStrategy.value, mult_value, schedStrategy.value, thinkTime.obj)
        elif schedStrategy != SchedStrategy.FCFS:
            self.obj = jpype.JPackage('jline').lang.layered.CacheTask(
                model.obj, name, int(items), int(itemLevelCap),
                replacementStrategy.value, mult_value, schedStrategy.value)
        else:
            self.obj = jpype.JPackage('jline').lang.layered.CacheTask(
                model.obj, name, int(items), int(itemLevelCap),
                replacementStrategy.value, mult_value)

    def on(self, proc):
        """Assign this cache task to run on a processor."""
        self.obj.on(proc.obj)
        return self

    def setThinkTime(self, distrib):
        """Set the think time distribution for this cache task."""
        self.obj.setThinkTime(distrib.obj)
        return self

    def addPrecedence(self, prec):
        """Add an activity precedence relationship."""
        self.obj.addPrecedence(prec)

    def getItems(self):
        """Get the number of items in the cache."""
        return self.obj.getItems()

    def setItems(self, items):
        """Set the number of items in the cache."""
        self.obj.setItems(int(items))
        return self

    def getItemLevelCap(self):
        """Get the item level capacity."""
        return self.obj.getItemLevelCap()

    def setItemLevelCap(self, itemLevelCap):
        """Set the item level capacity."""
        self.obj.setItemLevelCap(int(itemLevelCap))
        return self

    def getReplacestrategy(self):
        """Get the replacement strategy."""
        java_strategy = self.obj.getReplacestrategy()
        for strategy in ReplacementStrategy:
            if strategy.value == java_strategy:
                return strategy
        return None

    def setReplacestrategy(self, replacementStrategy):
        """Set the replacement strategy."""
        self.obj.setReplacestrategy(replacementStrategy.value)
        return self

    set_think_time = setThinkTime
    get_items = getItems
    set_items = setItems
    get_item_level_cap = getItemLevelCap
    set_item_level_cap = setItemLevelCap
    get_replacestrategy = getReplacestrategy
    set_replacestrategy = setReplacestrategy


class ItemEntry:
    def __init__(self, model, name, cardinality, distribution):
        if hasattr(distribution, 'obj'):
            dist_obj = distribution.obj
        else:
            dist_obj = distribution

        self.obj = jpype.JPackage('jline').lang.layered.ItemEntry(
            model.obj, jpype.JPackage('java').lang.String(name), int(cardinality), dist_obj)

    def on(self, task):
        """Assign this entry to a parent task (typically a CacheTask)."""
        self.obj.on(task.obj)
        return self

    def getCardinality(self):
        """Get the number of items."""
        return self.obj.getCardinality()

    def getPopularity(self):
        """Get the popularity distribution."""
        java_dist = self.obj.getPopularity()
        from . import jlineFromDistribution
        return jlineFromDistribution(java_dist)

    get_cardinality = getCardinality
    get_popularity = getPopularity
