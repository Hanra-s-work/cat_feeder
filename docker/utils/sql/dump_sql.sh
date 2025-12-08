#!/bin/bash
# 
# +==== BEGIN CatFeeder =================+
# LOGO: 
# ..............(..../\
# ...............)..(.')
# ..............(../..)
# ...............\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: dump_sql.sh
# CREATION DATE: 08-12-2025
# LAST Modified: 2:24:51 08-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The bash script used to allow an easy way of exporting a database content.
# // AR
# +==== END CatFeeder =================+
# 
# Function to generate SQL file header
generate_sql_header() {
    local filename=$1
    local creation_date=$(date +"%d-%m-%Y")
    local last_modified=$(date +"%H:%M:%S %d-%m-%Y")
    
    cat <<EOF
/* 
 * +==== BEGIN CatFeeder =================+
 * LOGO: 
 * ..............(..../\\\\
 * ...............)..(.')
 * ..............(../..)
 * ...............\\\\(__)|
 * Inspired by Joan Stark
 * source https://www.asciiart.eu/
 * animals/cats
 * /STOP
 * PROJECT: CatFeeder
 * FILE: $filename
 * CREATION DATE: $creation_date
 * LAST Modified: $last_modified
 * DESCRIPTION: 
 * This is the project in charge of making the connected cat feeder project work.
 * /STOP
 * COPYRIGHT: (c) Cat Feeder
 * PURPOSE: This is the database structure file that is in charge of deploying the structure and/or data into the database.
 * // AR
 * +==== END CatFeeder =================+
 */

EOF
}

# Function to list available databases
list_databases() {
    local user=$1
    local pass=$2
    local host=$3
    local port=$4
    
    echo ""
    echo "Testing connection and fetching available databases..."
    DATABASES=$(mariadb -u $user -p$pass -h $host -P $port -e "SHOW DATABASES;" 2>&1)
    if [ $? -ne 0 ]; then
        echo "Error: Failed to connect to database server"
        echo "$DATABASES"
        exit 1
    fi
    
    echo "Connection successful!"
    echo "Available databases:"
    echo "$DATABASES" | tail -n +2 | grep -v "information_schema\|performance_schema\|mysql" | nl -w2 -s'. '
    echo ""
}

echo "Welcome to $0"

echo -n "Enter username: "
read username

echo "Enter password: "
read -s password

echo -n "Enter database host: "
read host

echo -n "Enter database port: "
read port

# Ask if user wants to list databases
echo ""
echo -n "Query available databases? [(Y)es/(n)o]: "
read -n 1 query_choice
echo ""

if [ "$query_choice" = "Y" ] || [ "$query_choice" = "y" ]; then
    list_databases "$username" "$password" "$host" "$port"
fi

echo -n "Enter database(s) to export [syntax: db1 [db2 db3]]: "
read db

echo -n "Enter save file name (no file extension): "
read savefile

if [ "$db" == "" ] || [ "$db" == "\n" ]; then
    echo "No database specified, dumping all databases present"
    db="--all-databases"
else
    db="--databases $db"
fi

echo "Dumping sql from database:"
# Generate header and dump data
generate_sql_header "$savefile.sql" > "$savefile.sql"
mariadb-dump -u $username -p$password -h $host -P $port $db >> "$savefile.sql"
if [ $? -ne 0 ]; then
    STATUS=$?
    echo "Error: Failed to dump data"
    # Rename file to indicate error for inspection
    mv "$savefile.sql" "$savefile.error.sql"
    echo "Partial dump saved to: $savefile.error.sql (for inspection)"
    exit $STATUS
fi
echo "Data dumped to: $savefile.sql"

echo "When displayed, press the Q key to exit."
echo "Display file content? [(Y)es/(n)o]"
read -n 1 choice

echo "Displaying file content:"
if [ "$choice" = "Y" ] || [ "$choice" = "y" ]; then
    cat $savefile.sql | less
fi

echo "(c) Created by Henry Letellier"
