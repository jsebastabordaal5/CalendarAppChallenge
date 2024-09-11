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

    def __str__(self):
        return f"Reminder on {self.date_time} of type {self.type}"

@dataclass
class Event:
    title: str
    description: str
    date_: date
    start_at: time
    end_at: time

    reminders: list[Reminder] = field(default_factory=list)
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
        return (f"ID: {self.id}\n"
                f"Event title: {self.title}\n"
                f"Description: {self.description}\n"
                f"Time: {self.start_at} - {self.end_at}")


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

    def add_event(self, title: str, description: str, date_: date, start_at: time, end_at: time) -> str:

        if date_ < datetime.now().date():
            date_lower_than_today_error()
            return ""


        if date_ not in self.days:
            self.days[date_] = Day(date_)
            event_id = generate_unique_id()
            event = Event(
                title=title,
                description=description,
                date_=date_,
                start_at=start_at,
                end_at=end_at,
                id=event_id
            )

        self.days[date_].add_event(title, description, date_, start_at, end_at)
        self.events[event_id] = event

        return event_id

    def add_reminder(self, event_id: str, date_time: datetime, type_: str):
        if event_id not in self.events:
            event_not_found_error()
            return
        self.events[event_id].add_reminder(date_time, type_)

    def find_available_slots(self, date_: date) -> list[time]:
        if date_ not in self.days:
            return []

        day = self.days[date_]
        available_slots = [slot for slot, event in day.slots.items() if event is None]
        return available_slots

    def update_event(self, event_id: str, title: str, description: str, date_: date, start_at: time, end_at: time):
        event = self.events[event_id]
        if not event:
            event_not_found_error()

        is_new_date = False

        if event.date_ != date_:
            self.delete_event(event_id)
            event = Event(title=title, description=description, date_=date_, start_at=start_at, end_at=end_at)
            event.id = event_id
            self.events[event_id] = event
            is_new_date = True
            if date_ not in self.days:
                self.days[date_] = Day(date_)
            day = self.days[date_]
            day.add_event(event_id, start_at, end_at)
        else:
            event.title = title
            event.description = description
            event.date_ = date_
            event.start_at = start_at
            event.end_at = end_at

        for day in self.days.values():
            if not is_new_date and event_id in day.slots.values():
                day.delete_event(event.id)
                day.update_event(event.id, start_at, end_at)

    def delete_event(self, event_id: str):
        if event_id not in self.events:
            event_not_found_error()

        self.events.pop(event_id)

        for day in self.days.values():
            if event_id in day.slots.values():
                day.delete_event(event_id)
                break

    def find_events(self, start_at: date, end_at: date) -> dict[date, list[Event]]:
        events: dict[date, list[Event]] = {}
        for event in self.events.values():
            if start_at <= event.date_ <= end_at:
                if event.date_ not in events:
                    events[event.date_] = []
                events[event.date_].append(event)
        return events

    def delete_reminder(self, event_id: str, reminder_index: int):
        event = self.events.get(event_id)
        if not event:
            event_not_found_error()

        event.delete_reminder(reminder_index)

    def list_reminders(self, event_id: str) -> list[Reminder]:
        event = self.events.get(event_id)
        if not event:
            event_not_found_error()

        return event.reminders