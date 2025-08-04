from datetime import datetime
from dateutil import parser

import pytz

# Helper function to create local time to utc
def to_utc(dt: datetime, tz_str: str) -> datetime:
  if dt.tzinfo is None:
    if not tz_str:
      raise ValueError("Naive datetime requires a timezone")
    local_tz = pytz.timezone(tz_str)
    dt = local_tz.localize(dt)
  return dt.astimezone(pytz.utc)

# Helper function to create utc to local time
def from_utc(utc_dt: datetime, tz_str: str) -> datetime:
  if isinstance(utc_dt, str):
    utc_dt = parser.isoparse(utc_dt)
  if utc_dt.tzinfo is None:
    utc_dt = pytz.utc.localize(utc_dt)
  local_tz = pytz.timezone(tz_str)
  return utc_dt.astimezone(local_tz)
