import os

def load_config(path):
	try:
		import yaml
	except ImportError:
		raise ImportError("pyyaml is required to load YAML config files. Please install pyyaml.")
	with open(path, 'r', encoding='utf-8') as f:
		config = yaml.safe_load(f)
	# Environment variable override for 'enabled'
	ra_enabled = os.environ.get('RA_ENABLED')
	if ra_enabled is not None:
		# Interpret '1', 'true', 'yes' as True
		config['enabled'] = ra_enabled.lower() in ('1', 'true', 'yes')
	return config
