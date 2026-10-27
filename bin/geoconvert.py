"""
geoconvert <x_field> <y_field>

Streaming search command: converts KATEC (Naver TM128) coordinates in the two
given fields to WGS84 and adds x_long (longitude) and y_lat (latitude).
Events whose fields are missing or not numeric get empty x_long / y_lat.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))

from splunklib.searchcommands import Configuration, StreamingCommand, dispatch  # noqa: E402

from katec import katec_to_wgs84  # noqa: E402


@Configuration()
class GeoConvertCommand(StreamingCommand):

    def stream(self, records):
        if len(self.fieldnames) != 2:
            # Reported this way (not raised) so Splunk shows the message instead of "exited with code 1".
            self.write_error('Usage: geoconvert <x_field> <y_field>')
            return
        x_field, y_field = self.fieldnames
        for record in records:
            # Always set both fields: the SDK takes a chunk's columns from its first record.
            record['x_long'] = record['y_lat'] = None
            try:
                x = float(record[x_field])
                y = float(record[y_field])
            except (KeyError, TypeError, ValueError):
                yield record
                continue
            if math.isfinite(x) and math.isfinite(y):
                record['x_long'], record['y_lat'] = katec_to_wgs84(x, y)
            yield record


dispatch(GeoConvertCommand, sys.argv, sys.stdin, sys.stdout, __name__)
