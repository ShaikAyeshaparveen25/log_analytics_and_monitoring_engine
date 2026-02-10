import re

def parse_log_line(line):
    log_pattern = r'^(?P<timestamp>\S+ \S+) (?P<level>\S+) (?P<service>\S+) (?P<message>.+)$'
    match = re.match(log_pattern, line)

    if match:
        return match.groupdict()
    else:
        return None

    # groupdict() -> converts raw data into structured dictionary
    # r'' -> raw string
    # ?P<timestamp> -> named group
    # \S+ -> non-space characters (one or more)
    # ^ -> start of line
    # $ -> end of line
