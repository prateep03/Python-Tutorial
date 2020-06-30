# Utility Functions (sourceManager)
# Documentation at https://bitbucket.zgtools.net/projects/CDA/repos/sourcemanager/browse
# Created by Anna Liu (annali@zillowgroup.com)
import os
import sys
import re
import subprocess
import yaml
import turbodbc
import pyodbc
import math
import string
import csv
import errno
from itertools import islice

config_folder = r"\\IRV-WIN-FIL-001\Data Services Assessment Team\Python Tools\config"

# ======================================================================================================================
# General Utility Functions
# ======================================================================================================================
def is_number(s):
    """check if an object is number"""
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

def search_county_names(fips_codes):
    """Return a list of dictionaries of fips and county names found"""
    if isinstance(fips_codes, list):
        fips_list_path = resource_path(r"resources\FIPS Codes.txt")
        with open(fips_list_path) as f:
            fips_list = f.readlines()
        fips_list = [record.strip().replace('"', '').split(',') for record in fips_list]
        valid_fips = []
        invalid_fips = []
        for code in fips_codes:
            found = False
            for fips in fips_list:
                if fips[2] == code:
                    valid_fips.append(dict(zip(['County', 'State', 'FIPS'], fips)))
                    found = True
                    break
            if not found:
                invalid_fips.append(code)
        return valid_fips, invalid_fips

def is_valid_fips(code):
    """Check if the code is a valid FIPS code"""
    code = str(code)
    if is_number(code) and len(code) == 5:
        fips_list_path = resource_path(r"resources\FIPS Codes.txt")
        with open(fips_list_path) as f:
            fips_list = f.readlines()
        fips_list = [record.strip().replace('"', '').split(',')[-1] for record in fips_list]
        if code[-3:] == '000':
            valid_fips = [fips for fips in fips_list if fips[:2] == code[:2]]
        else:
            valid_fips = [fips for fips in fips_list if fips == code]
        if len(valid_fips) > 0:
            return True
        else:
            return False
    else:
        return False

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def extract_query(path):
    """Extract sql query from text file"""
    file_path = resource_path(path)
    with open(file_path, 'r') as f:
        lines = f.readlines()
    query = " ".join([line.strip('\n') for line in lines])
    return query

def find_mapped_drive(remote_drive):
    remote_drive = remote_drive.lower()
    user = os.environ["USERNAME"]
    p = subprocess.check_output(["net", "use"], cwd=os.path.join(r"C:\Users", user), shell=True,
                                **subprocess_args(False))
    data = p.decode("utf-8").split('\n')
    data = [line.strip().lower() for line in data]
    mapped_drives = [re.sub(r'\s{2,}', '|', line) for line in data
                     if " "+remote_drive+" " in line or line.endswith(remote_drive)]
    if len(mapped_drives) > 0:
        return mapped_drives[0].split('|')[1]

def map_network_drive(remote_drive):
    user = os.environ["USERNAME"]
    subprocess.Popen(["net", "use", "*", remote_drive, "/persistent:yes"],
                     cwd=os.path.join(r"C:\Users", user), shell=True, **subprocess_args(False))

def subprocess_args(include_stdout=True):
    # The following is true only on Windows.
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        env = os.environ
    else:
        si = None
        env = None
    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}
    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env})
    return ret

def get_rds_credential():
    rds_cred_path = os.path.join(config_folder, "credentials.yaml")
    with open(rds_cred_path, 'r') as cred_file:
        accounts = yaml.load(cred_file)
    return accounts['rds']['sqlserver']['host'], accounts['rds']['sqlserver']['username'], accounts['rds']['sqlserver']['password']

def convert_csv_file(file_import_path, file_export_path, new_delimiter):
    """Convert csv file to a delimiter-separated file"""
    with open(file_import_path, 'r') as fin:
        reader = csv.reader(fin)
        with open(file_export_path, 'w') as fout:
            writer = csv.writer(fout, delimiter=new_delimiter)
            writer.writerows(reader)

