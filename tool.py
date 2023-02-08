from bs4 import BeautifulSoup
from modules.db import DatabaseHandler
from modules.package import Package
from modules.proxy_request import RequestHandler
from modules.cran_scraper import PackageScraper
from colorama import Fore
from modules.util import print_colored


# Functions
# -----------------------------------------------

# Function to scrape the table
def scrape_table(table, packages):
    
    # We iterate over each row of the table
    for row in table.find_all("tr"):

        # We extract the cells of the current row
        cells = row.find_all("td")

        package_name = ""
        # If there are cells in the row
        if cells:
            try: 
                # We extract the name of the package
                # The name is in the first cell of the row
                package_name = cells[0].find("a").text   

                # We create a Package object
                # We add the Package structure, to later process them all
                curr_package = Package(package_name)
                packages.append(curr_package)

            # If an error occurs, we show the error message
            except Exception as e:
                
                # message string
                message = "Error processing package: " + package_name
                message += "Exception: " + e.__class__.__name__ 
                message += "Error: " + str(e)

                # Print error message
                print_colored(message, Fore.RED)
                print("Continuing...")

# Script
# -----------------------------------------------

# List of packages in CRAN
packages = []
all_packages_names =  False

# Create object of class DatabaseHandler
# We instantiate the connection to the database
db = DatabaseHandler()
cnx = db.get_connection()

# We load the CRAN packages in the packages list
# The packages are obtained by scraping the CRAN page
rh = RequestHandler()
response = rh.do_request("https://cran.r-project.org/web/packages/available_packages_by_name.html", retry=True)

# If the request was successful
if response.status_code == 200:

    # We parse the HTML content of the web page using BeautifulSoup
    # We extract the table that contains the information of the CRAN packages
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")

    # We scrape the table
    scrape_table(table, packages)

    # If the list of packages is not empty
    if packages:
        all_packages_names = True

else:

    # Build the error message string
    message = "Error making the request"
    message += "Review the RequestHandler"
    message += "The package list could not be obtained"
    message += "Ending program execution"

    # Print error message
    print_colored(message, Fore.RED)
    

# Show if the packages were obtained
print("Initial data obtained:")
if all_packages_names:
    print_colored("OK", Fore.GREEN)
else:
    print_colored("ERROR", Fore.RED)
    print("Finalizando ejecución del programa")
    exit()



# Process packages
# ----------------

# Get the number of packages that are already in the database
query_result = db.execute_query("SELECT COUNT(*) FROM packages")
num_packages_in_db = query_result[0][0]

print("Starting to process packages...")
print("Number of packages: ", len(packages))
print("Number of packages saved in db: ", str(num_packages_in_db) + "/" + str(len(packages)), "(", round(num_packages_in_db / len(packages) * 100, 2), "%)")


# Create object of class Scraper
scraper = PackageScraper(rh)

# Iterate over the packages
for package in packages:

    # Print the name of the package
    print_colored("\nProcessing package: " + package.name, Fore.BLUE)

    # Get the package from the database
    p = Package(package.name).get_package(cnx)

    # If the package is already in the database, dont do anything
    if p:
        # buid message string
        message = "Package already in database: " + package.name
        message += "\nNumber of packages saved in db: " + str(num_packages_in_db) + "/" + str(len(packages)) + " (" + str(round(num_packages_in_db / len(packages) * 100, 2)) + "%)"

        # Print message
        print_colored(message, Fore.YELLOW)
        continue


    # Process the package
    p = scraper.pkg_builder(package.name)
    result = p.save(cnx)

    # If the package wasn't saved in the database
    if not result:
        # Build the error message string
        message = "Error saving package: " + p.name
        message += "\nNumber of packages saved in db: " + str(num_packages_in_db) + "/" + str(len(packages)) + " (" + str(round(num_packages_in_db / len(packages) * 100, 2)) + "%)"
        
        # Print error message
        print_colored(message, Fore.RED)
        print("Ending program execution")
        cnx.close()
        exit()

    # If the package was saved in the database
    else:

        # Increment the number of packages in the database
        num_packages_in_db += 1

        # buid message string
        message = "Package saved: " + p.name
        message += "\nNumber of packages saved in db: " + str(num_packages_in_db) + "/" + str(len(packages)) + " (" + str(round(num_packages_in_db / len(packages) * 100, 2)) + "%)"

        # Print message
        print_colored(message, Fore.GREEN)


# Close the connection to the database
cnx.close()

# Show final message
print_colored("All packages processed", Fore.GREEN)

# End of the program
exit()
