from datetime import datetime, timedelta

import pytest

from resy_bot.errors import NoSlotsError
from resy_bot.selectors import SimpleSelector

from tests.factories import ReservationRequestFactory, SlotFactory


def test_simple_selector_select_exact_match():
    request = ReservationRequestFactory.create()
    slots = SlotFactory.create_batch(5)

    ideal_start_dt = datetime(
        year=request.ideal_date.year,
        month=request.ideal_date.month,
        day=request.ideal_date.day,
        hour=request.ideal_hour,
        minute=request.ideal_minute,
    )

    correct_slot = SlotFactory.create(
        date__start=ideal_start_dt,
        config__type=request.preferred_type
    )

    slots.append(correct_slot)

    sorted_slots = sorted(slots, key=lambda x: x.date.start)

    selector = SimpleSelector()
    best_slot = selector.select(sorted_slots, request)

    assert best_slot == correct_slot


def test_simple_selector_select_no_preferred_type():
    request = ReservationRequestFactory.create(preferred_type=None)
    slots = SlotFactory.create_batch(5)

    ideal_start_dt = datetime(
        year=request.ideal_date.year,
        month=request.ideal_date.month,
        day=request.ideal_date.day,
        hour=request.ideal_hour,
        minute=request.ideal_minute,
    )

    correct_slot = SlotFactory.create(
        date__start=ideal_start_dt,
    )

    slots.append(correct_slot)

    sorted_slots = sorted(slots, key=lambda x: x.date.start)

    selector = SimpleSelector()
    best_slot = selector.select(sorted_slots, request)

    assert best_slot == correct_slot


def test_simple_selector_select_time_match_without_preferred_type_match():
    request = ReservationRequestFactory.create()
    slots = SlotFactory.create_batch(5)

    ideal_start_dt = datetime(
        year=request.ideal_date.year,
        month=request.ideal_date.month,
        day=request.ideal_date.day,
        hour=request.ideal_hour,
        minute=request.ideal_minute,
    )

    correct_slot = SlotFactory.create(
        date__start=ideal_start_dt,
    )

    slots.append(correct_slot)

    sorted_slots = sorted(slots, key=lambda x: x.date.start)

    selector = SimpleSelector()

    with pytest.raises(NoSlotsError):
        selector.select(sorted_slots, request)


def test_simple_selector_select_early_if_equally_off():
    request = ReservationRequestFactory.create(
        preferred_type=None,
        prefer_early=True,
        window_hours=1
    )
    slots = SlotFactory.create_batch(5)

    ideal_start_dt = datetime(
        year=request.ideal_date.year,
        month=request.ideal_date.month,
        day=request.ideal_date.day,
        hour=request.ideal_hour,
        minute=request.ideal_minute,
    )
    td = timedelta(hours=0.5)

    early_slot = SlotFactory.create(
        date__start=ideal_start_dt - td,
    )

    later_slot = SlotFactory.create(
        date__start=ideal_start_dt + td,
    )

    slots.extend([early_slot, later_slot])

    sorted_slots = sorted(slots, key=lambda x: x.date.start)

    selector = SimpleSelector()
    best_slot = selector.select(sorted_slots, request)

    assert best_slot == early_slot


def test_simple_selector_select_later_if_equally_off():
    request = ReservationRequestFactory.create(
        preferred_type=None,
        prefer_early=False,
        window_hours=1
    )
    slots = SlotFactory.create_batch(5)

    ideal_start_dt = datetime(
        year=request.ideal_date.year,
        month=request.ideal_date.month,
        day=request.ideal_date.day,
        hour=request.ideal_hour,
        minute=request.ideal_minute,
    )
    td = timedelta(hours=0.5)

    early_slot = SlotFactory.create(
        date__start=ideal_start_dt - td,
    )

    later_slot = SlotFactory.create(
        date__start=ideal_start_dt + td,
    )

    slots.extend([early_slot, later_slot])

    sorted_slots = sorted(slots, key=lambda x: x.date.start)

    selector = SimpleSelector()
    best_slot = selector.select(sorted_slots, request)

    assert best_slot == later_slot


def test_simple_selector_no_slots_in_window():
    request = ReservationRequestFactory.create(
        preferred_type=None,
        prefer_early=False,
        window_hours=1
    )
    slots = SlotFactory.create_batch(5)

    ideal_start_dt = datetime(
        year=request.ideal_date.year,
        month=request.ideal_date.month,
        day=request.ideal_date.day,
        hour=request.ideal_hour,
        minute=request.ideal_minute,
    )
    td = timedelta(hours=1.5)

    too_late_slot = SlotFactory.create(
        date__start=ideal_start_dt + td,
    )

    selector = SimpleSelector()

    with pytest.raises(NoSlotsError):
        selector.select([too_late_slot], request)
