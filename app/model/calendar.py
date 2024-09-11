from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from typing import ClassVar

from app.services.util import generate_unique_id, date_lower_than_today_error, event_not_found_error, \
    reminder_not_found_error, slot_not_available_error

@dataclass
class Reminder:
    date_time: datetime

    EMAIL: str = "email"
    SYSTEM: str = "system"

    type: str = EMAIL



    def __str__(self) -> str:
        return f"Reminder on {self.date_time} of type {self.type}"

@dataclass
class Event:
    title: str
    description: str
    date_: date
    start_at: time
    end_at: time
    reminders: list[Reminder]
    id: str = field(default_factory=generate_unique_id)

    def add_reminder(self, date_time: datetime, type: str = Reminder.EMAIL):
        reminder = Reminder(date_time=date_time, type=type)
        self.reminders.append(reminder)


    def delete_reminder(self, reminder_index: int):
        if 0 <= reminder_index < len(self.reminders):
            del self.reminders[reminder_index]
        else:
            reminder_not_found_error()



    def __str__(self) -> str:
        return """
            ID: {id}
            Event title: {title}
            Description: {description}
            Time: {start_at} - {end_at}
        """


class Day:

    def __init__(self, date_: date):
        self.date_: date = date_
        self.slots: dict[time, str | None] = {}
        self._init_slots()

    def _init_slots(self):
        current_time = time(0, 0)
        end_time = time(23, 45)
        slot_duration = timedelta(minutes=15)

        while current_time <= end_time:
            self.slots[current_time] = None
            current_datetime = datetime.combine(self.date_, current_time) + slot_duration
            current_time = current_datetime.time()

    def add_event(self, event_id: str, start_at: time, end_at: time):
        current_time = start_at

        while current_time < end_at:
            if self.slots.get(current_time) is not None:
                slot_not_available_error()
                return

            current_datetime = datetime.combine(self.date_, current_time) + timedelta(minutes=15)
            current_time = current_datetime.time()

        current_time = start_at
        while current_time < end_at:
            self.slots[current_time] = event_id
            current_datetime = datetime.combine(self.date_, current_time) + timedelta(minutes=15)
            current_time = current_datetime.time()

    def delete_event(self, event_id: str):
        deleted = False
        for slot, saved_id in self.slots.items():
            if saved_id == event_id:
                self.slots[slot] = None
                deleted = True
        if not deleted:
            event_not_found_error()

    def update_event(self, event_id: str, start_at: time, end_at: time):
        for slot in self.slots:
            if self.slots[slot] == event_id:
                self.slots[slot] = None

        for slot in self.slots:
            if start_at <= slot < end_at:
                if self.slots[slot]:
                    slot_not_available_error()
                else:
                    self.slots[slot] = event_id


class Calendar:

    def __init__(self):
        self.days: dict[date, Day] = {}
        self.events: dict[str, Event] = {}

    def add_event(self, title: str, ):