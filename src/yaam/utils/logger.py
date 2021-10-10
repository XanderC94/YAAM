'''
Simple static logging utility module
'''
import logging

def static_logger(name = None):
    '''
    Simple static logger
    '''
    return logging.getLogger(name)
    