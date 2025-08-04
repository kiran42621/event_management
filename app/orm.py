from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func

from .utils import *

import uuid
import os

Base = declarative_base()

TIMEZONE = os.getenv("TIMEZONE") or "Asia/Kolkata"

def gen_uuid():
  return uuid.uuid4().hex

class Events(Base):
  __tablename__ = 'events'

  id = Column(String, primary_key=True, default=gen_uuid)
  name = Column(String, unique=True)
  location = Column(String)
  startTime = Column(DateTime, server_default=func.now()) 
  endTime = Column(DateTime, server_default=func.now())
  maxCapacity = Column(Integer)
  
  # Relationship
  attendees = relationship("Attendees", back_populates="events")

  createdAt = Column(DateTime, server_default=func.now())
  updatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())

  # Converting local time to utc
  @validates("startTime", "endTime", "createdAt", "updatedAt")
  def convert_to_utc(self, key, dt):
    return to_utc(dt, TIMEZONE)

class Attendees(Base):
  __tablename__ = 'attendees'

  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String)
  email = Column(String, nullable=False)
  eventId = Column(String, ForeignKey("events.id", ondelete="CASCADE"))

  # Relationship
  events = relationship("Events", back_populates="attendees", primaryjoin="Events.id == Attendees.eventId")
