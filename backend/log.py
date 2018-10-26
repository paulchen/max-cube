#!/usr/bin/python3

import os, logging

path = os.path.dirname(os.path.abspath(__file__)) + '/'

logfile = path + 'log/max.log'

logger = logging.getLogger()
handler = logging.FileHandler(logfile)
handler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

