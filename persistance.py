import sqlite3
import pathlib
import logging
import datetime
from collections import namedtuple

import discord 


logger = logging.getLogger(__name__)

class Persistance:

    member_rep = namedtuple('MemberRep', ['member','rep'])
    DATE_FORMAT = '%m/%d/%Y %H:%M:%S.%f'

    def __init__(self, db_file:pathlib.Path, guild:discord.Guild=None):

        self.guild = guild

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
            "rep"	INTEGER,
            "last_used" TEXT
            )"""
        
        self.__execute_query(sql_statement, True)

    def add_new_user(self, member:discord.Member):
        """Adds a new user to the database"""

        sql_statement = """
        INSERT INTO users(d_id,d_name,d_discriminator,rep,last_used)
            VALUES ({0}, '{1}', '{2}', 0, '{3}')""".format(
                member.id,
                member.name,
                member.discriminator,
                (datetime.datetime.now() - datetime.timedelta(minutes = 12)).strftime(self.DATE_FORMAT)
            )

        self.__execute_query(sql_statement,True)

    @property
    def users(self):
        """retrieves a dictionary of all users in the database"""

        sql_statement = """SELECT d_id, d_name, d_discriminator FROM 'users'"""

        self.__execute_query(sql_statement)
        results = self._cursor.fetchall()
        #return [{row['d_id']:'{0}#{1}'.format(row['d_name'], row['d_discriminator'])} for row in results]
        return tuple(self.guild.get_member(row['d_id']) for row in results)

    def get_users_by_rep(self):
        """returns a list of all users by rep whose rep is not 0"""

        sql_statement = "SELECT d_id, rep FROM 'users' WHERE rep > 0 ORDER BY rep DESC"

        self.__execute_query(sql_statement)
        results = self._cursor.fetchall()
        return {index:self.member_rep(self.guild.get_member(row['d_id']),row['rep']) for index, row in enumerate(results,1)}

    def add_rep(self, users:list):
        """Adds rep to the called users and adds a time stamp to the requestor"""

        sql_statement = """UPDATE users SET rep = rep + 1 WHERE users.d_id = {0}"""
        try:
            for user in users:
                self.__execute_query(sql_statement.format(user.id), True)

            return True
        except:
            logger.exception("Error committing job")
            return False
        
    def set_rep(self, member:discord.Member, rep:int):
        """Manually sets the rep for a user"""

        sql_statement = "UPDATE users SET rep = {0} where users.d_id = {1}".format(rep, member.id)

        try:
            self.__execute_query(sql_statement, True)

            return True
        except:
            return False

    def get_rep(self, member:discord.Member):
        """Gets the current rep for a user"""

        sql_statement = "SELECT rep FROM users WHERE users.d_id = {0}".format(member.id)

        self.__execute_query(sql_statement)

        result = self._cursor.fetchone()
        return result['rep']

    def get_last_used(self, member:discord.Member):
        """Gets the 'last_used' filed value as a datetime object"""

        sql_statement = """SELECT last_used FROM users WHERE users.d_id = {0}""".format(
            member.id
        )

        self.__execute_query(sql_statement)

        result = self._cursor.fetchone()
        return datetime.datetime.strptime(result['last_used'],self.DATE_FORMAT)


    def set_last_used(self, member:discord.Member):
        """Set the 'last_used' field with the current datetime"""

        sql_statement = """UPDATE users SET last_used = '{0}' WHERE users.d_id = {1}""".format(
            datetime.datetime.now().strftime(self.DATE_FORMAT),
            member.id
        )

        self.__execute_query(sql_statement, True)




if __name__ == '__main__':
    db_file = pathlib.Path('c:/temp/temp.db')
    print(db_file.absolute())
    db=Persistance(db_file.absolute())
    print(db.users)
