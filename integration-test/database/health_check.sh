#!/bin/bash

# Function to check if the database exists
check_database_existence() {
    PGPASSWORD="$POSTGRES_PASSWORD" psql -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='ready'"
}

# Attempt to check the existence of the database
if check_database_existence; then
    echo "Database exists"
    exit 0
else
    echo "Database does not exist"
    exit 1
fi
