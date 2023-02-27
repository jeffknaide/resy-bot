import pytest
from requests import HTTPError
from unittest.mock import MagicMock
from requests import Session

from resy_bot.api_access import build_session, ResyApiAccess
from tests.factories import (
    ResyConfigFactory,
    AuthRequestBodyFactory,
    AuthResponseBodyFactory,
    FindRequestBodyFactory,
    FindResponseBodyFactory,
    DetailsResponseBodyFactory,
    DetailsRequestBodyFactory,
    BookRequestBodyFactory,
    BookResponseBodyFactory,
)


def test_build_session():
    config = ResyConfigFactory.create()
    session = build_session(config)

    assert isinstance(session, Session)
    assert session.headers["Authorization"] == f'ResyAPI api_key="{config.api_key}"'
    assert session.headers["X-Resy-Auth-Token"] == config.token


def test_build_api_access():
    config = ResyConfigFactory.create()
    api_access = ResyApiAccess.build(config)

    assert isinstance(api_access, ResyApiAccess)
    assert isinstance(api_access.session, Session)
    assert (
        api_access.session.headers["Authorization"]
        == f'ResyAPI api_key="{config.api_key}"'
    )
    assert api_access.session.headers["X-Resy-Auth-Token"] == config.token


def test_auth():
    session = MagicMock()
    resp_mock = MagicMock()
    expected_resp = AuthResponseBodyFactory.create()
    resp_mock.json.return_value = expected_resp.dict()
    session.post.return_value = resp_mock
    api_access = ResyApiAccess(session)

    body = AuthRequestBodyFactory.create()

    resp = api_access.auth(body)

    session.post.assert_called_once_with(
        "https://api.resy.com/3/auth/password",
        data=body.dict(),
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert resp == expected_resp


def test_bad_auth():
    session = MagicMock()
    resp_mock = MagicMock()
    resp_mock.ok = False
    session.post.return_value = resp_mock

    api_access = ResyApiAccess(session)

    body = AuthRequestBodyFactory.create()

    with pytest.raises(HTTPError):
        api_access.auth(body)


def test_find_booking_slots():
    expected_resp = FindResponseBodyFactory.create()

    session = MagicMock()
    resp_mock = MagicMock()

    resp_mock.json.return_value = expected_resp.dict()
    session.get.return_value = resp_mock

    api_access = ResyApiAccess(session)

    body = FindRequestBodyFactory.create()

    api_access.find_booking_slots(body)

    session.get.assert_called_once_with(
        "https://api.resy.com/4/find", params=body.dict()
    )


def test_find_booking_slots_bad_resp():
    session = MagicMock()
    resp_mock = MagicMock()
    resp_mock.ok = False
    session.get.return_value = resp_mock

    api_access = ResyApiAccess(session)

    body = FindRequestBodyFactory.create()

    with pytest.raises(HTTPError):
        api_access.find_booking_slots(body)


def test_get_booking_token():
    expected_resp = DetailsResponseBodyFactory.create()

    session = MagicMock()
    resp_mock = MagicMock()

    resp_mock.json.return_value = expected_resp.dict()
    session.get.return_value = resp_mock

    api_access = ResyApiAccess(session)

    body = DetailsRequestBodyFactory.create()

    api_access.get_booking_token(body)

    session.get.assert_called_once_with(
        "https://api.resy.com/3/details", params=body.dict()
    )


def test_get_booking_token_bad_resp():
    session = MagicMock()
    resp_mock = MagicMock()
    resp_mock.ok = False
    session.get.return_value = resp_mock

    api_access = ResyApiAccess(session)

    body = DetailsRequestBodyFactory.create()

    with pytest.raises(HTTPError):
        api_access.get_booking_token(body)


def test_book_slot():
    expected_resp = BookResponseBodyFactory.create()

    session = MagicMock()
    resp_mock = MagicMock()

    resp_mock.json.return_value = expected_resp.dict()
    session.post.return_value = resp_mock

    api_access = ResyApiAccess(session)

    body = BookRequestBodyFactory.create()

    output = api_access.book_slot(body)

    payment_json = body.struct_payment_method.json()
    body_dict = body.dict()
    body_dict["struct_payment_method"] = payment_json

    session.post.assert_called_once_with(
        "https://api.resy.com/3/book",
        data=body_dict,
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert output == expected_resp.resy_token


def test_book_slot_bad_resp():
    session = MagicMock()
    resp_mock = MagicMock()
    resp_mock.ok = False
    session.post.return_value = resp_mock

    api_access = ResyApiAccess(session)

    body = BookRequestBodyFactory.create()

    with pytest.raises(HTTPError):
        api_access.book_slot(body)
