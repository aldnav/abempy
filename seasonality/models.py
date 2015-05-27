
import random
from __init__ import rel_import
rel_import()
from abempy.core import models
from abempy.core.models import Agent
# Pull states from Agent
STATES = Agent.STATES
# Pull settings
import settings

# List id's here
ID_DEATH_BY_INCIDENCE = settings.__indices.index('death_by_incidence')
ID_INFECTION_PROBABILITY_PERSON = settings.__indices.index(
    'infection_probability_person')
ID_INFECTION_PROBABILITY_MOSQUITO = settings.__indices.index(
    'infection_probability_mosquito')


class Person(models.Agent):

    """
    The person agent"""

    def __init__(self, *args, **kwargs):
        models.Agent.__init__(self, *args, **kwargs)
        self.infection_duration = random.randrange(
            *settings.disease["infection_duration"])
        self.infection_probability = float(
            settings.disease["infection_probability_person"])

    def pre_run(self):
        #: update attributes according to time
        self.cur_time = self.environment.current_time
        #: pull from MATRIX
        self.infection_probability = settings.MATRIX[
            self.cur_time][ID_INFECTION_PROBABILITY_PERSON]

    def run(self):
        #: update attributes first
        self.pre_run()

        #: CASE: Currently infected so infection duration minimized
        if self.state is STATES.INFECTED:
            if self.infection_duration > 0:
                self.infection_duration -= 1
            #: CASE: Infection is over and now recover
            else:
                self.state = STATES.RECOVERED
                self.is_latent = False
                # update person manager
                self.environment.person_manager.counter_recovered += 1
                self.environment.person_manager.counter_infected -= 1


class Mosquito(models.Agent):

    """The mosquito agent"""

    def __init__(self, *args, **kwargs):
        models.Agent.__init__(self, *args, **kwargs)
        #: Tells whether the mosquito is dying
        self.is_dying = False
        #: Indicates the chance of mosquito's death by incidence
        self.death_probability = float(settings.contact["death_by_incidence"])
        #: Indicates the chance of the mosquito to get infected
        self.infection_probability = float(
            settings.disease["infection_probability_mosquito"])
        #: Indicates the number of bites per day
        self.number_of_bites = int(settings.contact["number_of_bites"])

    def pre_run(self):
        #: update attributes according to time
        self.cur_time = self.environment.current_time
        #: pull from MATRIX
        self.death_probability = settings.MATRIX[
            self.cur_time][ID_DEATH_BY_INCIDENCE]
        self.infection_probability = settings.MATRIX[
            self.cur_time][ID_INFECTION_PROBABILITY_MOSQUITO]

    def run(self):
        """
        [1] Survivability of the mosquito depends whether it is dying
        or not. If the mosquito is dying, remove from the environment
        and trigger spawning of new mosquito.
        [2] Bite persons
        [3] Evaluate death by probability
        """
        #: Update attributes first
        self.pre_run()

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
        current_number_of_bites = random.randint(0, self.number_of_bites)
        for number_of_bites in xrange(current_number_of_bites):
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
                        # update person manager
                        self.environment.person_manager.counter_infected += 1
                        self.environment.person_manager.counter_susceptible -= 1
                        continue
            # CASE: Mosquito is not infected yet
            if not self.is_latent:
                # CASE: Mosquito is susceptible, person is infected
                if (target_person.state is STATES.INFECTED and
                        self.state is STATES.SUSCEPTIBLE):
                    if random.random() < self.infection_probability:
                        self.state = STATES.INFECTED
                        self.is_latent = True
                        # update mosquito manager
                        self.environment.mosquito_manager.counter_infected += 1
                        self.environment.mosquito_manager.counter_susceptible -= 1
                        continue


class PersonManager(models.Manager):
    # counters for states
    counter_susceptible = 0
    counter_infected = 0
    counter_recovered = 0

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

        #: reset counters for states
        self.counter_susceptible = int(settings.environment['no_of_persons']) -\
            (infected_count + recovered_count)
        self.counter_infected = infected_count
        self.counter_recovered = recovered_count

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

    def count_susceptible(self):
        return self.counter_susceptible

    def count_infected(self):
        return self.counter_infected

    def count_recovered(self):
        return self.counter_recovered


class MosquitoManager(models.Manager):
    # counters for states
    counter_susceptible = 0
    counter_infected = 0

    """Manages the mosquito agents"""

    def __init__(self, queue, *args, **kwargs):
        models.Manager.__init__(self, queue, *args, **kwargs)
        self.__init_states()

    def __init_states(self):
        #: calculate each agent with states
        infected_count = int(
            settings.disease['initially_infected_mosquitoes'] *
            settings.environment['no_of_mosquitoes'])
        #: reset counters for states
        self.counter_susceptible = int(settings.environment['no_of_persons']) -\
            infected_count
        self.counter_infected = infected_count

        for mosquito in self.queue:
            if infected_count > 0:
                mosquito.state = STATES.INFECTED
                mosquito.is_latent = True
                infected_count -= 1
            else:
                break

    def count_susceptible(self):
        return self.counter_susceptible

    def count_infected(self):
        return self.counter_infected
