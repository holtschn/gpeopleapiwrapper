from enum import Enum
from typing import Optional

from gpeopleapiwrapper.base import ModelWrapper


class GroupField(Enum):
    """
    Enumeration of all fields available for a Group object from the API.
    """
    client_data = "clientData"
    group_type = "groupType"
    member_count = "memberCount"
    metadata = "metadata"
    name = "name"


class GroupWrapper(ModelWrapper[GroupField]):

    @property
    def name(self) -> Optional[str]:
        return self._model_field(GroupField.name)

    @property
    def group_type(self) -> Optional[str]:
        return self._model_field(GroupField.group_type)

    def has_member(self, person: ModelWrapper) -> bool:
        if "memberResourceNames" not in self.model_copy():  # seems to occur with system groups
            return False
        member_resource_names = self.model_copy()["memberResourceNames"]
        if member_resource_names:
            return person.resource_name in member_resource_names
        return False
