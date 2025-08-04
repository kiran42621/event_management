from pydantic import BaseModel, EmailStr, model_validator
from datetime import datetime
from typing import List, Optional

from .utils import *

import os

# Get TIMEZONE from env-file or default "Asia/Kolkata"
TIMEZONE = os.getenv("TIMEZONE") or "Asia/Kolkata"

class AttendeesList(BaseModel):
  name: str
  email: EmailStr

  class Config:
    from_attributes = True

class Event(BaseModel):
  name: str
  location: str
  startTime: datetime
  endTime: datetime
  maxCapacity: int = 0

  # Converting utc to localtime.
  @model_validator(mode="after")
  def convert_all_to_local(cls, values):
    # print("Here", values)
    values.startTime = from_utc(values.startTime, TIMEZONE)
    values.endTime = from_utc(values.endTime, TIMEZONE)
    return values

  class Config:
    from_attributes = True

class EventDetail(Event):
  id: str
  attendees: Optional[List[AttendeesList]] = None

  class Config:
    from_attributes = True

