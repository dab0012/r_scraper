#!/bin/bash

# This script is used to configure the database for the application
# It is called from the install.sh script
# 
# Author: 	Daniel Alonso (@dnllns)
# Date: 	  2022-12-24
# Version: 	1.0
# Project:  OLIVIA
# License: 	GNU General Public License v3.0

# Database connection configuration
# ----------------------

DB_HOST=localhost                       # Database host          
DB_PORT=3306                            # Database port
DB_USERNAME=                            # Database username
DB_PASSWORD=                            # Database password

# Database application configuration
# ----------------------

DB_NAME=r_network                       # Database name
DB_APP_USERNAME=scraper                 # Database username for the application
DB_APP_PASSWORD=scraper123$$$12_        # Database password for the application

# functions
print_status() {
  if [ $? -eq 0 ]; then
    # ansi greencolor with "OK" message
    echo -e "    \e[32mOK\e[0m"
  else
    # ansi redcolor with "Error" message
    echo -e "    \e[31mError\e[0m"
    exit 1
  fi
}


# Build the database
# ----------------------

# Check if the database exists
echo "Checking if database $DB_NAME exists"
if [ $(mysql -u $DB_USERNAME -p$DB_PASSWORD -e "SHOW DATABASES LIKE '$DB_NAME';" | wc -l) -eq 2 ]; then

    # Tell the user that the database already exists and is going to be deleted
    # Ask the user if they want to continue
    # its an alert message so its in ansi orange color
    echo -e "\e[33mThe database $DB_NAME already exists and is going to be deleted\e[0m"
    read -p "Do you want to continue? [y/n]: " -n 1 -r


    # If the user does not want to continue, exit the script
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        echo -e "\nExiting"
        exit 1
    else
        echo -e "\nContinuing..."
        # Delete the database
        echo -e "[+] Deleting database $DB_NAME"
        mysql -u $DB_USERNAME -p$DB_PASSWORD -e "DROP DATABASE $DB_NAME;" > /dev/null 2>&1
        print_status
    fi
fi

# Check if the user exists
echo "Checking if user $DB_APP_USERNAME exists"
if [ $(mysql -u $DB_USERNAME -p$DB_PASSWORD -e "SELECT User FROM mysql.user WHERE User = '$DB_APP_USERNAME';" | wc -l) -eq 2 ]; then

    # Tell the user that the user already exists and is going to be deleted
    # Ask the user if they want to continue
    # its an alert message so its in ansi orange color
    echo -e "\e[33mThe user $DB_APP_USERNAME already exists and is going to be deleted\e[0m"
    read -p "Do you want to continue? [y/n]: " -n 1 -r
    
    # If the user does not want to continue, exit the script
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        echo -e "\nExiting"
        exit 1
    else
        echo -e "\nContinuing..."
        # Delete the user
        echo -e "[+] Deleting user $DB_APP_USERNAME"
        mysql -u $DB_USERNAME -p$DB_PASSWORD -e "DROP USER '$DB_APP_USERNAME'@'$DB_HOST';" > /dev/null 2>&1
        print_status
    fi
fi

# Create the database
echo "[+] Creating database $DB_NAME..."
mysql -u $DB_USERNAME -p$DB_PASSWORD -e "CREATE DATABASE $DB_NAME;"  > /dev/null 2>&1
print_status

# Create the user for the application
echo "[+] Creating user $DB_APP_USERNAME..."
mysql -u $DB_USERNAME -p$DB_PASSWORD -e "CREATE USER '$DB_APP_USERNAME'@'$DB_HOST' IDENTIFIED BY '$DB_APP_PASSWORD';" > /dev/null 2>&1
print_status

# Grant privileges to the user
echo "[+] Granting privileges to $DB_APP_USERNAME..."
mysql -u $DB_USERNAME -p$DB_PASSWORD -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_APP_USERNAME'@'$DB_HOST' WITH GRANT OPTION;" > /dev/null 2>&1
print_status

# Flush privileges
echo "[+] Flushing privileges..."
mysql -u $DB_USERNAME -p$DB_PASSWORD -e "FLUSH PRIVILEGES;" > /dev/null 2>&1
print_status

# Create the tables
echo "[+] Creating tables..."
mysql -u $DB_APP_USERNAME -p$DB_APP_PASSWORD $DB_NAME < config/db/db_schema.sql > /dev/null 2>&1
print_status

# # Import the data
# echo "Importing data"
# mysql -u $DB_APP_USERNAME -p$DB_APP_PASSWORD $DB_NAME < db_data.sql

echo "Database configured"