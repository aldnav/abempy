
from models import Person, Mosquito, PersonManager, MosquitoManager
from environment import Environment
import settings


def main():
    # Get the environment ready
    num_of_persons = settings.environment['no_of_persons']
    num_of_mosquitoes = settings.environment['no_of_mosquitoes']
    env = Environment()
    pq = [Person() for x in xrange(num_of_persons)]
    mq = [Mosquito() for x in xrange(num_of_mosquitoes)]
    #: Refer this environment to managers
    pm = PersonManager(pq, environment=env)
    mm = MosquitoManager(mq, environment=env)
    #: Keep track of managers
    env.person_manager = pm
    env.mosquito_manager = mm
    #: Nullify temporary queues
    pq, mq = None, None
    #: Associate agents to environment
    env.associate_agents()

    env.simulate()

if __name__ == '__main__':
    if settings.system['profile']:
        import cProfile
        cProfile.run('main()')
    else:
        main()
