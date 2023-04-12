from copy import deepcopy
from enum import Enum
from typing import Iterable, List, TypeVar, Generic, Optional, Callable

FIELD_RESOURCE_NAME = "resourceName"

FieldT = TypeVar("FieldT", bound=Enum)  # Available fields of the model that is wrapped by the ModelWrapper


class FieldNotInMaskError(Exception):
    """
    Exception that is raised if reading or modifying a field is attempted although this field is not contained in
    the underlying model of a ModelWrapper.

    When requesting an object (person, group, ..) from the Google People API one has to provide the needed fields as a
    list parameter. In turn, only the properties of the object are returned that are contained in this field mask.
    While using the returned object one should neither read nor modify the properties that are not contained in the
    underlying model of the wrapper.
    """

    def __init__(self, field: FieldT, field_mask: Iterable[FieldT]):
        super().__init__(f"Field {field} not in current mask {fields_to_str(field_mask)}")


class ModelWrapper(Generic[FieldT]):
    """
    Base class for all top level objects (e.g. person, group) returned by the client from the Google People API.

    The ModelWrapper or, more specific, all subclasses derived (e.g. :py:class:`persons.PersonWrapper`,
    :py:class:`groups.GroupWrapper`) wrap the dictionary that is returned from the API. The specific ModelWrappers
    then provide accessors to the different properties.
    With the Google People API an object is always retrieved with respect to a field mask that selects the attributes
    that are retrieved for a certain object. Attributes that are not requested by the field mask are not contained in
    the model. The ModelWrapper factors the FieldMask in and prohibits access to attributes that were not requested
    and, in turn, not received from the API.
    """

    def __init__(self, model: dict, field_mask: Iterable[FieldT]):
        self.__model = deepcopy(model)
        self.__original_model = deepcopy(model)
        self.__field_mask = field_mask

    def __str__(self) -> str:
        return str(self.__model)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[" + \
            f"fields=[{fields_to_str(self.__field_mask)}," + \
            f"model={self.__model}," + \
            f"original={self.__original_model}]"

    def _model_field(self, field: FieldT) -> Optional:
        """
        Returns the value of the given field from the underlying model object. If the field is not contained in the
        model dict retrieved from the api None is returned. If the field was not requested from the api and therefor
        not contained in the field mask a FieldNotInMaskError is raised.
        """
        if field not in self.__field_mask:
            raise FieldNotInMaskError(field, self.__field_mask)
        return self.__model.get(field.value, None)

    def _creation_callback(self, field: FieldT, creation_value) -> Callable:
        """
        Creates a function that can be called to create a new field in the underlying model object if it does not exist
        yet. This is mainly used for list fields like addresses or phone numbers. If there is no list item present for
        the list field (e.g. as the person has no addresses yet) the list attribute itself is missing in the model dict
        retrieved from the api as well. To add a list item (e.g. a new address) we need to create the list attribute
        first. As the model dict is a private attribute of the ModelWrapper we need to create a callback that is used
        to create the initial empty list.
        """
        if field not in self.__field_mask:
            raise FieldNotInMaskError(field, self.__field_mask)

        def callback():
            if field.value not in self.__model:
                self.__model[field.value] = creation_value
            return self.__model[field.value]

        return callback

    @property
    def resource_name(self) -> str:
        return self.__model[FIELD_RESOURCE_NAME]

    @property
    def field_mask(self) -> List[FieldT]:
        return list(self.__field_mask)

    def model_copy(self) -> dict:
        """
        Returns a deep copy of the underlying model dict.
        """
        return deepcopy(self.__model)

    def has_changes(self) -> bool:
        """
        Returns true if the underlying model dict has changed from the original version.
        """
        return self.__model != self.__original_model


def fields_to_str(fields: Iterable[FieldT]) -> str:
    """
    Helper function to convert the field mask to a string representation.
    """
    return ",".join([str(f.value) for f in fields])
