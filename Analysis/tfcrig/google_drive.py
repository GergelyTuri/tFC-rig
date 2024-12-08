"""Module for loading data from Google Spreadsheet on Google drive."""

import os

import gspread
import pandas as pd
from dotenv import load_dotenv
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables from .env file
load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


class GoogleDrive:
    """A class to interact with Google Drive and Google Sheets using a service account.
    Attributes:
        scopes (list): The scopes required for accessing Google Sheets.
        credentials (ServiceAccountCredentials): The credentials for the service account.
        client (gspread.Client): The gspread client authorized with the service account credentials.
    Methods:
        __init__(service_account_file: str = SERVICE_ACCOUNT_FILE):
            Initializes the GoogleDrive instance with the provided service account file.
        get_sheet_as_df(sheet_id: str, sheet_name: str = "Sheet1") -> pandas.DataFrame:
    """

    def __init__(self, service_account_file: str = None):
        if service_account_file is None:
            service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
        self.scopes = SCOPES
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            service_account_file, self.scopes
        )
        self.client = gspread.authorize(self.credentials)

    def get_sheet_as_df(
        self, sheet_id: str, sheet_name: str = "Sheet1"
    ) -> pd.DataFrame:
        """
        Retrieves a Google Sheets worksheet as a pandas DataFrame.

        Args:
            sheet_id (str): The unique identifier of the Google Sheets document.
            sheet_name (str, optional): The name of the worksheet to retrieve. Defaults to "Sheet1".

        Returns:
            pandas.DataFrame: The worksheet data as a DataFrame.
        """
        sheet = self.client.open_by_key(sheet_id)
        worksheet = sheet.worksheet(sheet_name)
        df = get_as_dataframe(worksheet)
        return df
