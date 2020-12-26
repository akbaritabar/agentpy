""" Agentpy Network Module """

import networkx as nx
from .objects import ApEnv, Agent
from .lists import AgentList


class Network(ApEnv):
    """ Agent environment with a graph topology.

    This class can be used as a parent class for custom network types.
    Unknown attribute and method calls are forwarded to self.graph.

    Notes:
        All agentpy model objects can access attributes as items
        and will call the method ``setup()`` after creation (if defined).

    Arguments:
        model (Model): The model instance.
        key (str, optional): The environments' name.
        graph (networkx.Graph, optional): The environments' graph.
            Agents of the same number as graph nodes must be passed.
            If none is passed, an empty graph is created.
        agents (AgentList, optional): Agents of the network (default None).
            If a graph is passed, agents are mapped to each node of the graph.
            Otherwise, new nodes will be created for each agent.
        **kwargs: Will be forwarded to :func:`Network.setup`.
    """

    def __init__(self, model, graph=None, agents=None, **kwargs):

        super().__init__(model)

        if graph is None:
            self.graph = nx.Graph()
            if agents:
                self.add_agents(agents)
        elif isinstance(graph, nx.Graph):
            self.graph = graph
            # Map each agent to a node of the graph
            if agents is None or len(agents) != len(self.graph.nodes):
                la = len(agents) if agents else 0
                ln = len(self.graph.nodes)
                raise ValueError(
                    f"Number of agents ({la}) in 'agents' doesn't match "
                    f"number of nodes ({ln}) in graph.")
            super().add_agents(agents)  # Add agents without new nodes
            mapping = {i: agent for i, agent in enumerate(agents)}
            nx.relabel_nodes(self.graph, mapping=mapping, copy=False)
        else:
            raise TypeError("Argument 'graph' must be of type networkx.Graph")

        self._topology = 'network'
        self._set_var_ignore()
        self.setup(**kwargs)

    def add_agents(self, agents, agent_class=Agent, **kwargs):
        """ Adds agents to the network environment as new nodes.
        See :func:`Environment.add_agents` for standard arguments.
        """
        new_agents = super().add_agents(agents, agent_class, **kwargs)
        for agent in new_agents:
            self.graph.add_node(agent)  # Add agents to graph as new nodes

    def neighbors(self, agent, mode=None):
        """ Returns an :class:`AgentList` of agents
        that are connected to the passed agent. """
        return AgentList([n for n in self.graph.neighbors(agent)])

    def __getattr__(self, name):
        # Forward unknown method call to self.graph
        def method(*args, **kwargs):
            return getattr(self.graph, name)(*args, **kwargs)

        try:
            return method
        except AttributeError:
            raise AttributeError(
                f"Environment '{self.key}' has no attribute '{name}'")
