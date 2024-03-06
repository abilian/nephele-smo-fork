# SMO

This repository hosts the Synergetic Meta-Orchestrator consisting of a Flask REST API that is responsible for translating intent formulations, constructing and enforcing deployment plans for Hyper Distributed Application Graphs.

## Getting started
### Creating the database
Create a PostgreSQL database using Docker and run in detached mode:
```bash
docker run -d \
	--name postgres-db \
    -p 5432:5432 \
    -e PGUSER=root \
    -e POSTGRES_USER=root \
	-e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=smo \
	postgres:16.2
```

### Running the Flask app:
```
# install the requirements
(.venv) $ pip install -r requirements.txt

# create the .env file
(.venv) src$ cp .env.example .env
```

Open the new .env file and adjust the values, so that the credentials match to those of your database.

Run the app:
```
cd src/

python appy.py
```

## File structure
The folder structure of the codebase is as follows:
```
/src
├── errors  					     # custom errors and handlers
├── models						     # db models
├── routes						     # app blueprints
├── services				         # business logic for the routes
├── utils					         # misc
```
