from datetime import datetime, timedelta
from typing import List
from abc import ABC, abstractmethod

from resy_bot.errors import NoSlotsError
from resy_bot.models import Slot, ReservationRequest


class AbstractSelector(ABC):
    @abstractmethod
    def select(self, slots: List[Slot], request: ReservationRequest) -> Slot:
        pass


class SimpleSelector(AbstractSelector):
    def select(self, slots: List[Slot], request: ReservationRequest) -> Slot:
        """
        simple selection algo that assumes a sorted list of slots
        if preferred slot is provided, that is the only selectable option
        """
        window_timedelta = timedelta(hours=request.window_hours)
        ideal_datetime = datetime(
            request.target_date.year,
            request.target_date.month,
            request.target_date.day,
            request.ideal_hour,
            request.ideal_minute,
        )
        min_time = ideal_datetime - window_timedelta
        max_time = ideal_datetime + window_timedelta

        last_diff = None
        last_slot = None

        for slot in slots:
            diff = slot.date.start - ideal_datetime
            matches_preferred_type = (
                request.preferred_type is None
                or slot.config.type == request.preferred_type
            )

            # once we're after the target time, the slots will only get worse
            # so take the first we find
            if diff >= timedelta(microseconds=0) and slot.date.start <= max_time:
                if matches_preferred_type:
                    if not last_diff or diff < last_diff:
                        return slot
                    elif last_diff == abs(diff) and request.prefer_early:
                        return last_slot
                    elif last_diff == abs(diff) and not request.prefer_early:
                        return slot

            if slot.date.start >= min_time:
                if matches_preferred_type:
                    last_diff = abs(diff)
                    last_slot = slot

        raise NoSlotsError("No acceptable slots found")
