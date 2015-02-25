

__config_file__ = '.config.json'
__matrix_file__ = 'matrix.csv'

import json

with open(__config_file__) as f:
    # include in namespace the configuration details
    globals().update(json.loads(f.read()))

__indices = (
    "time_steps", "death_by_incidence", "infection_duration",
    "infection_probability_person", "infection_probability_mosquito",
    "no_of_persons", "no_of_mosquitoes"
)

# prepare the great parameter matrix
MATRIX = []
for i in xrange(environment['time_steps']):
    MATRIX.append([
        i, contact['death_by_incidence'], disease['infection_duration'],
        disease['infection_probability_person'], disease['infection_probability_mosquito'],
        environment['no_of_persons'], environment['no_of_mosquitoes']
    ])

#: dynamic set-up of matrix changes due to seasonal variation
for season in system['seasons']:
    season = globals().get(season)
    for time in season['times']:
        for i in xrange(time[0], time[1]):
            if 'contact' in season:
                for setting in season['contact']:
                    MATRIX[i][__indices.index(setting)] = season['contact'][setting]
            if 'disease' in season:
                for setting in season['disease']:
                    MATRIX[i][__indices.index(setting)] = season['disease'][setting]

import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(MATRIX)

# write matrix to external csv file
import csv
with open(__matrix_file__, 'w') as csvfile:
    fieldnames = __indices
    writer = csv.writer(csvfile)
    writer.writerow(fieldnames)
    writer.writerows(MATRIX)