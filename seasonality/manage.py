
import sys
# check to see if arguments given
argv = sys.argv
if argv[1:]:
    config_file = argv[1]
print "Run with config: ", config_file

# invoke a config_file first before even instantiating settings
import os
os.system('python settings.py ' + config_file)
import settings
# settings.config_file = config_file
from models import Person, Mosquito, PersonManager, MosquitoManager
from environment import Environment


def main(argv):
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
        cProfile.run('main(sys.argv)')
    else:
        main(sys.argv)
