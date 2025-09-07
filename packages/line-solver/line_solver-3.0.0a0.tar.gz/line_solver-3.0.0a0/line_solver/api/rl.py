
import jpype
import numpy as np
from line_solver import jlineMatrixToArray, jlineMatrixFromArray


class RlEnv:

    def __init__(self, model, idx_of_queue_in_nodes, idx_of_source_in_nodes, state_size, gamma):
        """Initialize the RL environment."""
        self._java_env = jpype.JPackage('jline').api.rl.RlEnv(
            model,
            jpype.JArray(jpype.JInt)(idx_of_queue_in_nodes),
            jpype.JArray(jpype.JInt)(idx_of_source_in_nodes),
            jpype.JInt(state_size),
            jpype.JDouble(gamma)
        )

    @property
    def model(self):
        """Get the network model."""
        return self._java_env.model

    @property
    def action_size(self):
        """Get the number of possible actions."""
        return self._java_env.actionSize

    def is_in_state_space(self, nodes):
        java_nodes = jpype.JArray(jpype.JObject)(len(nodes))
        for i, node in enumerate(nodes):
            java_nodes[i] = jpype.JInt(node)
        return self._java_env.isInStateSpace(java_nodes)

    def is_in_action_space(self, nodes):
        java_nodes = jpype.JArray(jpype.JObject)(len(nodes))
        for i, node in enumerate(nodes):
            java_nodes[i] = jpype.JInt(node)
        return self._java_env.isInActionSpace(java_nodes)

    def sample(self):
        result = self._java_env.sample()
        return result.getFirst(), result.getSecond()

    def update(self, new_state):
        java_state = jpype.JArray(jpype.JInt)(new_state)
        self._java_env.update(java_state)

    def reset(self):
        """Reset environment to initial state."""
        self._java_env.reset()


class RlEnvGeneral:

    def __init__(self, model, idx_of_queue_in_nodes, idx_of_action_nodes, state_size, gamma):
        """Initialize the general RL environment."""
        self._java_env = jpype.JPackage('jline').api.rl.RlEnvGeneral(
            model,
            jpype.JArray(jpype.JInt)(idx_of_queue_in_nodes),
            jpype.JArray(jpype.JInt)(idx_of_action_nodes),
            jpype.JInt(state_size),
            jpype.JDouble(gamma)
        )

    @property
    def model(self):
        """Get the network model."""
        return self._java_env.model

    @property
    def nqueues(self):
        """Get the number of queues."""
        return self._java_env.nqueues

    @property
    def action_space(self):
        """Get the action space mapping."""
        return self._java_env.actionSpace

    def is_in_state_space(self, state):
        java_state = jpype.JArray(jpype.JInt)(state)
        return self._java_env.isInStateSpace(java_state)

    def is_in_action_space(self, state):
        java_state = jpype.JArray(jpype.JInt)(state)
        return self._java_env.isInActionSpace(java_state)

    def sample(self):
        return self._java_env.sample()

    def update(self, sample):
        self._java_env.update(sample)

    def reset(self):
        """Reset environment to initial state."""
        self._java_env.reset()


class RlTDAgent:

    def __init__(self, lr=0.05, epsilon=1.0, eps_decay=0.99):
        """Initialize the TD agent."""
        self._java_agent = jpype.JPackage('jline').api.rl.RlTDAgent(
            jpype.JDouble(lr),
            jpype.JDouble(epsilon),
            jpype.JDouble(eps_decay)
        )

    def reset(self, env):
        self._java_agent.reset(env._java_env)

    def get_value_function(self):
        v = self._java_agent.getValueFunction()
        if v is None:
            return None

        result = np.zeros((len(v), len(v[0])))
        for i in range(len(v)):
            for j in range(len(v[i])):
                result[i][j] = v[i][j]
        return result

    def get_q_function(self):
        q = self._java_agent.getQFunction()
        if q is None:
            return None

        result = np.zeros((len(q), len(q[0]), len(q[0][0])))
        for i in range(len(q)):
            for j in range(len(q[i])):
                for k in range(len(q[i][j])):
                    result[i][j][k] = q[i][j][k]
        return result

    def solve(self, env):
        self._java_agent.solve(env._java_env)

    @staticmethod
    def create_greedy_policy(state_q, epsilon, n_a):
        result = jpype.JPackage('jline').api.rl.RlTDAgent.createGreedyPolicy(
            jpype.JArray(jpype.JDouble)(state_q),
            jpype.JDouble(epsilon),
            jpype.JInt(n_a)
        )
        return np.array(result)

    @staticmethod
    def get_state_from_loc(obj_size, loc):
        result = jpype.JPackage('jline').api.rl.RlTDAgent.getStateFromLoc(
            jpype.JArray(jpype.JInt)(obj_size),
            jpype.JArray(jpype.JInt)(loc)
        )
        return np.array(result)