def check_desktop_setup():
    """Run before ICR process to create necessary folders if not exist"""
    folders = ["ICR - Completed", "ICR - Currently Working", "ICR - Move to Network", "ICR - On Hold Acquisition"]
    user = os.environ["USERNAME"]  # getpass.getuser()
    desktop_path = r"C:\Users\{0}\Desktop".format(user)
    for folder in folders:
        folder_path = os.path.join(desktop_path, folder)
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            try:
                os.makedirs(folder_path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

def is_standardized(file_path):
    """Return False on if any of the following conditions meet, otherwise return True
        1) the file is not standardized by Standardizer
        2) the file is empty
        3) the file has only headers
        4) the file has more than 1024 columns
    """
    if file_path.endswith('.csv') and os.path.exists(file_path):
        with open(file_path, 'r') as f:
            first_two_lines = [x.strip() for x in islice(f, 2)]
        try:
            first_line = first_two_lines[0]
            second_line = first_two_lines[1]
        except IndexError:
            return False
        a = first_line.split(',')
        b = first_line.split('","')
        c = second_line.split('","')
        if first_line[0] != '"' or first_line[-1] != '"' or len(a) != len(b) or len(b) > 1024:
            return False
        elif len(c) != len(b):
            return False
        else:
            return True
    else:
        return False

# ======================================================================================================================
# SQL Utility Functions
# ======================================================================================================================
def connect_to_sql_server(server, dbname, username=None, password=None, quiet_mode=False, driver='turbodbc'):
    """Connect to MSSQL Server"""
    if not quiet_mode:
        print("")
        print("Establishing Database Connection ... ")
        print("... SQL Server: {0}".format(server))
        print("... Database: {0}".format(dbname))
    if username is None and password is None:
        connection_string = "Driver={{SQL Server}};" \
                            "Server={0};" \
                            "Port:1433;" \
                            "database={1};" \
                            "trusted_connection = 'yes';" \
                            "Encrypt='yes';".format(server, dbname)
    else:
        connection_string = "Driver={{SQL Server}};" \
                            "Server={0};" \
                            "Port:1433;" \
                            "database={1};" \
                            "uid={2};" \
                            "pwd={3};" \
                            "Encrypt='yes';".format(server, dbname, username, password)
    try:
        if driver == 'pyodbc':
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            cursor.fast_executemany = True
            if not quiet_mode:
                print("... Successful Connection!")
            return cursor
        else:
            options = turbodbc.make_options(prefer_unicode=True,
                                            parameter_sets_to_buffer=100000,
                                            limit_varchar_results_to_max=True,
                                            varchar_max_character_limit=8000)
            conn = turbodbc.connect(connection_string=connection_string, turbodbc_options=options)
            if not quiet_mode:
                print("... Successful Connection!")
            return conn
    except:
        print("... Failed Connection!")
        return 0

def create_sql_schema(cursor, dbname, schema_name):
    """
    Create schema if not exists
    :param cursor:
    :param dbname:
    :param schema_name:
    :return:
    """
    cursor.execute('use {0};'.format(dbname))
    query = "IF NOT EXISTS (SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{0}' ) " \
            "BEGIN EXEC sp_executesql N'CREATE SCHEMA {0}'END".format(schema_name)
    cursor.execute(query)

def drop_sql_table(cursor, dbname, schema, table):
    """Drop a sql table if exists"""
    cursor.execute('use {0};'.format(dbname))
    query = "IF EXISTS (select * from information_schema.tables where TABLE_CATALOG = '{0}' and TABLE_SCHEMA = '{1}' " \
            "and TABLE_NAME = '{2}') drop table [{0}].[{1}].[{2}]".format(dbname, schema, table)
    cursor.execute(query)
    print("... Table {0}.{1}.{2} dropped!".format(dbname, schema, table))

def check_if_schema_exists(cursor, dbname, schema_name):
    """Check if the schema exists in the database"""
    cursor.execute('use {0};'.format(dbname))
    query = "SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{0}'".format(schema_name)
    cursor.execute(query)
    if len(cursor.fetchall()) > 0:
        return True
    return False

def check_if_table_exists(cursor, dbname, schema_name, table_name):
    """Check if the table exists in the database and schema"""
    cursor.execute('use {0};'.format(dbname))
    query = "select * from information_schema.tables where TABLE_CATALOG = '{0}' and TABLE_SCHEMA = '{1}' " \
            "and TABLE_NAME = '{2}'".format(dbname, schema_name, table_name)
    cursor.execute(query)
    if len(cursor.fetchall()) > 0:
        return True
    return False

def list_all_tables(cursor, dbname, schema):
    """list all table names in the database and schema"""
    cursor.execute('use {0};'.format(dbname))
    cursor.execute(
        "select table_name from information_schema.tables where table_schema='{0}';".format(schema))
    all_tables = cursor.fetchall()
    return all_tables

def list_all_columns(cursor, dbname, schema, table, db_login=None):
    """list all table names in the database and schema"""
    one_time_conn = False
    if cursor is None:
        conn = connect_to_sql_server(**db_login, quiet_mode=True)
        cursor = conn.cursor()
        one_time_conn = True
    cursor.execute('use {0};'.format(dbname))
    cursor.execute(
        "select ordinal_position, column_name from information_schema.columns "
        "where table_schema='{0}' and table_name='{1}';".format(schema, table))
    all_columns = cursor.fetchall()
    if one_time_conn:
        conn.close()
    return all_columns

def clean_sql_schema(cursor, dbname, schema):
    """Drop all tables in the schema"""
    print("Cleaning the schema: {0}".format(schema))
    all_tables = list_all_tables(cursor, dbname, schema)
    print("Total {0} tables to be dropped.".format(len(all_tables)))
    for table in all_tables:
        table_name = table[0]
        drop_sql_table(cursor, dbname, schema, table_name)

def clean_file_name(file_name):
    """Prepare a sql table name"""
    print("Cleaning the file name")
    # Because SQL tables can't start with spaces or special characters,
    # we might need to change the name slightly.  These replace statements will do that.
    load_file_first_char = file_name[:1]
    # Drop file extension
    file_name = "_".join(file_name.lower().split(".")[:-1])
    # Certain characters aren't allowed in table names- these are the characters not allowed
    file_name = file_name.replace('values', '_values')
    file_name = file_name.replace(' ', '_')
    # Replace punctuations in a string with underscore(_)
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    file_name = regex.sub('_', file_name)
    # DB table names cannot start with numbers- so this checks to see if the first digit
    # is a number, if it is then it will append a '_' to the front
    if load_file_first_char in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
        file_name = '_' + file_name
    return file_name

def clean_column_name(column_name):
    """Prepare a sql table column name"""
    column_name = column_name.replace('"', '')  # double quote
    column_name = column_name.replace(' ', '_')  # space
    column_name = column_name.replace('\t', '_')  # tab
    column_name = column_name.replace('<', 'ls_than_')
    column_name = column_name.replace('>', 'gr_than_')
    column_name = column_name.lower().replace('exists', '_exists_')
    # Replace punctuations in a string with underscore(_)
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    column_name = regex.sub('_', column_name)
    # Checks to see if the first character in the first column is a number.  If it is, a '_' is appended before hand
    base_col_first_character = column_name[:1]
    table_filler = '_'
    if base_col_first_character in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
        column_name = table_filler + column_name
    return column_name

def create_sql_table(cursor, dbname, schema, table, file_path=None, columns=[]):
    """Create a sql table using the layout of a data file or specified column names"""
    print("Creating table: {0}.{1}.{2}".format(dbname, schema, table))
    if file_path is not None and os.path.exists(file_path) and file_path.endswith('.csv'):
        h = open(file_path, 'r')
        header_line = h.readline()
        h.close()
        header_line = header_line.strip()
        split_columns = header_line.split(',')
        colnames = ','.join(["\"{0}\" varchar(8000) null".format(clean_column_name(column)) for column in split_columns])
        query = "create table {0}.{1}.{2} ({3});".format(dbname, schema, table, colnames)
        cursor.execute(query)
    elif len(columns) > 0:
        colnames = ','.join(["\"{0}\" varchar(8000) null".format(clean_column_name(column)) for column in columns])
        query = "create table {0}.{1}.{2} ({3});".format(dbname, schema, table, colnames)
        cursor.execute(query)

def insert_to_sql_table(cursor, dbname, schema, table, source_file=None, records=[], driver='turbodbc'):
    """insert to sql table using data from a source file or a list of data points (single row)"""
    if source_file is not None and os.path.exists(source_file) and source_file.endswith('.csv'):
        print("... Loading data to {0}.{1}.{2}".format(dbname, schema, table))
        cursor.execute('use {0}'.format(dbname))
        with open(source_file, 'r', encoding="utf8") as f:
            source_data = f.read()
        source_data = source_data[1:-2].split('"\n"')  # skip the first " and last "\n
        source_data = [[x[:8000] for x in tuple(row.strip().split('","'))] for row in source_data]
        num_headers = len(source_data[0])
        sql_statement = "insert into {0}.{1}.{2} values (".format(dbname, schema, table) + ','.join(
            ["?"] * num_headers) + ");"
        source_data = source_data[1:]
        if driver == 'pyodbc':
            chunksize = 10000
            cursor.fast_executemany = True
            num_chunk = int(math.ceil(len(source_data) / chunksize))
            for i in range(num_chunk):
                start = chunksize * i
                end = chunksize * (i + 1)
                chunk_data = source_data[start:end]
                cursor.executemany(sql_statement, chunk_data)
        else:
            cursor.executemany(sql_statement, source_data)
    elif len(records) > 0 and (isinstance(records[0], list) or isinstance(records[0], tuple)):
        cursor.execute('use {0}'.format(dbname))
        chunk_limit = 1000
        num_chunks = int(math.ceil(len(records) / chunk_limit))
        for i in range(num_chunks):
            start_index = chunk_limit * i
            end_index = chunk_limit * (i+1)
            values = ",".join(["('{0}')".format("','".join([i[:8000] for i in v]))
                               for v in records[start_index:end_index]])
            query = "insert into {0}.{1}.{2} values {3};".format(dbname, schema, table, values)
            cursor.execute(query)
    elif len(records) > 0:
        cursor.execute('use {0}'.format(dbname))
        values = ",".join(["'{0}'".format(v[:8000]) for v in records])
        query = "insert into {0}.{1}.{2} values ({3})".format(dbname, schema, table, values)
        cursor.execute(query)

def file_upload_worker(args, failed_files):
    """A helper function to upload files"""
    # get arguments
    file = args['file']
    source_folder = args['source_folder']
    dbname = args['dbname']
    schema = args['schema']
    mode = args['mode']
    db_login = args['login']
    print("Working on source file: {0}".format(file))
    original_file_path = os.path.join(source_folder, file)
    table_name = clean_file_name(file)
    try:
        conn = connect_to_sql_server(**db_login)
        cursor = conn.cursor()
        table_exists = check_if_table_exists(cursor=cursor, dbname=dbname, schema_name=schema, table_name=table_name)
        if table_exists and mode == 'keep':
            return
        elif table_exists:
            drop_sql_table(cursor=cursor, dbname=dbname, schema=schema, table=table_name)
        create_sql_table(cursor, dbname, schema, table_name, original_file_path)
        conn.commit()
        print("... Finish creating table {0}".format(table_name))
        try:
            insert_to_sql_table(cursor, dbname, schema, table_name, original_file_path)
            conn.commit()
            conn.close()
        except turbodbc.exceptions.DatabaseError:
            conn.close()
            cursor = connect_to_sql_server(**db_login, driver='pyodbc')
            insert_to_sql_table(cursor, dbname, schema, table_name, original_file_path, driver='pyodbc')
            cursor.commit()
            cursor.close()
    except Exception:
        failed_files.append(file)

def summarize_schema(cursor, dbname, schema):
    """Summarize table layout in a schema"""
    cursor.execute('use {0};'.format(dbname))
    cursor.execute(
        "select table_name from information_schema.tables where table_schema='{0}'".format(schema))
    all_tables = cursor.fetchall()
    print("Total {0} tables in the schema {1}".format(len(all_tables), schema))
    result = []
    for table in all_tables:
        table_name = table[0]
        query = "select count(*) from {0}.{1}.{2}".format(dbname, schema, table_name)
        cursor.execute(query)
        nrows = cursor.fetchone()[0]
        query2 = "SELECT COLUMN_NAME FROM {0}.INFORMATION_SCHEMA.COLUMNS " \
                 "WHERE TABLE_SCHEMA='{1}' and TABLE_NAME = '{2}'".format(dbname, schema, table_name)
        cursor.execute(query2)
        col_result = cursor.fetchall()
        ncols = len(col_result)
        column_names = ",".join([v[0] for v in col_result])
        result.append((str(table_name), str(nrows), str(ncols), str(column_names)))
    return result

def get_table_names(cursor, dbname, schema):
    """Return a list of tables in the schema"""
    sql_query = "select TABLE_SCHEMA, TABLE_NAME from {0}.information_schema.tables " \
                "where TABLE_SCHEMA in ({1});".format(dbname, schema)
    cursor.execute(sql_query)
    return cursor.fetchall()

def copy_sql_table(cursor, dbname_from, schema_from, old_table, dbname_to, schema_to, new_table):
    """Copy sql table from one location to another in the SQL Server"""
    drop_sql_table(cursor, dbname_to, schema_to, new_table)
    sql_query = "select * into [{0}].[{1}].[{2}] from [{3}].[{4}].[{5}];".format(dbname_to, schema_to, new_table,
                                                                                 dbname_from, schema_from, old_table)
    cursor.execute(sql_query)

def create_apn_format_table(cursor, dbname, schema_name, fips_codes_list):
    """Create APN Formats table"""
    table_name = "_APNFormats"
    fips = ",".join(["'{0}'".format(code) for code in fips_codes_list])
    sql_query = "select * into [{1}].[{2}].[{3}] from Tableau.dbo.APNformats " \
                "where FIPS in ({0})".format(fips,dbname, schema_name, table_name)
    cursor.execute(sql_query)
    print("... Created {0}".format(table_name))

def create_land_use_lookup(cursor, dbname, schema_name, fips_codes_list, statewide=False):
    """Create Land Use Lookup table"""
    table_name = "_LandUseLookup"
    fips = ",".join(["'{0}'".format(code) for code in fips_codes_list])
    if statewide:
        sql_query = extract_query(r"resources\Land Use Lookup Statewide.txt").format(fips, dbname, schema_name, table_name)
    else:
        sql_query = "select * into [{1}].[{2}].[{3}] from Tableau.dbo.ZasmtLandUseReference " \
                    "where FIPS in ({0})".format(fips, dbname, schema_name, table_name)
    cursor.execute(sql_query)
    print("... Created {0}".format(table_name))

def create_other_lookups(cursor, dbname, schema_name, fips_codes_list, statewide=False):
    """Create Other Lookups table"""
    table_name = "_OtherLookups"
    fips = ",".join(["'{0}'".format(code) for code in fips_codes_list])
    if statewide:
        sql_query = extract_query(r"resources\Other Lookups Statewide.txt").format(fips, dbname, schema_name, table_name)
    else:
        sql_query = "select * into [{1}].[{2}].[{3}] from Tableau.dbo.ZasmtStandardCodes " \
                    "where FIPS in ({0}) and CodeType like '%stndcode%'".format(fips, dbname, schema_name, table_name)
    cursor.execute(sql_query)
    print("... Created {0}".format(table_name))

def create_all_lookups(cursor, dbname, schema_name, fips_codes_list, statewide=False):
    """Create APN Formats, Land Use, Other Lookups"""
    create_apn_format_table(cursor, dbname, schema_name, fips_codes_list)
    create_land_use_lookup(cursor, dbname, schema_name, fips_codes_list, statewide)
    create_other_lookups(cursor, dbname, schema_name, fips_codes_list, statewide)