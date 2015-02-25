
import time
import logging
import glob
from __init__ import rel_import
rel_import()
from abempy.core import environment
import settings

# configure the output file and logger
path = "/".join(glob.glob(__file__)[0].split('/')[:-1]) + "/results/"
file_name = "results" + time.strftime("%Y%m%d-%H%M%S")
output_file = "{0}{1}.csv".format(path, file_name)
logging.basicConfig(
    filename=output_file, level=logging.WARNING, format='%(message)s'
)


class Environment(environment.Environment):
    """Envronment class"""

    def __init__(self, *args, **kwargs):
        environment.Environment.__init__(self)

    def associate_agents(self):
        """Tell the managers to associate agents with environment"""
        self.person_manager.__associate_agents_to_environment__()
        self.mosquito_manager.__associate_agents_to_environment__()

    def simulate(self):
        self.log_headers()
        time_steps = settings.environment['time_steps']
        to_log_results = settings.system['generate_output_file']
        for time_step in xrange(1, time_steps+1):
            if to_log_results:
                self.log_results(time_step)
            self.mosquito_manager.run()
            self.person_manager.run()

    def log_headers(self):
        line = """{0},{1},{2},{3},{4}""".format(
            "P_Susceptible", "P_Infected",  # person SIR
            "P_Recover",
            "M_Susceptible", "M_Infected"  # mosquito SI
        )
        logging.warning(line)

    def log_results(self, time_step):
        line = """{0},{1},{2},{3},{4}""".format(
            self.person_manager.count_susceptible(),
            self.person_manager.count_infected(),  # person SIR
            self.person_manager.count_recovered(),
            self.mosquito_manager.count_susceptible(),
            self.mosquito_manager.count_infected()  # mosquito SI
        )
        logging.warning(line)
