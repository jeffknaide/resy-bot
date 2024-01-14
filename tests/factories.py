import factory
from datetime import date, datetime
from random import randint

from resy_bot.models import (
    ResyConfig,
    ReservationRequest,
    ReservationRetriesConfig,
    TimedReservationRequest,
    Slot,
    SlotConfig,
    SlotDate,
    BookToken,
    DetailsRequestBody,
    DetailsResponseBody,
    AuthRequestBody,
    PaymentMethod,
    AuthResponseBody,
    FindRequestBody,
    Venue,
    Results,
    FindResponseBody,
    BookRequestBody,
    BookResponseBody,
)


class ReservationRequestFactory(factory.Factory):
    class Meta:
        model = ReservationRequest

    venue_id = factory.Faker("bs")
    party_size = factory.Faker("random_int")
    ideal_date = factory.LazyFunction(lambda: date.today())
    ideal_hour = factory.LazyFunction(lambda: randint(1, 23))
    ideal_minute = factory.LazyFunction(lambda: randint(0, 59))
    window_hours = factory.LazyFunction(lambda: randint(0, 4))
    prefer_early = factory.Faker("boolean")
    preferred_type = factory.Faker("bs")


class ReservationRequestDaysInAdvanceFactory(factory.Factory):
    class Meta:
        model = ReservationRequest

    venue_id = factory.Faker("bs")
    party_size = factory.Faker("random_int")
    days_in_advance = factory.Faker("random_int")
    ideal_hour = factory.LazyFunction(lambda: randint(1, 23))
    ideal_minute = factory.LazyFunction(lambda: randint(0, 59))
    window_hours = factory.LazyFunction(lambda: randint(0, 4))
    prefer_early = factory.Faker("boolean")
    preferred_type = factory.Faker("bs")


class ReservationRetriesConfigFactory(factory.Factory):
    class Meta:
        model = ReservationRetriesConfig

    seconds_between_retries = factory.LazyFunction(lambda: randint(0, 100) / 100)
    retry_duration = factory.LazyFunction(lambda: randint(1, 10))


class TimedReservationRequestFactory(factory.Factory):
    class Meta:
        model = TimedReservationRequest

    reservation_request = factory.SubFactory(ReservationRequestFactory)
    expected_drop_hour = factory.LazyFunction(lambda: randint(1, 24))
    expected_drop_minute = factory.LazyFunction(lambda: randint(0, 60))


class SlotConfigFactory(factory.Factory):
    class Meta:
        model = SlotConfig

    id = factory.Faker("uuid4")
    type = factory.Faker("bs")
    token = factory.Faker("uuid4")


class SlotDateFactory(factory.Factory):
    class Meta:
        model = SlotDate

    start = factory.Faker("date_time")
    end = factory.Faker("date_time")


class SlotFactory(factory.Factory):
    class Meta:
        model = Slot

    config = factory.SubFactory(SlotConfigFactory)
    date = factory.SubFactory(SlotDateFactory)


class ResyConfigFactory(factory.Factory):
    class Meta:
        model = ResyConfig

    api_key = factory.Faker("uuid4")
    token = factory.Faker("uuid4")
    payment_method_id = factory.Faker("random_int")
    email = factory.Faker("email")
    password = factory.Faker("password")


class BookTokenFactory(factory.Factory):
    class Meta:
        model = BookToken

    date_expires = factory.Faker("date_time")
    value = factory.Faker("uuid4")


class DetailsRequestBodyFactory(factory.Factory):
    class Meta:
        model = DetailsRequestBody

    config_id = factory.Faker("uuid4")
    party_size = factory.Faker("random_int")
    day = factory.LazyFunction(lambda: datetime.now().strftime("%Y-%m-%d"))


class DetailsResponseBodyFactory(factory.Factory):
    class Meta:
        model = DetailsResponseBody

    book_token = factory.SubFactory(BookTokenFactory)


class AuthRequestBodyFactory(factory.Factory):
    class Meta:
        model = AuthRequestBody

    email = factory.Faker("email")
    password = factory.Faker("password")


class PaymentMethodFactory(factory.Factory):
    class Meta:
        model = PaymentMethod

    id = factory.Faker("random_int")


class AuthResponseBodyFactory(factory.Factory):
    class Meta:
        model = AuthResponseBody

    payment_methods = factory.List([factory.SubFactory(PaymentMethodFactory)])
    token = factory.Faker("uuid4")


class FindRequestBodyFactory(factory.Factory):
    class Meta:
        model = FindRequestBody

    venue_id = factory.Faker("uuid4")
    party_size = factory.Faker("random_int")
    day = factory.LazyFunction(lambda: datetime.now().strftime("%Y-%m-%d"))


class VenueFactory(factory.Factory):
    class Meta:
        model = Venue

    slots = factory.List([factory.SubFactory(SlotFactory)])


class ResultsFactory(factory.Factory):
    class Meta:
        model = Results

    venues = factory.List([factory.SubFactory(VenueFactory)])


class FindResponseBodyFactory(factory.Factory):
    class Meta:
        model = FindResponseBody

    results = factory.SubFactory(ResultsFactory)


class BookRequestBodyFactory(factory.Factory):
    class Meta:
        model = BookRequestBody

    book_token = factory.Faker("uuid4")
    struct_payment_method = factory.SubFactory(PaymentMethodFactory)


class BookResponseBodyFactory(factory.Factory):
    class Meta:
        model = BookResponseBody

    resy_token = factory.Faker("uuid4")
