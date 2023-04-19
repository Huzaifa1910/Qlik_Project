# Qlik_Project
Project Name
Project Name is a Python-based data scraping tool that extracts data from a website and stores it in a MySQL database. It uses the Airflow platform to schedule and execute the scraping tasks. This documentation provides a step-by-step guide on how to install and configure the project.

# Installation
Clone the project from GitHub:

git clone https://github.com/<username>/<project-name>.git
Navigate to the project directory:

cd <project-name>
Install the required packages:

pip install -r requirements.txt
Configuration
Create a MySQL database and a user with remote access. Note down the database name, host, port, username, and password.

Install the MySQL package for Airflow:

pip install apache-airflow[mysql]
Edit the config.py file and enter the database details:

DB_CONFIG = {
    'database': '<database-name>',
    'host': '<host>',
    'port': <port>,
    'user': '<username>',
    'password': '<password>'
}
In the Airflow web UI, go to the Admin section and click on "Connections".

Click on the "Create" button and enter the following details:

Conn Id: mysql_default
Conn Type: MySQL
Host: <host>
Port: <port>
Schema: <database-name>
Login: <username>
Password: <password>
Click on the "Save" button to create the connection.

Usage
Start the Airflow scheduler:

airflow scheduler
Start the Airflow webserver:

airflow webserver
Open the Airflow web UI in your browser (http://localhost:8080) and navigate to the "DAGs" section.

Turn on the "project_name" DAG and trigger a run by clicking on the "Trigger DAG" button.

Monitor the progress of the scraping task in the Airflow web UI.

# Unique Steps
To install the MySQL package for Airflow, run the following command:

pip install apache-airflow[mysql]
This package includes the necessary dependencies to connect to a MySQL database from Airflow.

## To create a user with remote access to the MySQL database, run the following SQL command:

CREATE USER '<username>'@'%' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON <database-name>.* TO '<username>'@'%';
This command creates a new user with a password and grants all privileges on the specified database to that user. The % symbol allows the user to connect from any host.
