from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import ClassVar

from app.services.util import generate_unique_id, date_lower_than_today_error, event_not_found_error, \
    reminder_not_found_error, slot_not_available_error


class Reminder:

    "EMAIL": str = "email"
    "SYSTEM": str = "system"

    date_time: datetime
    type: str

    def __str__(self):
        return f"Reminder on {self.date_time} of type {self.type}"
