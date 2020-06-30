'''
Created on May 29, 2018
@author: nicholasr
'''
import logging
logger = logging.getLogger(__name__)

class Column(object):
    '''
    Representation of a column from a PGDump file
    '''
    def __init__(self, statement: str):
        '''
        Constructor
        '''
        self.name = statement.split(' ')[0]
        self.not_nullable = 'NOT NULL' in statement
        self.statement = statement
        self.type = self.determine_type(statement.split(' ')[1])
        assert self.type is not None, \
            f"Column definition with unknown data type: {statement.split(' ')[1]}"
    def determine_type(self, type_statement: str):
        '''
        Convert a postgre type into a python type
        '''
        if 'character' in type_statement:
            return str
        elif 'int' in type_statement:
            return int
        elif 'numeric' in type_statement:
            return float
    def convert_from_string(self, value: str):
        '''
        Convert the value into the python equivalent of the column's data type
        '''
        if value == '\\N':
            return None
        elif self.type is str:
            col_def = self.statement
            col_length = int(col_def[col_def.find('(')+1:col_def.find(')')])
            return value[:col_length].strip()
        elif self.type is int:
            try:
                return int(value) if len(value) > 0 else None
            except ValueError:
                logger.info(f"Value in schema couldn't be converted to integer: {value}")
                raise
        elif self.type is float:
            try:
                if len(value.replace('.', '')) > 11:
                    logger.debug(f"Float value too large, setting to null: {value}")
                    return None
                return float(value)
            except ValueError:
                logger.info(f"Value in schema couldn't be converted to float: {value}")
                raise