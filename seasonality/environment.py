
import os
import shutil
import time
import logging
from __init__ import rel_import
rel_import()
from abempy.core import environment
import settings

# ready the output folder
main_directory = settings.system['output_folder']
if not os.path.exists(main_directory):
    os.makedirs(main_directory)

# configure the output file and logger
file_name = "results-" + time.strftime("%Y%m%d-%H%M%S")
file_name = settings.system['test_name'] + file_name
# the directory specific to this run
output_dir = "{0}{1}/".format(main_directory, file_name)
os.makedirs(output_dir)
log_file = "{0}{1}.csv".format(output_dir, file_name)
# copy the config file
shutil.copy2(".config.json", output_dir)
logging.basicConfig(
    filename=log_file, level=logging.WARNING, format='%(message)s'
)


person_log_raw = []
mosquito_log_raw = []


class Environment(environment.Environment):
    """Envronment class"""

    def __init__(self, *args, **kwargs):
        environment.Environment.__init__(self)
        #: modules dependent on time may access this
        self.current_time = 0

    def associate_agents(self):
        """Tell the managers to associate agents with environment"""
        self.person_manager.__associate_agents_to_environment__()
        self.mosquito_manager.__associate_agents_to_environment__()

    def simulate(self):
        to_log_results = settings.system['generate_output_file']
        if to_log_results:
            self.log_headers()
        time_steps = settings.environment['time_steps']
        for time_step in xrange(1, time_steps+1):
            print '.',
            if time_step % 10 == 0:
                print '\t', time_step
            #: update current time
            self.current_time = time_step-1
            if to_log_results:
                #: optional logging of results
                self.log_results(time_step-1)
            #: run managers
            self.mosquito_manager.run()
            self.person_manager.run()
        # generate excel report
        self.export_excel()

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

        line_person = """{0},{1},{2}""".format(
            self.person_manager.count_susceptible(),
            self.person_manager.count_infected(),  # person SIR
            self.person_manager.count_recovered()
        )
        person_log_raw.append(tuple([int(x) for x in line_person.split(",")]))

        line_mosquito = """{0},{1}""".format(
            self.mosquito_manager.count_susceptible(),
            self.mosquito_manager.count_infected()  # mosquito SI
        )
        mosquito_log_raw.append(tuple(
            [int(x) for x in line_mosquito.split(",")]))

    def export_excel(self):

        import tablib
        # save into databook
        databook = tablib.Databook()

        # separate data sheets each log
        # specify sheet name from settings
        for report, data_raw in zip(
                settings.REPORTS, [person_log_raw, mosquito_log_raw]):
            datasheet = tablib.Dataset(
                *data_raw, headers=report[1], title=report[0])
            databook.add_sheet(datasheet)
        output_file = "{0}{1}.xls".format(output_dir, file_name)
        with open(output_file, "wb") as f:
            f.write(databook.xls)
