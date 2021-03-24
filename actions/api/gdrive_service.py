# -*- coding: utf-8 -*-
import logging

import gspread
import tempfile
from oauth2client.service_account import ServiceAccountCredentials
from gspread.models import Spreadsheet
from typing import List, Text, Optional

from actions import config

logger = logging.getLogger(__name__)


class GDriveService:
    """Service to write to a spreadsheet in google drive."""

    # Name of the spreadsheet
    SPREADSHEET_NAME = "Qualify Inbounds"

    # Worksheet in spreadsheet where the new address change entries should be stored in
    WORKSHEET_NAME = "demobot"

    def __init__(self, gdrive_credentials_json: Text = config.gdrive_credentials):
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        # authenticate the service with a json key
        with tempfile.NamedTemporaryFile(suffix="_credentials.json", mode="w") as f:
            f.write(gdrive_credentials_json)
            f.flush()
            self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                f.name, scopes=scopes
            )

    def request_spreadsheet(self, spreadsheet_name: Text) -> Optional[Spreadsheet]:
        # fetch a specific spreadsheet
        logging.debug("Refreshing auth")
        try:
            return gspread.authorize(self.credentials).open(spreadsheet_name)
        except Exception as e:
            logging.error(
                "Failed to create google spreadsheet connection. %s", e, exc_info=True
            )
            return None

    def store_data(self, data: List[Text]) -> None:
        """Add a single new row to the worksheet containing the user's
        information"""
        self.append_row(self.SPREADSHEET_NAME, self.WORKSHEET_NAME, data)

    def append_row(
        self, spreadsheet_name: Text, worksheet_name: Text, row_values: List[Text]
    ) -> None:
        # add a row to the spreadsheet
        spreadsheet = self.request_spreadsheet(spreadsheet_name)
        if spreadsheet:
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                if worksheet:
                    worksheet.append_row(row_values)
            except Exception as e:
                logging.error(
                    f"Failed to write row to gdocs. Sheet {spreadsheet_name}/{worksheet_name}. "
                    f"Error: {e}",
                    exc_info=True,
                )
