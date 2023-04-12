import logging
from typing import List, Iterable, Optional

from apiclient import discovery
from ratelimit import limits, sleep_and_retry

from gpeopleapiwrapper import auth
from gpeopleapiwrapper.base import fields_to_str
from gpeopleapiwrapper.groups import GroupField, GroupWrapper
from gpeopleapiwrapper.persons import PersonWrapper, PersonField

LOG = logging.getLogger(__name__)


class Client:
    """
    Implementation of a client for the Google Contacts API.
    While all other modules in this package provide structures or objects to be used with the api this class
    encapsulates the actual communication i.e. all calls to the Google Contacts API.
    This client
    - provides methods to conveniently fetch, create, and update contacts
    - provides methods to conveniently fetch, create, and update groups
    - provides methods to conveniently manage group assignments of contacts
    - handles the rate limits of the api

    """

    def __init__(self, api_client_secret: dict, credentials_store: auth.CredentialsStore = auth.NoCredentialsStore()):
        self.__service = discovery.build("people",
                                         "v1",
                                         credentials=auth.authorize(api_client_secret, credentials_store))

    @sleep_and_retry
    @limits(calls=7, period=5)
    def _check_read_limit(self):
        """
        Empty function to check for the limit "Read requests" (Contact Group Reads) to the Google Contacts API.

        The 'magic' is done by the annotations from the ratelimit package: The 'sleep_and_retry' annotation
        causes the current thread to sleep until the specified time period has elapsed and then retries this (empty)
        function.

        We need to obey this same read limit in multiple other functions, so we came up with this rather unusual usage
        of the ratelimit package: Every other function that reads from the Google Contacts API must call this
        (empty) function before the request.
        """
        return

    @sleep_and_retry
    @limits(calls=7, period=5)
    def _check_write_limit(self):
        """
        Empty function to check for the limit "Write requests" (Contact Deletes and Contact Group Writes) to the
        Google Contacts API.

        The 'magic' is done by the annotations from the ratelimit package: The 'sleep_and_retry' annotation
        causes the current thread to sleep until the specified time period has elapsed and then retries this (empty)
        function.

        We need to obey this same read limit in multiple other functions, so we came up with this rather unusual usage
        of the ratelimit package: Every other function that writes to the Google Contacts API must call this
        (empty) function before the request.
        """
        return

    @staticmethod
    def _wrap_persons(persons: Iterable[dict], field_mask: Iterable[PersonField]) -> List[PersonWrapper]:
        """
        Helper function to wrap a list of persons (as returned by the Google Contacts API) into a list of the wrapper
        classes :py:class:`persons.PersonWrapper` that encapsulate the persons.
        """
        return list(map(lambda p: PersonWrapper(p, field_mask), persons))

    def _fetch_connections_paged(self, field_mask: Iterable[PersonField], page_token=None) -> List[PersonWrapper]:
        """
        Internal function to handle paging with the api, i.e. recursively fetch all persons.
        """
        self._check_read_limit()
        page_results = self.__service.people().connections().list(
            resourceName="people/me",
            pageToken=page_token,
            pageSize=100,
            personFields=fields_to_str(field_mask)
        ).execute()

        page_connections = page_results.get("connections", [])
        if not page_connections or len(page_connections) == 0:
            return list()

        if "nextPageToken" in page_results and page_results["nextPageToken"]:
            return Client._wrap_persons(page_connections, field_mask) \
                + self._fetch_connections_paged(field_mask, page_token=page_results["nextPageToken"])

        return Client._wrap_persons(page_connections, field_mask)

    def get_all_persons(self, field_mask: Iterable[PersonField]) -> List[PersonWrapper]:
        """
        Fetch all persons from the Google Contacts API and return them as a list of PersonWrapper objects.
        Each :py:class:`persons.PersonWrapper` will only contain the attributes specified in the field_mask parameter,
        cf. https://developers.google.com/people/api/rest/v1/people.connections/list#query-parameters. In turn,
        the returned PersonWrappers can only be used to change the attributes specified in the field_mask parameter.
        This method will automatically handle paging and return all persons.
        """
        return self._fetch_connections_paged(field_mask)

    def create_person(self, unstructured_name: str, return_field_mask: Iterable[PersonField]) -> PersonWrapper:
        """
        Create a new person with the given unstructured name and return the newly created person as a PersonWrapper.
        The returned :py:class:`persons.PersonWrapper` will only contain the attributes specified in the field_mask
        parameter and, in turn, can only be used to change the attributes specified in the field_mask parameter.
        Be aware that the api handles all modifying requests in an eventually consistent manner, i.e. a subsequent
        update of the person returned on create may fail with a "person does not exist" error for a while.
        Api documentation: https://developers.google.com/people/api/rest/v1/people.connections/list
        """
        self._check_write_limit()
        created_person = self.__service.people().createContact(
            personFields=fields_to_str(return_field_mask),
            body={
                PersonField.names.value: [{
                    "unstructuredName": unstructured_name,
                }]
            }
        ).execute()
        return PersonWrapper(created_person, return_field_mask)

    def update_person(self, person: PersonWrapper, return_field_mask: Iterable[PersonField]) -> PersonWrapper:
        """
        Updates an existing person according to the given PersonWrapper and returns the updated person object.
        The returned :py:class:`persons.PersonWrapper` will only contain the attributes specified in the field_mask
        parameter and, in turn, can only be used to change the attributes specified in the field_mask parameter.
        Of course, you may update certain attributes of a person (if you have retrieved the person with the appropriate
        field_mask) and have the api return the same person object with a different field_mask to change other
        attributes subsequently.
        Api documentation: https://developers.google.com/people/api/rest/v1/people/createContact
        """
        self._check_write_limit()
        updated = self.__service.people().updateContact(
            resourceName=person.resource_name,
            updatePersonFields=fields_to_str(person.field_mask),
            personFields=fields_to_str(return_field_mask),
            body=person.model_copy()
        ).execute()
        return PersonWrapper(updated, return_field_mask)

    @staticmethod
    def _wrap_groups(groups: List[dict], field_mask: Iterable[GroupField]) -> List[GroupWrapper]:
        """
        Helper function to wrap a list of groups (as returned by the Google Contacts API) into a list of the wrapper
        classes :py:class:`groups.GroupWrapper` that encapsulate the groups
        """
        return list(map(lambda p: GroupWrapper(p, field_mask), groups))

    def _fetch_groups_paged(self, field_mask: Iterable[GroupField], page_token=None) -> List[GroupWrapper]:
        """
        Internal function to handle paging with the api, i.e. recursively fetch all groups.
        """
        self._check_read_limit()
        page_results = self.__service.contactGroups().list(
            pageToken=page_token,
            pageSize=100,
            groupFields=fields_to_str(field_mask)
        ).execute()

        page_groups = page_results.get("contactGroups", [])
        if not page_groups or len(page_groups) == 0:
            return list()

        if "nextPageToken" in page_results and page_results["nextPageToken"]:
            return Client._wrap_groups(page_groups, field_mask) \
                + self._fetch_groups_paged(field_mask, page_token=page_results["nextPageToken"])

        return Client._wrap_groups(page_groups, field_mask)

    def get_all_groups(self, field_mask: Iterable[GroupField]) -> List[GroupWrapper]:
        """
        Fetch all groups from the Google Contacts API and return them as a list of GroupWrapper objects.
        Each :py:class:`groups.GroupWrapper` will only contain the attributes specified in the field_mask parameter,
        cf. https://developers.google.com/people/api/rest/v1/contactGroups/list#query-parameters. In turn,
        the returned GroupWrappers can only be used to change the attributes specified in the field_mask parameter.
        This method will automatically handle paging and return all groups.
        """
        return self._fetch_groups_paged(field_mask)

    def get_first_group_by_name(self,
                                group_name: str,
                                field_mask: Iterable[GroupField] = None,
                                member_limit: int = 0) -> Optional[GroupWrapper]:
        """
        Retrieves the first group with the given name from the Google Contacts API and returns it as a
        :py:class:`groups.GroupWrapper`.
        In most cases there will only be one group with a given name, but the api does not enforce this. Therefor
        we return the first group with the given name. If no group with the given name exists, None is returned.
        """
        existing_groups = list(filter(lambda g: g.name == group_name, self.get_all_groups([GroupField.name])))
        if not existing_groups or len(existing_groups) == 0:
            return None

        # group with name exists. now we can use the group name to retrieve the full info
        self._check_read_limit()
        group_details = self.__service.contactGroups().get(
            resourceName=existing_groups[0].resource_name,
            maxMembers=member_limit,
            groupFields=fields_to_str(field_mask)
        ).execute()

        return GroupWrapper(group_details, field_mask)

    def get_first_or_create_group(self, group_name: str, return_field_mask: Iterable[GroupField]) -> GroupWrapper:
        """
        Retrieves the first group with the given name from the Google Contacts API and returns it as a
        :py:class:`groups.GroupWrapper`. If no group with the given name exists the group is created.
        In most cases there will only be one group with a given name, but the api does not enforce this. Therefor
        we return the first group with the given name.
        """
        existing_group = self.get_first_group_by_name(group_name, return_field_mask)
        if existing_group:
            return existing_group

        self._check_write_limit()
        created_group = self.__service.contactGroups().create(
            body={
                "contactGroup": {
                    GroupField.name.value: group_name
                },
                "readGroupFields": fields_to_str(return_field_mask)
            }
        ).execute()
        return GroupWrapper(created_group, return_field_mask)

    def add_member_to_group(self, group_name: str, person: PersonWrapper):
        """
        Adds the given person to the group with the given name. If no group with the given name exists, it is created.
        """
        target_group = self.get_first_or_create_group(group_name, [GroupField.name])

        self._check_write_limit()
        self.__service.contactGroups().members().modify(
            resourceName=target_group.resource_name,
            body={
                "resourceNamesToAdd": [person.resource_name]
            }).execute()

    def remove_member_from_group(self, group_name: str, person: PersonWrapper):
        """
        Removes the given person from the group with the given name. If the group does not exist, nothing happens.
        """
        target_group = self.get_first_group_by_name(group_name, [GroupField.name])
        if not target_group:
            return

        self._check_write_limit()
        self.__service.contactGroups().members().modify(
            resourceName=target_group.resource_name,
            body={
                "resourceNamesToRemove": [person.resource_name]
            }).execute()
