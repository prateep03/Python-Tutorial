import logging
import time

# logging.basicConfig(filename='app.log', level=logging.DEBUG, filemode='w', format='%(name)s - %(levelname)s - %(message)s') # logging to file `app.log`
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S') # logging to console
logger = logging.getLogger('example_logger')

# logging.debug('This will get logged')
# logger.debug('This will get logged')

# name='John'
# age=3
# print('{name}, {age}'.format(name=name, age=age)) # kwargs
# print(f'{name}, {age}') # f-string, only works in python 3.6
# print('{0}, {1}'.format(name, age)) # args

def f(logger):
    a = 1
    logger.info('value of a is %d' % a)
    b = 3.142
    logger.info('value of a formatted {0:.5f}'.format(b))
    logger.warning('This is a warning')

f(logger)