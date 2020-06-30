import mysql.connector
from mysql.connector import MySQLConnection, Error

from configparser import ConfigParser

# Connect to db using hard coded parameters
def connect():
    try:
        conn = mysql.connector.connect(host='localhost',
                                       database='python_mysql',
                                       user='prateepm',
                                       passwd='Tcw@1234')
        print(type(conn))
        if conn.is_connected():
            print('Connected to MySQL database')
    except Error as e:
        print(e)
    finally:
        conn.close()


# if __name__ == "__main__":
#     connect()


def read_db_config(filename='mysql_config.ini', section='mysql'):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db

# connect to db from a configuration file
def connect_from_config():

    # read from a configuration file('mysql_config.ini')
    db_config = read_db_config()

    try:
        print('Connecting to MySQL database...')
        conn = mysql.connector.MySQLConnection(**db_config)

        if conn.is_connected():
            print('connection is established')
        else:
            print('connection failed.')
        conn.close()
    except Error as e:
        print(e)


# insert a book in db. Columns to add are (id, title, isbn)
def insert_book(id, title, isbn):

    query = "insert into books (id, title, isbn) values (%s, %s, %s)"
    # query = "delete from books where id=(%s)"
    # def query(id, title, isbn):
    #    execute 'insert ...'

    args = (id, title, isbn) # tuple of values

    try:
        db_config = read_db_config() # dictionary of db config values

        conn = MySQLConnection(**db_config)

        cursor = conn.cursor() # reference to query results
        cursor.execute(query, args) # execute one query at a time

        conn.commit()
    except Error as e:
        print(e)
    finally: # executed always
        conn.close()

def insert_books(books): # books is list of tuple (id, title, isbn)

    query = "insert into books (id, title, isbn) "  \
            "values (%s, %s, %s)"

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.executemany(query, books)

        conn.commit()
    except Error as e:
        print(e)
    finally:
        conn.close()


def query_with_fetchall(): # returns all the results in one time

    query = "select * from books where title like 'The Alchemist%'"

    try:
        db_config = read_db_config()

        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        res = cursor.execute(query)
        print(res)

        rows = cursor.fetchall() # list of all results in db

        print('Total rows {}'.format(cursor.rowcount))
        for row in rows:
            print(row)


    except Error as e:
        print(e)
    finally:
        conn.close()

def query_with_fetchone(): # generator, returning one row at a time

    query = "select * from books"

    try:
        db_config = read_db_config()

        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(query)
        # print(res)

        rows = cursor.fetchone() # generator returning a single row
        print('Total rows {}'.format(cursor.rowcount))

        while rows is not None:
            print(rows[0], rows[1], rows[2])
            rows = cursor.fetchone()

    except Error as e:
        print(e)
    finally:
        conn.close()

# generator to return results of length = size
def iter_row(cursor, size=10):
    while True:
        rows = cursor.fetchmany(size) # returns a boolean
        if not rows:
            break
        # for row in rows:
        yield rows


def query_with_fetchmany():  # return specified size of results

    query = "select * from books"

    try:
        db_config = read_db_config()

        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(query)

        for row in iter_row(cursor, size=2):
            print(row)
            print('----------')

    except Error as e:
        print(e)
    finally:
        conn.close()


if __name__ == '__main__':
    # connect()
    # connect_from_config()
    # insert_book('2', 'Harry Potter And The Order Of The Phoenix', '9780439358071')
    # books = []
    # for book in books:
    #     # book = (id, title, isbn) -> read from csv file (using pandas.read_csv(filename))
    #     books.append(book)
    # insert_books(books)
    #
    # insert_books([('5', 'Gone with the Wind', '9780446675536'),
    #               ('6', 'Pride and Prejudice (Modern Library Classics)', '9780679783268')])

    # query_with_fetchone()
    # query_with_fetchall()
    query_with_fetchmany()

# import mysql.connector as connector
#
# conn = connector.connect(host="localhost",
#                          user="prateepm", passwd="Tcw@1234",
#                          database="student_db")
#
# cursor = conn.cursor()
# # cursor.execute("insert into student(name, college) values('john','uic');")
# # conn.commit()
# # conn.close()
#
# cursor.execute("delete from student where name='john'")
# conn.commit()
# conn.close()

# mycursor = mydb.cursor()
# mycursor.execute("show databases")
#
# result = mycursor.fetchone()
#
# for db in result:
#     print(db)
