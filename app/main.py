from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional

from .objects_events import Event, EventDetail, AttendeesList
from .orm import Events, Attendees

from datetime import datetime, timezone

# uncomment below lines if not using docker
# from dotenv import load_dotenv
# load_dotenv()

import os

# Database info
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DB = os.getenv('POSTGRES_DB')

# Pagenation limit for event list
PAGENATION_LIMIT = os.getenv('PAGENATION_LIMIT')

DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

services = FastAPI(openapi_url="/docs", docs_url="/apidocs")

event_db = create_engine(DB_URL)

# Function to get DB session instance
def get_db():
  global event_db
  Session = sessionmaker(bind=event_db)
  db_session = Session()
  return db_session

# Status or Health check
@services.get("/")
def index():
  return {"status": "Running..."}

# Post request to create event which takes valid Event details and returns success event creation
@services.post("/events", response_model=EventDetail, response_model_exclude={"__all__": {"attendees"}})
def post_event(eventDetails: Event):
  # Basic validations
  # Check event details
  if not eventDetails:
    raise HTTPException(status_code=400, detail="Invalid event details")
  
  # Date check
  if (eventDetails.startTime > eventDetails.endTime) or (eventDetails.startTime < datetime.now(timezone.utc)):
    raise HTTPException(status_code=400, detail="Invalid date")
  
  # Maximum capacity check
  if eventDetails.maxCapacity <= 0:
    raise HTTPException(status_code=400, detail="Maximum capacity should be more than 0")
  
  db_session = get_db()
  try:
    event = db_session.query(Events).filter(Events.name == eventDetails.name)

    # Rasie exception if event already exist
    if len(event.all()) > 0:
      # print("Already exists")
      raise HTTPException(status_code=400, detail="Event name already exists")
    new_event = Events(**eventDetails.dict())
    db_session.add(new_event)
    db_session.flush()
    db_session.commit()
    return EventDetail.from_orm(new_event)
  except Exception as e:
    db_session.rollback()
    raise e
  finally:
    db_session.close()

# Get request to get all upcoming event with page number which takes page number as input and returns list of events.
@services.get("/events", response_model=List[EventDetail], response_model_exclude={"__all__": {"attendees"}})
def get_event(page:int = 1):
  db_session = get_db()
  # Page number validation
  if page <= 0:
    raise HTTPException(status_code=400, detail="Page cannot be negative or zero")

  try:
    events = db_session.query(Events).filter(Events.startTime >= datetime.now(timezone.utc)).limit(PAGENATION_LIMIT).offset((int(PAGENATION_LIMIT) * page) - int(PAGENATION_LIMIT))
    
    # No event validation
    if len(events.all()) <= 0:
      raise HTTPException(status_code=400, detail="No events found")

    response = [ EventDetail.from_orm(event) for event in events ]
    return response
  except Exception as e:
    db_session.rollback()
    raise e
  finally:
    db_session.close()

# Post request to register an attendee to the event takes event_id and attendee details as input and returns Event detail on successfull registration
@services.post("/events/{event_id}/register", response_model=EventDetail, response_model_exclude_none=True)
def register_attendee(event_id: str, attendee: AttendeesList):
  # event_id validation
  if not event_id:
    raise HTTPException(status_code=400, detail="Invalid event id")
  
  # attendee details validation
  if not attendee:
    raise HTTPException(status_code=400, detail="Invalid attendee details")
  
  db_session = get_db()
  try:
    event = db_session.query(Events).filter(Events.id == event_id).first()

    # Event exist validation
    if not event:
      raise HTTPException(status_code=400, detail="Invalid event id")
    
    # MaxCapacity validation
    if len(event.attendees) >= event.maxCapacity:
      raise HTTPException(status_code=400, detail="Currently event attendee slots are full")

    existing_attendee = db_session.query(Attendees).filter(
        Attendees.eventId == event_id,
        Attendees.email == attendee.email
    ).first()

    # Attendee exists validation
    if existing_attendee:
      raise HTTPException(status_code=400, detail="Attendee already registered for this event")

    new_attendee = Attendees(
      name=attendee.name,
      email=attendee.email,
      eventId=event_id
    )
    db_session.add(new_attendee)
    db_session.flush()
    db_session.commit()
    return EventDetail.from_orm(event)
  except Exception as e:
    db_session.rollback()
    raise e
  finally:
    db_session.close()

# Get request to retrieve attendies takes event_id as input and returns Event detail with attendee list.
@services.get("/events/{event_id}/attendees", response_model=EventDetail, response_model_exclude_none=True)
def get_attendees(event_id: str):
  # Validate event_id
  if not event_id:
    raise HTTPException(status_code=400, detail="Invalid event id")
  
  db_session = get_db()
  try:
    event = db_session.query(Events).filter(Events.id == event_id).first()
    # Event exists validation
    if not event:
      raise HTTPException(status_code=400, detail="Invalid event id")
    return EventDetail.from_orm(event)
  except Exception as e:
    db_session.rollback()
    raise e
  finally:
    db_session.close()

