"""set up basepair package"""
from __future__ import print_function
import os
import sys

import requests

from .utils import colors

# Exposing infra webapp library
from .infra.webapp import (
	Analysis,
	File,
	Gene,
	Genome,
	GenomeFile,
	Host,
	Module,
	Pipeline,
	Project,
	Sample,
	Upload,
	User,
)

# Exposing the storage wrapper

__title__ = "basepair"
__version__ = "2.4.0"
__copyright__ = "Copyright [2017] - [2025] Basepair INC"


JSON_URL = f"https://pypi.python.org/pypi/{__title__}/json"

if not os.environ.get("SECRETS_DRIVER") == "local":
	try:
		resp = requests.get(JSON_URL, timeout=1)
		if resp.status_code == 200:
			latest_version = resp.json()["info"]["version"]
			if latest_version != __version__:
				print(
					colors.color.warning(
						f"WARNING: The latest version of basepair package is {latest_version}. "
						"Please upgrade to avail the latest features and bug-fixes"
					),
					file=sys.stderr,
				)
	except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
		print("warning: no internet", file=sys.stderr)


def connect(*args, **kwargs):
	"""return basepair package"""
    # pylint: disable=import-outside-toplevel
	from basepair.api import BpApi
	return BpApi(*args, **kwargs)
