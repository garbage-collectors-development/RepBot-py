import sqlite3
import pathlib
import logging

logger = logging.getLogger(__name__)

class Persistance:

    def __init__(self, db_file:pathlib.Path):

        if not isinstance(db_file, pathlib.Path):
            raise TypeError("db_file must be a Pathlib object")
        try:
            self._connection = sqlite3.connect(db_file.absolute())
            self._connection.row_factory = sqlite3.Row
        except Exception as e:
            logger.exception(e)
            raise
        else:
            self._cursor = self._connection.cursor()

        if len(tuple(table for table in self._get_tables() if table['name'] == 'users'))==0:
            self._create_table()

        # for row in self._get_tables():
        #     if not self.tableName == row['name']:
        #         self._create_table()

    def __execute_query(self, sql_statement:str, commit:bool=False):
        """Executes the provided statement against the database and commits 
        changes if prompted."""

        try:
            logger.debug('Execturing query {0}'.format(sql_statement))
            self._cursor.execute(sql_statement)
            if commit:
                logger.debug('Commiting changes')
                self._connection.commit()
        except:
            logger.exception('Error running the statement\n{0}'.format(
                sql_statement)
                )
            raise
        
    
    def _get_tables(self):
        """Returns a list of all tables in the databse"""
        
        sql_statement = "SELECT name FROM sqlite_master where type = 'table'"

        self.__execute_query(sql_statement)
        return self._cursor.fetchall()
    
    def _create_table(self):
        """Creates the table structure that will store the data for reputation"""

        sql_statement = """
        CREATE TABLE "users" (
            "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "d_id"	INTEGER UNIQUE,
            "d_name"	TEXT,
            "d_discriminator"	INTEGER,
            "rep"	INTEGER
            )"""
        
        self.__execute_query(sql_statement, True)

    def add_new_user(self, id:int,name:str, discriminator:str):
        """Adds a new user to the database"""

        sql_statement = """
        INSERT INTO 'users' 
            VALUES ({0}, '{1}', '{2}', 0)"""

        self.__execute_query(sql_statement,True)

    @property
    def users(self):
        

        sql_statement = """SELECT d_id, d_name, d_discriminator FROM 'users'"""

        self.__execute_query(sql_statement)
        results = self._cursor.fetchall()
        return {row['d_id']:'{0}#{1}'.format(row['d_name'], row['d_discriminator']) for row in results}





db_file = pathlib.Path('c:/temp/temp.db')
print(db_file.absolute())
db=Persistance(db_file.absolute())
print(db.users)

