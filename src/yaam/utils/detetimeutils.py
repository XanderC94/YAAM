'''
Date and time utilities
'''

from dateutil.parser import parse as parse_timestamp


def compare_timestamp_str(timestamp1: str, timestamp2: str) -> float:
    '''
    Compare two datetime strings
    '''
    dt1 = parse_timestamp(timestamp1)
    dt2 = parse_timestamp(timestamp2)

    return dt1.timestamp() - dt2.timestamp()