class RlTDAgentGeneral:

    def __init__(self, lr=0.1, epsilon=1.0, eps_decay=0.9999):
        """Initialize the advanced TD agent."""
        self._java_agent = jpype.JPackage('jline').api.rl.RlTDAgentGeneral(
            jpype.JDouble(lr),
            jpype.JDouble(epsilon),
            jpype.JDouble(eps_decay)
        )

    def reset(self, env):
        self._java_agent.reset(env._java_env)

    def get_value_function(self):
        v = self._java_agent.getValueFunction()
        if v is None:
            return None

        result = np.zeros((len(v), len(v[0])))
        for i in range(len(v)):
            for j in range(len(v[i])):
                result[i][j] = v[i][j]
        return result

    def solve_for_fixed_policy(self, env, num_episodes=10000):
        result = self._java_agent.solveForFixedPolicy(env._java_env, jpype.JInt(num_episodes))

        v = np.zeros((len(result), len(result[0])))
        for i in range(len(result)):
            for j in range(len(result[i])):
                v[i][j] = result[i][j]
        return v

    def solve(self, env, num_episodes=10000):
        result = self._java_agent.solve(env._java_env, jpype.JInt(num_episodes))

        v = np.zeros((len(result), len(result[0])))
        for i in range(len(result)):
            for j in range(len(result[i])):
                v[i][j] = result[i][j]
        return v

    def solve_by_hashmap(self, env, num_episodes=10000):
        result = self._java_agent.solveByHashmap(env._java_env, jpype.JInt(num_episodes))

        v_java = result.getFirst()
        v = np.zeros((len(v_java), len(v_java[0])))
        for i in range(len(v_java)):
            for j in range(len(v_java[i])):
                v[i][j] = v_java[i][j]

        rewards = np.array(result.getSecond())

        return v, rewards

    def solve_by_linear(self, env, num_episodes=10000):
        result = self._java_agent.solveByLinear(env._java_env, jpype.JInt(num_episodes))

        v_java = result.getFirst()
        v = np.zeros((len(v_java), len(v_java[0])))
        for i in range(len(v_java)):
            for j in range(len(v_java[i])):
                v[i][j] = v_java[i][j]

        rewards = np.array(result.getSecond())
        theta = np.array(result.getThird())

        return v, rewards, theta

    def solve_by_quad(self, env, num_episodes=10000):
        result = self._java_agent.solveByQuad(env._java_env, jpype.JInt(num_episodes))

        v_java = result.getFirst()
        v = np.zeros((len(v_java), len(v_java[0])))
        for i in range(len(v_java)):
            for j in range(len(v_java[i])):
                v[i][j] = v_java[i][j]

        rewards = np.array(result.getSecond())
        theta = np.array(result.getThird())

        return v, rewards, theta

    @staticmethod
    def create_greedy_policy(state_q, epsilon, n_a):
        result = jpype.JPackage('jline').api.rl.RlTDAgentGeneral.createGreedyPolicy(
            jpype.JArray(jpype.JDouble)(state_q),
            jpype.JDouble(epsilon),
            jpype.JInt(n_a)
        )
        return np.array(result)