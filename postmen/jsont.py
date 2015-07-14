import json
import datetime

import six
import dateutil.parser


class JSONWithDatetimeEncoder(json.JSONEncoder):
    """Create JSON string as json.JSONEncoder, convert datetime.datetime objects to ISO format string."""
    def default(self, o):
        o = o.isoformat() if isinstance(o, datetime.datetime) else json.JSONEncoder.default(self, o)
        return o


class JSONWithDatetimeDecoder(json.JSONDecoder):
    """Parse JSON string as json.JSONDecoder, matched strings convert to datetime.datetime."""
    def decode(self, s):
        o = json.JSONDecoder.decode(self, s)
        return self.handleObj(o)

    def handleObj(self, o):
        if isinstance(o, dict):
            keys = list(o.keys())
            for key in keys:
                val = o[key]
                o[key] = self.handleObj(val)
            return o
        if isinstance(o, list):
            c = []
            for val in o:
                c.append(self.handleObj(val))
            return c
        if isinstance(o, six.string_types):
            try:
                return dateutil.parser.parse(o)
            except:
                pass
        return o