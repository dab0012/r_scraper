from mysql.connector import MySQLConnection

# Class that represents a dependency of a package.
# 
# author: Daniel Alonso Báscones (@dnllns)
# date: 2022-12-23
# project: TFG OLIVIA

class Dependency:
    '''
    Class that represents a dependency of a package.

    attributes
    ---------
    id : int
        Identifier of the dependency in the database.
        
    pkg_id : int
        Identifier of the package to which the dependency belongs.
    
    name : str
        Dependency name.

    type : str
        Dependency type (IMPORT or DEPENDS).
    
    version : str
        Dependency version.

    methods
    -------
    __init__(self, name, type, id_pkg, version=None)
        Initializes an object of type Dependency.

    __str__(self)
        String representation of the Dependency class.

    save_in_db(self, cnx: MySQLConnection)
        Save the dependency in the database.

    build_object(self, cnx: MySQLConnection)
        Constructs an object of type Dependency from the information in the database.

    dump(self)
        String representation of the Dependency class.

    '''

    # Class constructor
    def __init__(self, name, type, id_pkg=None, id=None, version=None):

        self.id = id
        self.id_pkg = id_pkg
        self.name = name
        self.type = type
        self.version = version

    # String representation of the Dependency class
    def __str__(self):

        # If the dependency has a version, return the name and version
        if self.version:
            return  self.name + " (" + str(self.version) + ")" + " type: " + self.type
        # If the dependency does not have a version, return the name
        else:
            return self.name + ", type: " + self.type

    # function to save the dependency in the database
    def save(self, cnx: MySQLConnection):


        # Create SQL query to insert the dependency into the dependency table
        insert_query = '''
            INSERT INTO dependencies (name, version, type)
            VALUES (%s, %s, %s)
        '''

        # Establish connection to the database
        cursor = cnx.cursor(buffered=True)

        # Check if the dependency already exists in the database
        sql = 'SELECT * FROM dependencies WHERE name = %s AND version = %s AND type = %s'
        cursor.execute(sql, (self.name, self.version, self.type))
        dependency = cursor.fetchone()

        # If the dependency already exists, get its identifier
        if dependency:
            self.id = dependency[0]
        # If the dependency does not exist, insert it into the database
        else:

            # Execute query to insert dependency
            cursor.execute(insert_query, (self.name, self.version, self.type))
            
            # Get the identifier of the newly inserted dependency
            self.id = cursor.lastrowid  


        # Create SQL query to insert the relationship into the package_dependency table
        insert_query = '''
            INSERT INTO package_dependency (package_id, dependency_id)
            VALUES (%s, %s)
        '''

        # Execute query to insert the relationship
        cursor.execute(insert_query, (self.id_pkg, self.id))

        # Commit changes to the database
        cnx.commit()

        # Close connection to the database
        cursor.close()

    # # function to build an object of type Dependency from the information in the database
    # def build_object(self, cnx: MySQLConnection):
    #     '''
    #     Build an object of type Dependency from the information in the database.

    #     parameters
    #     ----------
    #     cnx : MySQLConnection
    #         Connection with the database.
    #     '''

    #     # Establish connection to the database
    #     cursor = cnx.cursor()

    #     sql = '''
    #         SELECT * FROM dependencies    
    #         WHERE name = %s
    #     '''
    #     cursor.execute(sql, (self.name,))
    #     dependency = cursor.fetchone()  

    #     # Get dependency information
    #     self.id = dependency[0]
    #     self.name = dependency[1]
    #     self.version = dependency[3]
    #     self.type = dependency[4]

    #     # Close connection to the database
    #     cursor.close()

    # function to print the data of the Dependency class
    def dump(self):
        '''
        String representation of the Dependency class.
        '''

        return f'{self.type}:{self.name}_v({self.version})'