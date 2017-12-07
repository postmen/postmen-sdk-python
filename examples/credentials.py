from __future__ import print_function

import pprint

pp = pprint.PrettyPrinter(indent=4)

from postmen import Postmen
from postmen import PostmenException

# TODO put your own API key here
key = None

# TODO region of the Postmen instance
region = None

# TODO if you need a custom endpoint
endpoint = None

if key is None :
    print('key is not set, modify file credentials.py')

if region is None:
    print('region is not set, modify file credentials.py')
