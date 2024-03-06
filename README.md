# SMO

This repository hosts the Synergetic Meta-Orchestrator consisting of a Flask REST API that is responsible for translating intent formulations, constructing and enforcing deployment plans for Hyper Distributed Application Graphs.

## Getting started
Use docker compose:
```
docker-compose up
```
The API is available at port 8000.

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
