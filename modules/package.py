from mysql.connector import MySQLConnection
from modules.dependency import Dependency
from modules.compression import compress_text, decompress_text


# Class to store CRAN packet data
#
# Author: Daniel Alonso Báscones (@dnllns)
# Date: 2022-12-23
# Project: TFG OLIVIA

class Package:
    
    # Constructor
    def __init__(self, name):
  
        self.id = None
        self.name = name
        self.description = None
        self.version = None
        self.publication_date = None
        self.mantainer = None
        self.authors_data = None
        self.dependencies : list[Dependency] = []
        self.licenses = None
        self.requires_compilation = None
        self.in_cran = True
        self.in_bioc = None
        self.links = []

    # Makes a representation of the object in a readable form
    def __str__(self):
        return self.name + " " + self.version

    # Prints a representation of the object in stdout
    def dump(self):

        # Create chain with maintainers
        mantainers_str = self.mantainer

        # Create chain with dependencies
        dependencies_str = "\n".join(["  - " + str(dependencie) for dependencie in self.dependencies])

        # Create string with package information
        package_str = "Name: " + self.name + "\n\n"

        if self.description is not None:
            package_str += "Description:\n" + self.description + "\n\n"

        if self.version is not None:
            package_str += "Version: " + self.version + "\n\n"

        if self.publication_date is not None:
            package_str += "Publication date: " + str(self.publication_date) + "\n\n"

        package_str += "Mantainer: " + mantainers_str + "\n\n"

        if len(self.authors_data) > 0:
            package_str += "Authors:\n" + self.authors_data + "\n\n"

        if len(self.dependencies) > 0:
            package_str += "Dependencies:\n" + dependencies_str + "\n\n"

        if self.requires_compilation is not None:
            package_str += "Requires compilation:\t" + str(self.requires_compilation) + "\n\n"

        if self.in_cran is not None:
            package_str += "In CRAN: " + str(self.in_cran) + "\n\n"

        if self.in_bioc is not None:
            package_str += "In Bioconductor: " + str(self.in_bioc) + "\n\n"

        if len(self.licenses) > 0:
            package_str += "Licenses:\n" + self.licenses + "\n\n"

        if len(self.links) > 0:
            package_str += "Links:\n"
            for link in self.links:
                package_str += link + "\n"

    

        print(package_str)

    # Build the object from the information in the database
    def get_package(self, cnx: MySQLConnection):

        # Create cursor
        cursor = cnx.cursor(buffered=True)

        # Create query to get package information
        sql = 'SELECT * FROM packages WHERE name = %s'
        cursor.execute(sql, (self.name,))
        pkg = cursor.fetchone()

        try:

            # Get package information
            self.id = pkg[0]
            # self.name = pkg[1]
            self.description = decompress_text(pkg[2])
            self.version = pkg[3]
            self.publication_date = pkg[4]

            # requires_compilation is a boolean
            if pkg[5] == 1:
                self.requires_compilation = True
            else:
                self.requires_compilation = False
            
            # in cran is a boolean
            if pkg[6] == 1:
                self.in_cran = True
            else:
                self.in_cran = False

            # in bioconductor is a boolean
            if pkg[7] == 1:
                self.in_bioc = True
            else:
                self.in_bioc = False

            self.mantainer = pkg[8]
            self.authors_data = decompress_text(pkg[9])
            self.licenses = pkg[10]

            # Get the package dependencies
            self.__pkg_dependencies_db(cnx)

            # Get the package links
            self.__pkg_links_db(cnx)

            # Close connection to the database
            cursor.close()

        except:
            return False
            

        if pkg:
            return True
        else:
            return False

    
    # Save to database
    def save(self, cnx: MySQLConnection):
        '''
        Save the package to the database
        
        Parameters
        ----------
        cnx : MySQLConnection
            Connection to the database
            
        Returns
        -------

        '''

        try:

            # Establish connection to the database
            cursor = cnx.cursor(buffered=True)


            # Insert package information
            # -------------------------

            # Create SQL statement to insert the package into the table
            sql = 'INSERT INTO packages (name, description, version, publication_date, requires_compilation, in_cran, in_bioconductor, mantainer, author_data, license) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            values = (
                self.name, 
                compress_text(self.description), 
                self.version, 
                self.publication_date, 
                self.requires_compilation, 
                self.in_cran, 
                self.in_bioc, 
                self.mantainer, 
                compress_text(self.authors_data), 
                self.licenses
            )

            # Execute SQL statement
            cursor.execute(sql, values)

            # Get the id of the package
            self.id = cursor.lastrowid

            # Insert package links
            # --------------------

            sql = 'INSERT INTO links (url, package_id) VALUES (%s, %s)'     
            
            for link in self.links:
                values = (link, self.id)
                cursor.execute(sql, values)

                # get the id of the link
                link_id = cursor.lastrowid

                # Create SQL statement to insert in package_links table
                sql = 'INSERT INTO package_link (package_id, url_id) VALUES (%s, %s)'
                values = (self.id, link_id)

                # Execute SQL statement
                cursor.execute(sql, values)
                        
            # insert Dependencies
            # ------------------

            for dependency in self.dependencies:
                dependency.id_pkg = self.id
                dependency.save(cnx)

            # --        

            # Commit changes to the database and close connection
            cnx.commit()

            # Close connection to the database
            cursor.close()

            return True


        # Catch any exception
        except Exception as e:
            return False, e




    # Get package dependencies
    def __pkg_dependencies_db(self, cnx: MySQLConnection):

        # Establish connection to the database
        cursor = cnx.cursor()

        # Create SQL statement to get package dependencies
        sql = 'SELECT * FROM package_dependency WHERE package_id = %s'
        cursor.execute(sql, (self.id,))
        pkg_dependency_list = cursor.fetchall()

        # Obtener dependencias del paquete
        for dependency in pkg_dependency_list:

            # Get dependency id
            dependency_id = dependency[1]
            
            # Create SQL statement to get package dependencies from dependencies table
            sql = 'SELECT * FROM dependencies WHERE id = %s'
            cursor.execute(sql, (dependency_id,))
            dependency = cursor.fetchone()

            # Get dependency information
            id = dependency[0]
            name = dependency[1]
            version = dependency[2]
            type = dependency[3]

            # Create dependency object
            d = Dependency(name, type, self.id, id, version)

            # Add dependency to package
            self.dependencies.append(d)

    # Get package links
    def __pkg_links_db(self, cnx: MySQLConnection):
            
            # Establish connection to the database
            cursor = cnx.cursor()
    
            # Create SQL statement to get package links
            sql = 'SELECT * FROM package_link WHERE package_id = %s'
            cursor.execute(sql, (self.id,))
            pkg_link_list = cursor.fetchall()
    
            # Obtener links del paquete
            for link in pkg_link_list:

                # Get link id
                link_id = link[1]
    
                # Create SQL statement to get package links from links table
                sql = 'SELECT * FROM links WHERE id = %s'
                cursor.execute(sql, (link_id,))
                link = cursor.fetchone()
    
                # Get link information
                url = link[1]
  
                # Add link to package
                self.links.append(url)


    