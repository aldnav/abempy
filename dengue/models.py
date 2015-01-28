
import random
from __init__ import rel_import
rel_import()
from abempy.core import models
from abempy.core.models import Agent
# Pull states from Agent
STATES = Agent.STATES
# Pull settings
import settings


class Person(models.Agent):
    """The person agent"""
    #: The duration of a person in INFECTED state
    infection_duration = random.randrange(
        *settings.disease["infection_duration"])

    def run(self):
        #: CASE: Currently infected so infection duration minimized
        if self.state is STATES.INFECTED:
            if self.infection_duration > 0:
                self.infection_duration -= 1
            #: CASE: Infection is over and now recover
            else:
                self.state = STATES.RECOVERED
                self.is_latent = False


class Mosquito(models.Agent):
    """The mosquito agent"""
    #: Tells whether the mosquito is dying
    is_dying = False
    #: Indicates the chance of mosquito's death by incidence
    death_probability = settings.contact["death_by_incidence"]

    def run(self):
        """
        [1] Survivability of the mosquito depends whether it is dying
        or not. If the mosquito is dying, remove from the environment
        and trigger spawning of new mosquito.
        [2] Bite persons
        [3] Evaluate death by probability
        """
        # TODO: If mosquito is dying, remove mosquito from manager
        # TODO: CREATE ENVIRONMENT FIRST!
        if self.is_dying:
            self.environment.mosquito_manager.queue.remove(self)
            # TODO: Trigger spawning
            return

        # bite persons!
        self.bite_persons()

        # evaluate if dying
        if random.random() < self.death_probability:
            self.is_dying = True

    def bite_persons(self):
        """
        Choose a person from the population and bite.
        If the person isn't infected yet and the mosquito is infected,
        chances are the person will get INFECTED.
        If the mosquito isn't infected yet and the person is infected,
        chances are the mosquitoe will get INFECTED.
        """
        #: Choose a person to bite
        target_person = random.choice(
            self.environment.person_manager.queue)
        # CASE: Person is not infected yet
        if not target_person.is_latent:
            # CASE: Mosquito is infected, person is susceptible
            if (target_person.state is STATES.SUSCEPTIBLE and
                    self.state is STATES.INFECTED):
                if random.random() < target_person.infection_probability:
                    target_person.state = STATES.INFECTED
                    target_person.is_latent = True
                    return
        # CASE: Mosquito is not infected yet
        if not self.is_latent:
            # CASE: Mosquito is susceptible, person is infected
            if (target_person.state is STATES.INFECTED and
                    self.state is STATES.SUSCEPTIBLE):
                if random.random() < self.infection_probability:
                    self.state = STATES.INFECTED
                    self.is_latent = True
                    return


class PersonManager(models.Manager):
    """Manages the person agents"""
    def __init__(self, queue, *args, **kwargs):
        models.Manager.__init__(self, queue, *args, **kwargs)
        self.__init_states()

    def __init_states(self):
        #: calculate each agent with states
        infected_count = int(
            settings.disease['initially_infected_persons'] *
            settings.environment['no_of_persons'])
        recovered_count = int(
            settings.disease['initially_recovered_persons'] *
            settings.environment['no_of_persons'])

        for person in self.queue:
            if infected_count > 0:
                person.state = STATES.INFECTED
                person.is_latent = True
                infected_count -= 1
            else:
                if recovered_count > 0:
                    person.state = STATES.RECOVERED
                    recovered_count -= 1
                else:
                    break


class MosquitoManager(models.Manager):
    """Manages the mosquito agents"""
    def __init__(self, queue, *args, **kwargs):
        models.Manager.__init__(self, queue, *args, **kwargs)
        self.__init_states()

    def __init_states(self):
        #: calculate each agent with states
        infected_count = int(
            settings.disease['initially_infected_mosquitoes'] *
            settings.environment['no_of_mosquitoes'])

        for mosquito in self.queue:
            if infected_count > 0:
                mosquito.state = STATES.INFECTED
                mosquito.is_latent = True
                infected_count -= 1
            else:
                break
