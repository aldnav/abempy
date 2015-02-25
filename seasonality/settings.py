

__config_file__ = '.config.json'

import json

with open(__config_file__) as f:
	# include in namespace the configuration details
	globals().update(json.loads(f.read()))