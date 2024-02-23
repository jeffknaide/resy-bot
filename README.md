# Resy-Bot

Resy exposes a number of API endpoints for making reservations,
these can be investigated by taking a look at the `api.resy.com`
calls from the network tab. We can have some fun making automated
calls to those endpoints right when reservations become available

## Running

### Dependencies

Primary dependencies are pydantic and requests.
pydantic is used for serializing/deserializing requests/responses from Resy.

This project's dependencies are managed by poetry, so (assuming you have poetry installed) you can just install as easily as
`poetry install`.

### Local Configuration

The primary pieces of configuration for local execution are
defined in the `ResyConfig` and `TimedReservationRequest`
pydantic models in `resy_bot/models.py`.


#### ResyConfig

`ResyConfig` specifies credentials for personal Resy accounts.
Users should create a `credentials.json` file formatted as:
```json
{
  "api_key": "<api-key>",
  "token": "<api-token>",
  "payment_method_id": <payment-method>,
  "email": "<email>",
  "password": "<password>"
}
```

These values can be found in requests made in the Network tab.
- `api_key` can be found in the request headers under the
key `Authorization` in the format `ResyAPI api_key="<api-key>"`
- `token` can be found  in the request headers under the
key `X-Resy-Auth-Token`
- `payment_method_id` can be found in the request body to the endpoint
`/3/book`


#### TimedReservationRequest

In order to make a reservation right as it drops, a JSON
`TimedReservationRequest` must be created, see the following example
JSON:

```json
{
"reservation_request": {
  "party_size": 4,
  "venue_id": 12345,
  "window_hours": 1,
  "prefer_early": false,
  "ideal_date": "2023-03-30",
  "days_in_advance": 14,
  "ideal_hour": 19,
  "ideal_minute": 30,
  "preferred_type": "Dining Room"
},
  "expected_drop_hour": "10",
  "expected_drop_minute": "0"
}
```

These fields are mostly determined by the user:
- `party_size` is the number of members in the party
- `venue_id` is another field taken from communication in the
Network tab. This can be found as a URL param in requests to
the `/2/config` endpoint when navigating to the desired restaurant page
- `window_hours` is the number of hours before & after
the ideal hour/minute you are interested in
- `prefer_early` determines whether the earlier slot is selected when
2 time slots equidistant fom ideal hour/minute
- `ideal_date` is the date to search. This should not be provided if `days_in_advance` is used
- `days_in_advance` is the number of days from _now_ that the reservation becomes available. This should not be provided if `ideal_date` is used
- `ideal_hour` defines the hour field of the ideal timeslot
- `ideal_minute` defines the minute field of the ideal timeslot
- `preferred_type` is an optional field defining the type of seating
desired. If provided, Resy-Bot will _only_ search for that seating
type
- `expected_drop_hour` defines the hour field to of datetime
to start searching for slots
- `expected_drop_minute` defines the minute field to of datetime
to start searching for slots


### Command Line Execution

This application can be run from the command line. To do so,
the command should be formatted as

`poetry run python main.py <path/to/credentials.json> <path/to/reservation/request.json>`

From here, the application will wait until the time specified by
`expected_drop_hour` and `expected_drop_minute` to begin searching
for available timeslots.

### Notes
- test for local dev curl -X POST -H "Content-Type: application/json" -d '{"id":"7c9be457bc686964710ac0e219b54cc1","received_at":"2024-02-13 15:14:29","received_at_timestamp":1707837269,"received_at_iso8601":"2024-02-13T15:14:29+00:00","processed_at":"2024-02-13 15:29:07","processed_at_timestamp":1707838147,"processed_at_iso8601":"2024-02-13T15:29:07+00:00","available_table":"Minetta Tavern\n\n| Tuesday, Nov 30 at 7:00pm\n\n| Party of 2"}' http://localhost:3000/table-notification

# Install on heroku
## Install buildpacks
```
heroku buildpacks:clear
heroku buildpacks:add https://github.com/moneymeets/python-poetry-buildpack.git
heroku buildpacks:add heroku/python
```