from typing import List, Optional
from datetime import datetime, date

from pydantic import BaseModel, validator, ValidationError


class ResyConfig(BaseModel):
    api_key: str
    token: str
    payment_method_id: Optional[int]
    email: str
    password: str

    def get_authorization(self) -> str:
        return f'ResyAPI api_key="{self.api_key}"'


class ReservationRequest(BaseModel):
    venue_id: str
    party_size: int
    ideal_date: date
    ideal_hour: int
    ideal_minute: int
    window_hours: int
    prefer_early: bool
    preferred_type: Optional[str]


class RepeatedReservationRequest(BaseModel):
    """
    instead of specifying a date, specify the number of days from now
    """

    venue_id: str
    party_size: int
    days_from_now: int
    ideal_hour: int
    ideal_minute: int
    window_hours: int
    prefer_early: bool
    preferred_type: Optional[str]


class ReservationRetriesConfig(BaseModel):
    seconds_between_retries: float
    retry_duration: float


class TimedReservationRequest(BaseModel):
    reservation_request: ReservationRequest
    expected_drop_hour: int
    expected_drop_minute: int


class TimedRepeatedReservationRequest(BaseModel):
    reservation_request: RepeatedReservationRequest
    expected_drop_hour: int
    expected_drop_minute: int


class AuthRequestBody(BaseModel):
    email: str
    password: str


class PaymentMethod(BaseModel):
    id: int


class AuthResponseBody(BaseModel):
    payment_methods: List[PaymentMethod]
    token: str


class FindRequestBody(BaseModel):
    venue_id: Optional[str]
    party_size: int
    day: str
    lat: str = "0"
    long: str = "0"

    @validator("day")
    def validate_day(cls, day: str) -> str:
        try:
            datetime.strptime(day, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Day must be in isoformat", FindRequestBody)

        return day


class SlotConfig(BaseModel):
    id: str
    type: str
    token: str


class SlotDate(BaseModel):
    start: datetime
    end: datetime


class Slot(BaseModel):
    config: SlotConfig
    date: SlotDate


class Venue(BaseModel):
    slots: List[Slot]


class Results(BaseModel):
    venues: List[Venue]


class FindResponseBody(BaseModel):
    results: Results


class DetailsRequestBody(BaseModel):
    config_id: str
    party_size: int
    day: str


class BookToken(BaseModel):
    date_expires: datetime
    value: str


class DetailsResponseBody(BaseModel):
    book_token: BookToken


class BookRequestBody(BaseModel):
    book_token: str
    struct_payment_method: PaymentMethod
    source_id: str = "resy.com-venue-details"


class BookResponseBody(BaseModel):
    resy_token: str
