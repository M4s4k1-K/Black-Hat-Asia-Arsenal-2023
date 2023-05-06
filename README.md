# Forecasting ATT&CK Flow by Recommendation System Based on APT
## Description
This tool is to forecast undetected ATT&CK techniques based on collaborative filtering and graph databases.  
link here
Please, check this here for more information.  
[here](https://github.com/M4s4k1-K/Black-Hat-Asia-Arsenal-2023/blob/main/Black-Asia-Arsenal-2023-Presentation.pdf)
The algorithm is based on the proposed method in the paper below.  
[paper](https://ieeexplore.ieee.org/document/10032036)  

## Prerequisites (Tested Environment)
- Python 3.10.10
- Django 4.1.7
- Neo4j 4.4.9
- Java SE 11 or later
- mysqlclient 2.1.1
- Docker 20.10.22
- Docker Compose 2.15.1
## Getting Started
### Setting up Python and Django
1. Install Python (version 10.X).
2. Install the necessary packages using the requirements.txt file. Run the following command:
```
pip install -r requirements.txt
```
### Setting up Neo4j
1. Download Neo4j (version 4.X) from the following link:
https://neo4j.com/download-center/#community
1. Start Neo4j and complete the initial setup by accessing localhost:7474.
1. Place Groups.csv, Techniques.csv, and Tactics.csv into the import directory.
1. Place make_neo4j_data.ipynb, neo4j.ini, groups_techniques.csv, and matrix.csv into the appropriate directory in your environment and execute make_neo4j_data.ipynb.
1. Please add the following configuration to your settings.py file
```
NEO4J_USERNAME = "Your Username"
NEO4J_PASSWORD = "Your Password"
NEO4J_URL = "bolt://localhost:7687"
```

### Setting up ATT&CK DB
1. Create a .env file from the .env.sample.
```
copy .env.sample .env
```
2. Enter your desired values into the .env file.
```
# fill in your own values
MARIADB_USER="Your Username"
MARIADB_PASSWORD="Your Password"
MARIADB_DATABASE="Your DB name"
```
3. Start the application.
```
docker compose -f docker-compose.local.yaml up -d
```
4. Create the tables.
```
docker compose -f docker-compose.local.yaml run operation python seed.py
```
5. Please add the following configuration to your settings.py file.  
NAME, USER, and PASSWORD are set by you in .env.  
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    # Information configured in .env
    'Your DB name': {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "Your DB name",
        "USER": "Your Username",
        "PASSWORD": "Your Password",
        "HOST": "localhost",
        "PORT": "3306"
    }
}
```
6. Run the following command:
```
python manage.py inspectdb
```
## Running the Application
1. Set up the Neo4j database and the ATT&CK DB.
2. Run the following command to start the development server.
```
python manage.py runserver
```

## How to implement
[here](https://github.com/M4s4k1-K/Black-Hat-Asia-Arsenal-2023/blob/main/implementation.md)
