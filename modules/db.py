import configparser
from colorama import Fore, Style
import mysql.connector

class DatabaseHandler:
    '''
    Class for connecting to the database
    
    This class implements the Singleton pattern so that only one instance of the class exists.
    
    Parameters:
    -----------
        user (str): Database username
        password (str): Database password
        host (str): Address of the database server
        database (str): Name of the database
        
    Attributes:
    ----------
        cnx (mysql.connector.connection.MySQLConnection): Database connection object
        
    Methods:
    --------
        __new__ (cls, *args, **kwargs): Method to create a new instance of the class
        __init__ (self, user, password, host, database): Method to initialize the class
        
    Author:
    ------
        Daniel Alonso Báscones (@dnllns)
    
    Date:
    ------
        2022-12-25
    
    Version:
    --------
        1.0
    '''
    
    # Attribute to store the single instance of the class
    _instance = None

    def __new__(cls, *args, **kwargs):
        '''
        Method to create a new instance of the class

        Parameters:
        -----------
            cls (DatabaseHandler): Class object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
        --------
            DatabaseHandler: Single instance of the class
        '''

        # If an instance of the class already exists, that instance is returned
        if cls._instance is None:
            # If no instance exists, a new one is created and stored in the _instance attribute
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        '''
        Method to initialize the class

        Parameters:
        -----------
            user (str): Database username
            password (str): Database password
            host (str): Address of the database server
            database (str): Name of the database
        '''

        # Configure the database connection
        # ---------------------------------

        # Read configuration file
        config = configparser.ConfigParser()

        # Get the values ​​from the configuration file
        try:
            config.read('./config/db/config.ini')
            mysql_config = config['mysql']

        except Exception as e:

            print(Fore.RED)
            print("Exception in class DatabaseHandler, method __init__")
            print("Error: The database configuration file could not be read")
            print("Error: ", e)
            print(Style.RESET_ALL)
            exit(1)

        # Configure the connection to the database
        try:
            self.cnx = mysql.connector.connect(
                user=mysql_config['user'],
                password=mysql_config['password'],
                host=mysql_config['host'],
                database=mysql_config['database']
            )
        
        except Exception as e:
                
                print(Fore.RED)
                print("Exception in class DatabaseHandler, method __init__")
                print("Error: The database connection could not be established")
                print("Error: ", e)
                print(Style.RESET_ALL)
                exit(1)
        

    def get_connection(self):
        '''
        Method to get the connection to the database
        '''

        # Return the connection to the database
        return self.cnx

    def close_connection(self):
        '''
        Method to close the connection to the database
        '''

        # Close the connection to the database
        self.cnx.close()    

    def execute_query(self, query: str, params: tuple = None) -> list[tuple]:
        '''
        Method to execute a query in the database

        Parameters:
        -----------
            query (str): Query to be executed
            params (tuple): Parameters of the query

        Returns:
        --------
            list[tuple]: List of tuples with the result of the query
        '''

        # Create a cursor to execute the query
        cursor = self.cnx.cursor()

        # Execute the query
        cursor.execute(query, params)

        # Get the result of the query
        result = cursor.fetchall()

        # Close the cursor
        cursor.close()

        # Return the result of the query
        return result