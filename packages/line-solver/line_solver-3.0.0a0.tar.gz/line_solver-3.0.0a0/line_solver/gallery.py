
from line_solver import *
from line_solver import Erlang, SchedStrategy


def gallery_aphm1():
    model = Network('APH/M/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    alpha = [1, 0]
    T = [[-2, 1.5], [0, -1]]
    e = [[0.5], [1]]
    source.setArrival(oclass, APH(alpha, T, e))
    queue.setService(oclass, Exp(2))
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_coxm1():
    model = Network('Cox/M/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Coxian.fitMeanAndSCV(1.0, 4.0))
    queue.setService(oclass, Exp(2))
    model.link(Network.serialRouting(source, queue, sink))
    return model

def gallery_detm1():
    model = Network('D/M/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Det(1))
    queue.setService(oclass, Exp(2))
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_erlm1():
    model = Network('Er/M/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Erlang.fitMeanAndOrder(1, 5))
    queue.setService(oclass, Exp(2))
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_erlm1ps():
    model = Network('Er/M/1-PS')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.PS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Erlang.fitMeanAndOrder(1, 5))
    queue.setService(oclass, Exp(2))
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_gamm1():
    model = Network('Gam/M/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Gamma.fitMeanAndSCV(1, 1 / 5))
    queue.setService(oclass, Exp(2))
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_hyperlk(k=2):
    model = Network('H/Er/k')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, HyperExp.fitMeanAndSCVBalanced(1.0 / 1.8, 4))
    queue.setService(oclass, Erlang.fitMeanAndSCV(1, 0.25))
    queue.setNumberOfServers(k)
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_hypm1():
    model = Network('H/M/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, HyperExp.fitMeanAndSCV(1, 64))
    queue.setService(oclass, Exp(2))
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_mhyp1():
    model = Network('M/H/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Exp(1))
    queue.setService(oclass, Coxian.fitMeanAndSCV(0.5, 4))
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_merl1():
    model = Network('M/E/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Exp(1))
    queue.setService(oclass, Erlang.fitMeanAndOrder(0.5, 2))
    model.link(Network.serialRouting(source, queue, sink))
    return model, source, queue, sink, oclass


def gallery_mm1():
    model = Network('M/M/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Exp(1))
    queue.setService(oclass, Exp(2))
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_mm1_linear(n=2, Umax=0.9):
    model = Network('M/M/1-Linear')

    line = [Source(model, 'mySource')]
    for i in range(1, n + 1):
        line.append(Queue(model, 'Queue' + str(i), SchedStrategy.FCFS))
    line.append(Sink(model, 'mySink'))

    oclass = OpenClass(model, 'myClass')
    line[0].setArrival(oclass, Exp(1.0))

    if n == 2:
        means = np.linspace(Umax, Umax, 1)
    else:
        means = np.linspace(0.1, Umax, n // 2)

    if n % 2 == 0:
        means = np.concatenate([means, means[::-1]])
    else:
        means = np.concatenate([means, [Umax], means[::-1]])

    for i in range(1, n + 1):
        line[i].setService(oclass, Exp.fitMean(means[i - 1]))

    model.link(Network.serialRouting(line))
    return model


def gallery_mm1_tandem():
    return gallery_mm1_linear(2)


def gallery_mmk(k=2):
    model = Network('M/M/k')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Exp(1))
    queue.setService(oclass, Exp(2))
    queue.setNumberOfServers(k)
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_mpar1():
    model = Network('M/Par/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Exp(1))
    queue.setService(oclass, Pareto.fitMeanAndSCV(0.5, 64))
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_parm1():
    model = Network('Par/M/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Pareto.fitMeanAndSCV(1, 64))
    queue.setService(oclass, Exp(2))
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_um1():
    model = Network('U/M/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Uniform(1, 2))
    queue.setService(oclass, Exp(2))
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_cqn(M=2, useDelay=False, seed=2300):
    model = Network('CQN')

    stations = []
    for i in range(M):
        station = Queue(model, f'Queue{i+1}', SchedStrategy.PS)
        stations.append(station)

    if useDelay:
        delay = Delay(model, 'Delay')
        stations.append(delay)

    refStation = stations[0] if not useDelay else stations[-1]
    jobclass = ClosedClass(model, 'Jobs', 20, refStation)

    np.random.seed(seed)
    for i, station in enumerate(stations):
        if isinstance(station, Queue):
            rate = 0.1 + 0.9 * np.random.random()
            station.setService(jobclass, Exp(rate))
        elif isinstance(station, Delay):
            station.setService(jobclass, Exp(0.1))

    if len(stations) == 1:
        model.link(Network.selfRouting(stations[0]))
    else:
        model.link(Network.serialRouting(stations))

    return model


def gallery_mm1_feedback(p=0.5):
    model = Network('M/M/1-Feedback')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')
    source.setArrival(oclass, Exp(1))
    queue.setService(oclass, Exp(2))
    model.link(Network.serialRouting(source, queue, sink))
    return model


def gallery_mm1_prio():
    model = Network('M/M/1-Priority')
    source1 = Source(model, 'HighPrioSource')
    source2 = Source(model, 'LowPrioSource')
    queue = Queue(model, 'myQueue', SchedStrategy.HOL)
    sink = Sink(model, 'mySink')

    highPrioClass = OpenClass(model, 'HighPrio')
    lowPrioClass = OpenClass(model, 'LowPrio')

    queue.setPriorityClass(highPrioClass, 1)
    queue.setPriorityClass(lowPrioClass, 2)

    source1.setArrival(highPrioClass, Exp(0.3))
    source2.setArrival(lowPrioClass, Exp(0.5))
    queue.setService(highPrioClass, Exp(2))
    queue.setService(lowPrioClass, Exp(2))

    model.link(Network.serialRouting(source1, queue, sink))
    model.link(Network.serialRouting(source2, queue, sink))
    return model


def gallery_mm1_multiclass():
    model = Network('M/M/1-MultiClass')
    source1 = Source(model, 'Source1')
    source2 = Source(model, 'Source2')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')

    class1 = OpenClass(model, 'Class1')
    class2 = OpenClass(model, 'Class2')

    source1.setArrival(class1, Exp(0.4))
    source2.setArrival(class2, Exp(0.6))
    queue.setService(class1, Exp(1.5))
    queue.setService(class2, Exp(1.0))

    model.link(Network.serialRouting(source1, queue, sink))
    model.link(Network.serialRouting(source2, queue, sink))
    return model


def gallery_mapm1(map_arrival=None):
    model = Network('MAP/M/1')
    source = Source(model, 'mySource')
    queue = Queue(model, 'myQueue', SchedStrategy.FCFS)
    sink = Sink(model, 'mySink')
    oclass = OpenClass(model, 'myClass')

    if map_arrival is None:
        D0 = [[-2, 0], [0, -1]]
        D1 = [[1.5, 0.5], [0.8, 0.2]]
        map_arrival = MAP(D0, D1)

    source.setArrival(oclass, map_arrival)
    queue.setService(oclass, Exp(2))
    model.link(Network.serialRouting(source, queue, sink))
    return model
