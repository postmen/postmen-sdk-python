from __future__ import print_function

from credentials import *

# most obvious way would be to surround our
# call using try...except section
# pay attention to details attribute of the
# exception which will inform you what
# is wrong with your payload

try:
    api = Postmen('THIS IS NOT A VALID API KEY', region)
    result = api.get('labels')
except PostmenException as e:
    print("ERROR")
    print(e.code())
    print(e.message())
    print(e.details())

# we also can enable the safe mode,
# this way try...except... is no
# longer required

# check if error occured in the constructor

api = Postmen('THIS IS NOT A VALID API KEY', region, safe=True)
e = api.getError()
if e is not None:
    print("ERROR IN THE CONSTRUCTOR")
    print(e.code())
    print(e.message())
    print(e.details())

# perform call anyway

result = api.get('labels')
if result is None:
    e = api.getError()
    print("ERROR IN THE CALL")
    print(e.code())
    print(e.message())
    print(e.details())
