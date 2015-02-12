# TODO: can move to other file
class Enum(set):

    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError


class Agent(object):

    """The abstract class for agents in simulation"""
    #: Add states of agents here
    # STATES = enum('SUSCEPTIBLE', 'INFECTED', 'RECOVERED')
    STATES = Enum(['SUSCEPTIBLE', 'INFECTED', 'RECOVERED'])

    def __init__(self, state=STATES.SUSCEPTIBLE, *args, **kwargs):
        #: The current state of the agent
        self.state = state
        #: The environment the agent is in
        self.environment = kwargs.pop('environment', None)
        #: Tells whether an agent is latent or not
        self.is_latent = False
        #: Probability of an agent to be infected
        self.infection_probability = kwargs.pop('infection_probability', 0.0)

    def run(self):
        pass


class Manager(object):

    """The abstract class for manager of agents"""

    def __init__(self, queue, *args, **kwargs):
        #: Associate the environment
        self.environment = kwargs.pop("environment", None)
        #: Queue for all agents
        self.queue = queue

    #: Associate all agents in queue to the same environment
    def __associate_agents_to_environment__(self):
        for agent in self.queue:
            agent.environment = self.environment

    #: Returns the number of susceptible agents
    def count_susceptible(self):
        return len(
            [a for a in self.queue if a.state == Agent.STATES.SUSCEPTIBLE]
        )

    #: Returns the number of infected agents
    def count_infected(self):
        return len([a for a in self.queue if a.state == Agent.STATES.INFECTED])

    #: Returns the number of recovered agents
    def count_recovered(self):
        return len([a for a in self.queue if a.state == Agent.STATES.RECOVERED])

    #: Deprecated! Do not use. Extremely slow!
    def count_by_states(self):
        susceptible = 0
        recovered = 0
        infected = 0

        for a in self.queue:
            if a.state == Agent.STATES.SUSCEPTIBLE:
                susceptible += 1
            elif a.state == Agent.STATES.INFECTED:
                infected += 1
            else:
                recovered += 1

        return (susceptible, infected, recovered)

    def run(self):
        for agent in self.queue:
            agent.run()
