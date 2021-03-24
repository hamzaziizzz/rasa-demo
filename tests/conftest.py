# -*- coding: utf-8 -*-
"""
You can create a file called `.env` in the root of the repo, containing your local env vars.
"""
from dotenv import load_dotenv

# Load environment variables
# needs to happen before anything else (to properly instantiate constants)

load_dotenv(verbose=True)

import os
import pytest
import json
import requests
import uuid
from typing import Text, List, Dict, Tuple, Any, Iterator
import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker
from mailchimp3.mailchimpclient import MailChimpError
from mailchimp3 import MailChimp
from gspread.models import Worksheet

from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker
from rasa.shared.core.domain import Domain

from actions import config
from actions.api.rasaxapi import RasaXAPI
from actions.api.mailchimp import MailChimpAPI
from actions.api.gdrive_service import GDriveService


TRACKER_DB_URL = os.environ.setdefault("TRACKER_DB_URL", "postgresql:///tracker")


@pytest.fixture
def db_session() -> Session:
    engine = sa.create_engine(TRACKER_DB_URL)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def tracker() -> Tracker:
    """Load a tracker object"""
    with open("tests/data/initial_tracker.json") as json_file:
        tracker = Tracker.from_dict(json.load(json_file))
    return tracker


@pytest.fixture
def dispatcher() -> CollectingDispatcher:
    """Create a clean dispatcher"""
    return CollectingDispatcher()


@pytest.fixture
def domain() -> Dict[Text, Any]:
    """Load the domain and return it as a dictionary"""
    domain = Domain.load("domain.yml")
    return domain.as_dict()


@pytest.fixture
def rasa_x_conversation_endpoint() -> Text:
    """Return the Rasa X conversations endpoint"""
    rasax = RasaXAPI()
    return f"{rasax.schema}://{rasax.host}/api/conversations"


@pytest.fixture
def rasa_x_auth_header() -> Dict[Text, Text]:
    """Get authentication header for Rasa X"""
    rasax = RasaXAPI()
    return rasax.get_auth_header()


@pytest.fixture
def rasa_x_convo(
    rasa_x_conversation_endpoint: Text,
    rasa_x_auth_header: Dict,
    tracker: Tracker,
    db_session: Session,
) -> Iterator[None]:
    """Create an empty conversation in Rasa X"""
    del_endpoint = f"{rasa_x_conversation_endpoint}/{tracker.sender_id}"
    # delete the conversation in case it already exists due to an improperly exited test
    requests.delete(del_endpoint, headers=rasa_x_auth_header)

    data = {"sender_id": tracker.sender_id}
    requests.post(rasa_x_conversation_endpoint, json=data, headers=rasa_x_auth_header)

    yield

    requests.delete(del_endpoint, headers=rasa_x_auth_header)
    db_session.execute(f"DELETE FROM events WHERE sender_id = '{tracker.sender_id}'")
    db_session.commit()


@pytest.fixture
def mailchimp() -> Tuple[Text, "MailChimp"]:
    """Create a user who is not already subscribed to the newsletter"""
    # use a random email to avoid mailchimp errors due to too many
    # attempted signups by the same email address
    email = f"{uuid.uuid4().hex}@rasa.com"
    client = MailChimpAPI(config.mailchimp_api_key)
    # try to delete user in case of an improperly exited test
    try:
        client.delete_user(config.mailchimp_list, email)
    except MailChimpError:
        pass

    yield (email, client)

    client.delete_user(config.mailchimp_list, email)


@pytest.fixture
def mailchimp_new_email(mailchimp: Tuple[Text, "MailChimp"]) -> Iterator[Text]:
    """Create a user who is not already subscribed to the newsletter"""
    email = mailchimp[0]

    yield email


@pytest.fixture
def mailchimp_unsubscribed_email(mailchimp: Tuple[Text, "MailChimp"]) -> Iterator[Text]:
    """Create a user who is not already subscribed to the newsletter"""
    email = mailchimp[0]
    client = mailchimp[1]
    # add user to db
    client.subscribe_user(config.mailchimp_list, email)
    # set user as unsubscribed
    client.unsubscribe_user(config.mailchimp_list, email)

    yield email


@pytest.fixture
def mailchimp_subscribed_email(mailchimp: Tuple[Text, "MailChimp"]) -> Iterator[Text]:
    """Create a user who is already subscribed to the newsletter"""
    email = mailchimp[0]
    client = mailchimp[1]
    client.subscribe_user(config.mailchimp_list, email)

    yield email


@pytest.fixture
def gdrive(mocker) -> Tuple[GDriveService, "Worksheet"]:
    """Clear test worksheet to allow asserting contents of rows"""
    spreadsheet_name = "SaraUnitTestingSalesSheet"
    worksheet_name = "demobot_testing"
    mocker.patch.object(
        GDriveService, "SPREADSHEET_NAME", spreadsheet_name,
    )
    mocker.patch.object(
        GDriveService, "WORKSHEET_NAME", worksheet_name,
    )

    gdrive_client = GDriveService()
    spreadsheet = gdrive_client.request_spreadsheet(gdrive_client.SPREADSHEET_NAME)
    worksheet = spreadsheet.worksheet(worksheet_name)
    worksheet.resize(rows=1)

    yield (gdrive_client, worksheet)

    worksheet.resize(rows=1)
