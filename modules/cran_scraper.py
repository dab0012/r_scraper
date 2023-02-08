import re
from bs4 import BeautifulSoup
from modules.package import Package
from modules.proxy_request import RequestHandler
from modules.dependency import Dependency

# Class to obtain CRAN packet data
#
# Usage example:
# request_handler = RequestHandler()
# package_scraper = PackageScraper(request_handler)
# package_data = package_scraper.get_pkg_data('ggplot2')
#
# Author: Daniel Alonso Báscones (@dnllns)
# Date: 2022-12-23
# Project: TFG OLIVIA

class PackageScraper:
    '''
    Class to obtain CRAN packet data

    methods:
    --------
    __init__(self, request_handler)
        class constructor   

    __parse_pkg_data(self, pkg_name)
        Get data from a CRAN packet

    __parse_dependencies(self, dependencies_str)
        Parse dependencies string

    get_pkg_data(self, pkg_name)
        Get data from a CRAN packet

    get_pkg_dependencies(self, pkg_name)
        Get dependencies from a CRAN packet

    get_pkg_imports(self, pkg_name)
        Get imports from a CRAN packet

    '''

    # Class constructor
    def __init__(self, request_handler: RequestHandler) -> None:
        '''
        class constructor

        args:
        -----
            request_handler (RequestHandler): Object of class RequestHandler

        '''
        self.request_handler = request_handler

    # Get data from a CRAN packet
    def __parse_pkg_data(self, pkg_name) -> dict[str, str]:
        '''
        Get data from a CRAN packet

        args:
        -----
            package_name (str): Package name

        Returns:
        --------
            dict: Dictionary with the package data

        '''

        # Initialize variables to None
        name = None
        description = None
        version = None
        publication_date = None
        author = None
        mantainer = None
        license = None
        requires_compilation = None
        depends = None
        imports = None

        # Make HTTP request to package page
        url = f'https://cran.r-project.org/package={pkg_name}'

        # Get response content of the page
        response = self.request_handler.do_request(url)

        # Parsear HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        
        # Get elements of interest from HTML
        name = soup.title.text.split(':')[0]
        description = soup.find('p').text.strip()
        description = description.replace('\n', '')
        description = description.replace('\t', '')
        description = description.replace('   ', '')

        # Get optional table data
        td_version = soup.find('td', text='Version:')
        if td_version:
            version = td_version.find_next_sibling('td').text.strip()
            version = version.replace('\n', '')

        td_date = soup.find('td', text='Published:')
        if td_date:
            publication_date = td_date.find_next_sibling('td').text.strip()

        td_author = soup.find('td', text='Author:')
        if td_author:
            author = td_author.find_next_sibling('td').text.strip()

        td_mantainer = soup.find('td', text='Maintainer:')
        if td_mantainer:
            mantainer = td_mantainer.find_next_sibling('td').text.strip()
            mantainer = mantainer.replace(' at ', '@')

        td_license = soup.find('td', text='License:')
        if td_license:
            license = td_license.find_next_sibling('td').text.strip()

        td_compilation = soup.find('td', text='NeedsCompilation:')
        if td_compilation:
            requires_compilation = td_compilation.find_next_sibling('td').text.strip()

        td_depends = soup.find('td', text='Depends:')
        if td_depends:
            depends = td_depends.find_next_sibling('td').text.strip()
            depends = depends.replace('\n', '')

        td_imports = soup.find('td', text='Imports:')
        if td_imports:
            imports = td_imports.find_next_sibling('td').text.strip()
            imports = imports.replace('\n', '')

        # Build dictionary with package data
        return {
            'name': name,
            'description': description,
            'version': version,
            'publication_date': publication_date,
            'author': author,
            'mantainer': mantainer,
            'license': license,
            'requires_compilation': requires_compilation,
            'depends': depends,
            'imports': imports
        }

    # parse dependencies data from a CRAN packet
    def __parse_dependencies(self, dependencies_str) -> list[tuple[str, str]]:
        '''
        Parse dependencies string
        
        args:
        -----
            dependencies_str (str): String with dependencies
            
        Returns:
        --------
            
            list: List of tuples with dependencies and versions
            
        '''

        # Remove unnecessary line breaks, tabs, and spaces
        patron = r'\S+\s*(?:\(([^\)]*)\))?'

        # Get names and versions of dependencies
        versiones = re.findall(patron, dependencies_str)
        nombres = re.split(r'\s*,\s*', dependencies_str)
        nombres = [re.sub(r'\s*\(.*\)', '', nombre) for nombre in nombres]
        return list(zip(nombres, versiones))

    # parse authors data from a CRAN packet
    def __sanitize_str(self, s) :

        # Remove unnecessary line breaks, tabs, and spaces
        s = s.replace('\n', ' ')
        s = s.replace('\t', ' ')
        s = re.sub(r'\s+', ' ', s)

        return s

    # Construct object of class Package
    def pkg_builder(self, pkg_name) -> Package:

        # Get package data
        pkg_data = self.__parse_pkg_data(pkg_name)

        # sanitize data
        description_data = self.__sanitize_str(pkg_data['description'])
        version_data = self.__sanitize_str(pkg_data['version'])
        publication_date_data = self.__sanitize_str(pkg_data['publication_date'])
        authors_data = self.__sanitize_str(pkg_data['author'])
        mantainer_data = self.__sanitize_str(pkg_data['mantainer'])

        # Be careful with the license, requires_compilation, depends, and imports fields
        try:
            license_data = self.__sanitize_str(pkg_data['license'])
        except:
            license_data = None
        
        try:
            requires_compilation_data = self.__sanitize_str(pkg_data['requires_compilation'])
        except:
            requires_compilation_data = None
        
        depends_list = []
        try:
            depends_data = self.__sanitize_str(pkg_data['depends'])

            # Create list of dependencies objects
            depends_list = self.__parse_dependencies(depends_data)
            for i, dep in enumerate(depends_list):
                d = Dependency(dep[0], "IMP")
                d.version = dep[1]
                depends_list[i] = d
        except:
            depends_data = None


        imports_list = []
        try:
            imports_data = self.__sanitize_str(pkg_data['imports'])

            # Create list of dependencies objects
            imports_list = self.__parse_dependencies(imports_data)
            for i, imp in enumerate(imports_list):
                d = Dependency(imp[0], "DEP")
                d.version = imp[1]
                imports_list[i] = d
        except:
            imports_data = None

        # Parse required compilation data
        if requires_compilation_data == 'yes':
            requires_compilation_data = True
        else:
            requires_compilation_data = False

        # Construct object of class Package
        package = Package(pkg_name)

        # Set package attributes
        package.description = description_data
        package.version = version_data
        package.publication_date = publication_date_data
        package.authors_data = authors_data
        package.mantainer = mantainer_data
        package.licenses = license_data
        package.requires_compilation = requires_compilation_data
        package.dependencies = depends_list + imports_list
        package.links.append(f'https://cran.r-project.org/package={pkg_name}')
        
        # Return package
        return package




