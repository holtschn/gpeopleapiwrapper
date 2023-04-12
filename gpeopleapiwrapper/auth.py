import logging
import os
import pickle
from abc import ABCMeta, abstractmethod
from typing import Optional

from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

LOG = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/contacts"]


class AuthorizationFailed(Exception):
    """
    Exception that is raised if no valid credentials can be acquired.
    """
    pass


class CredentialsStore(metaclass=ABCMeta):
    """
    Abstract base class of a credentials store.

    With the authorization flow we can acquire credentials by opening a browser window and manually authorizing the
    application. The credentials are valid for a certain amount of time, after which they expire. But, with the
    credentials object we also retrieve a refresh token that enables us to refresh the credentials with a request to
    the api, i.e. without the need to manually authorize via the browser flow again.

    The credentials store is responsible for storing and retrieving the credentials, e.g. from a file or a database.
    """

    @abstractmethod
    def store(self, credentials: Credentials):
        """
        Store the given credentials to a persistent storage depending on the implementation.
        """
        pass

    @abstractmethod
    def load(self) -> Optional[Credentials]:
        """
        Load credentials from a persistent storage depending on the implementation.
        """
        pass


class NoCredentialsStore(CredentialsStore):
    """
    Implementation of a :py:class:`CredentialsStore` that does not store or retrieve credentials.

    This is the default implementation of a credentials store. It is used if no credentials store is specified.
    This implementation always forces the authorization flow to be executed, i.e. it forces the user to manually
    authorize the application via the browser flow each time the application is started.
    """

    def store(self, credentials: Credentials):
        return

    def load(self) -> Optional[Credentials]:
        return None


class PickleFileCredentialsStore(CredentialsStore):
    """
    Implementation of a :py:class:`CredentialsStore` that stores the credentials to a pickle file.
    """

    def __init__(self, filename: str):
        self.__filename = filename

    def store(self, credentials: Credentials):
        with open(self.__filename, "wb") as creds_file:
            pickle.dump(credentials, creds_file)

    def load(self) -> Optional[Credentials]:
        if os.path.exists(self.__filename):
            with open(self.__filename, "rb") as creds_file:
                return pickle.load(creds_file)
        return None


def authorize(api_client_secret: dict, credentials_store: CredentialsStore) -> Credentials:
    """
    Central method for acquiring valid credentials for the Google People API.

    We try to load credentials from the given credentials store.
    If the persisted credentials are loadable but outdated or invalid we try to refresh these credentials with the
    refresh token.
    If we fail to load valid credentials or fail to refresh them, we acquire new ones by sending the user to the
    authorization flow.
    """

    creds = None
    # noinspection PyBroadException
    try:
        # we try to load credentials from the store
        creds = credentials_store.load()
    except:
        LOG.warning("Loading of credentials from store failed")

    # noinspection PyBroadException
    try:
        # if we retrieved credentials from the store that are invalid, i.e. expired, we try to refresh them
        if creds and not creds.valid and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    except:
        LOG.warning("Refreshing of credentials read from store failed")

    # noinspection PyBroadException
    try:
        # if we still have no valid credentials, we try to acquire them via the authorization flow
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_config(api_client_secret, SCOPES)
            creds = flow.run_local_server(port=0)
    except:
        # the flow failed, i.e. we cannot retrieve valid credentials – we have no choice but to abort
        raise AuthorizationFailed("Authorization flow failed")

    # now, we should have valid credentials, therfore we try to store them and return them
    if creds and creds.valid:
        # noinspection PyBroadException
        try:
            credentials_store.store(creds)
        except:
            LOG.warning("Writing of valid credentials to store failed")

        return creds

    # we failed to acquire valid credentials by any method – we have no choice but to abort
    raise AuthorizationFailed("Valid credentials could not be acquired")
