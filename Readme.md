# ReadMe: Event Management
### Description
---
Event management API for Task
This is a Restful API built with FastAPI for simple event management

### Tech stack
1. Python(FastAPI)
2. PostgreSQL
3. Docker(Optional)

### Getting started / Installation
#### Method 1: Docker (Recommended)
1. Change appropriate values in .env.template file and rename it as .env.
``` docker-compose up --build ```
2. Run above command. This will initialize everything in a container. After successfull build and run application should be available on ```http://127.0.0.1:8000```.
#### Method 2: Manual installation
1. Extract zip to a Folder.
2. Create a venv inside Folder.
```python -m venv venv```
3. Inside virtual environment install all the required libraries.
```pip install -r requirements.txt```
4. Change appropriate values in .env.template file and rename it as .env.
5. Run ./app/schema.sql queries inside database.
6. Run tests.
```pytest -v -p no:warnings```
7. Run application.
```uvicorn app.main:services --host 0.0.0.0 --port 8000```
8. Now application should be running on http://localhost:8000
### Environment variables
```
POSTGRES_USER=<Postgres_User>
POSTGRES_PASSWORD=<User_Password>
POSTGRES_DB=<Database_name>
POSTGRES_HOST=<Database_host>
POSTGRES_PORT=<Database_port>
PAGENATION_LIMIT=<Pagenation_length>
TIMEZONE=<Time_zone>
```
### API Documentation
swagger specs is available on "/apidocs"
json specs is available on "/docs"
### Testing
```pytest -v -p no:warnings```
use above command to run tests
### Project structure
```
event_management/
├── app/
│   ├── tests/
│   │   └── test_event.py   // unit test file
│   ├── main.py             // main service file(app runs here)
│   ├── objects_events.py   // Pydantic models file 
│   ├── orm.py              // SqlAlchemy models file
│   ├── utils.py            // Helper functions
│   └── schema.sql          // SQL Schema
├── Dockerfile             // Dockerfile
├── docker-compose.yaml    // docker-compose config file
├── Readme.md              // Readme file
├── requirements.txt       // Requirements file
├── .env                   // Environment file
├── .env.template          // Environment file template
└── .gitignore             // git-ignore file
```

## Thank you