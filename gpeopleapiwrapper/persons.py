from abc import ABCMeta, abstractmethod
from datetime import date, datetime
from enum import Enum
from typing import List, Iterator, TypeVar, Generic, Optional, Callable, Tuple, Dict

from gpeopleapiwrapper.base import ModelWrapper

ARG_WRAPPER_CLASS = "wrapper_class"

FIELD_VALUE = "value"
FIELD_TYPE = "type"
FIELD_DATE = "date"
FIELD_FORMATTED_TYPE = "formattedType"


class PersonField(Enum):
    """
    Enumeration of all fields available for a Person object from the API.
    see https://developers.google.com/people/api/rest/v1/people/get#query-parameters for available personFields
    see https://developers.google.com/people/api/rest/v1/people#Person for the underlying model object of a Person.

    As this project is still in an early stage, not all fields are implemented. All non-implemented fields are
    commented out.
    """
    addresses = "addresses"
    # age_ranges = "ageRanges"
    # biographies = "biographies"
    birthdays = "birthdays"
    # calendar_urls = "calendarUrls"
    # client_data = "clientData"
    # cover_photos = "coverPhotos"
    email_addresses = "emailAddresses"
    events = "events"
    # external_ids = "externalIds"
    # genders = "genders"
    # im_clients = "imClients"
    # interests = "interests"
    # locales = "locales"
    # locations = "locations"
    # memberships = "memberships"
    # misc_keywords = "miscKeywords"
    names = "names"
    # nicknames = "nicknames"
    # occupations = "occupations"
    # organizations = "organizations"
    phone_numbers = "phoneNumbers"
    # photos = "photos"
    # relations = "relations"
    # sip_addresses = "sipAddresses"
    # skills = "skills"
    # urls = "urls"
    # user_defined = "userDefined"


class BaseWrapper:
    """
    Base class for all wrappers of attributes on the lowest (2nd) level in the large object tree of a Person object.

    The classes derived from this BaseWrapper are used e.g. for single addresses or single phone numbers while the
    lists of addresses and phone numbers that belong to a person are wrapped by :py:class:`persons.BaseListWrappers`.
    The model object that is wrapped by the :py:class:`persons.PersonWrapper` is delegated through the ListWrappers
    to this BaseWrapper class, i.e. in each step of delegation a smaller part of the model is passed by value
    (modifiable) to constitute the model part of the corresponding wrapper.

    Concrete classes are in some cases extended by mixin classes that provide access to common attributes like
    "value" and "type". With respect to the evaluation of multiple inheritance in python the BaseWrapper which is
    implementing the method _model_part should always come first in the class definition followed by the mixins. This
    ensures that the abstract properties of the mixin classes are overridden by the concrete implementation of the
    same method in this BaseWrapper.
    """

    def __init__(self, part_of_person_model: dict):
        self.__part_of_person_model = part_of_person_model

    @property
    def _model_part(self) -> dict:
        """
        Access to the underlying model that is part of the full model of a :py:class:PersonWrapper.
        """
        return self.__part_of_person_model


class DateValueVisitor(metaclass=ABCMeta):
    """
    Provides none-safe access to :py:class:DateValue.
    As DateValues come with different levels of  none-ness, i.e. year and month only (for contract expiration dates) or
    day and month only (for anniversaries), we provide a visitor to handle the different cases.
    """

    @abstractmethod
    def visit_full_date(self, full_date: date):
        pass

    @abstractmethod
    def visit_without_year(self, month: int, day: int):
        pass

    @abstractmethod
    def visit_year_only(self, year: int):
        pass

    @abstractmethod
    def visit_without_day(self, year: int, month: int):
        pass


class DateValue:
    """
    Representation of a date value in the Google People API.
    Mainly provides equality, access to the underlying possibly incomplete value by invitation of
    a :py:class:DateValueVisitor, and static factory methods.
    """

    def __init__(self, year: Optional[int], month: Optional[int], day: Optional[int]):
        self.__year = year
        self.__month = month
        self.__day = day

    def __str__(self):
        return f"DateValue({self.__year}, {self.__month}, {self.__day})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other) -> bool:

        if other is None:
            return False
        if not isinstance(other, DateValue):
            return False

        if self.__year is None and other.__year is not None:
            return False
        if self.__year is not None and other.__year is None:
            return False
        if self.__year != other.__year:
            return False

        if self.__month is None and other.__month is not None:
            return False
        if self.__month is not None and other.__month is None:
            return False
        if self.__month != other.__month:
            return False

        if self.__day is None and other.__day is not None:
            return False
        if self.__day is not None and other.__day is None:
            return False
        if self.__day != other.__day:
            return False

        return True

    def __hash__(self) -> int:
        return self.__day if self.__day else self.__year if self.__year else 0

    def visit_value(self, visitor: DateValueVisitor):
        if self.__year and self.__month and self.__day:
            visitor.visit_full_date(date(self.__year, self.__month, self.__day))
        elif self.__year and self.__month:
            visitor.visit_without_day(self.__year, self.__month)
        elif self.__month and self.__day:
            visitor.visit_without_year(self.__month, self.__day)
        elif self.__year:
            visitor.visit_year_only(self.__year)

    def google_value(self) -> Dict[str, int]:
        google_date = dict()
        google_date["year"] = self.__year if self.__year else 0
        google_date["month"] = self.__month if self.__month else 0
        google_date["day"] = self.__day if self.__day else 0
        return google_date

    @staticmethod
    def from_date(date_value: date) -> "DateValue":
        return DateValue(date_value.year, date_value.month, date_value.day)

    @staticmethod
    def from_datetime(datetime_value: datetime) -> "DateValue":
        return DateValue(datetime_value.year, datetime_value.month, datetime_value.day)

    @staticmethod
    def from_google(google_date: dict) -> "DateValue":
        year = google_date.get("year", None)
        if year is not None and year <= 0:
            year = None
        month = google_date.get("month", None)
        if month is not None and month <= 0:
            month = None
        day = google_date.get("day", None)
        if day is not None and day <= 0:
            day = None

        return DateValue(year, month, day)

    @staticmethod
    def from_full_date(year: int, month: int, day: int) -> "DateValue":
        return DateValue(year, month, day)

    @staticmethod
    def from_year_month(year: int, month: int) -> "DateValue":
        return DateValue(year, month, None)

    @staticmethod
    def from_month_day(month: int, day: int) -> "DateValue":
        return DateValue(None, month, day)

    @staticmethod
    def from_year_only(year: int) -> "DateValue":
        return DateValue(year, None, None)


class DateValueMixin:
    """
    Mixin class that provides accessors for the "date" attribute of the model object of a :py:class:BaseWrapper.
    Examples of Person fields with a date are Birthday and Event.
    """

    @property
    @abstractmethod
    def _model_part(self) -> dict:
        """
        Method definition that enforces the use of the DateValueMixin with a :py:class:BaseWrapper.
        """
        pass

    @property
    def date_value(self) -> DateValue:
        google_date = self._model_part.get(FIELD_DATE, None)
        return DateValue.from_google(google_date) if google_date else None

    @date_value.setter
    def date_value(self, date_value: DateValue):
        self._model_part[FIELD_DATE] = date_value.google_value()


class StringValueMixin:
    """
    Mixin class that provides accessors for the "value" attribute of the model object of a :py:class:BaseWrapper.
    Examples of Person fields with a value are EmailAddresses and PhoneNumbers.
    """

    @property
    @abstractmethod
    def _model_part(self) -> dict:
        """
        Method definition that enforces the use of the StringValueMixin with a :py:class:BaseWrapper.
        """
        pass

    @property
    def value(self) -> str:
        return self._model_part.get(FIELD_VALUE, "")

    @value.setter
    def value(self, value: str):
        self._model_part[FIELD_VALUE] = value


class TypeMixin:
    """
    Mixin class that provides accessors for the "type" attribute of the model object of a :py:class:BaseWrapper.
    Examples of Person fields with a type attribute are EmailAddresses and PhoneNumbers.
    """

    @property
    @abstractmethod
    def _model_part(self) -> dict:
        """
        Method definition that enforces the use of the TypeMixin with a :py:class:BaseWrapper.
        """
        pass

    @property
    def vtype(self) -> str:
        return self._model_part.get(FIELD_TYPE, "")

    @vtype.setter
    def vtype(self, type_value: str):
        self._model_part[FIELD_TYPE] = type_value

    @property
    def formatted_type(self) -> str:
        """
        Returns the formatted value of the type attribute. This value is read only in the api and therefor only
        updated if the person object is retrieved again. In turn, this property returns the old value if the type
        attribute has been changed for update.
        """
        return self._model_part.get(FIELD_FORMATTED_TYPE, "")


class ListWrapperMeta(type):
    """
    Metaclass of the :py:class:BaseListWrapper.

    List wrappers represent list attributes of a :py:class:PersonWrapper. Examples of list attributes are addresses or
    phone numbers as contacts can have multiple addresses and phone numbers.
    When accessing the items in the list a wrapper for each item needs to be created. Therefor each concrete class that
    derived from a :py:class:BaseListWrapper needs to "know" the concrete class derived from a :py:class:BaseWrapper.
    Furthermore, the ListWrapper must be able to instantiate objects of the concrete wrapper class.
    Both requirements are fulfilled by the ListWrapperMeta class that ensures via a member on class level that a
    wrapper class is provided.
    """

    def __new__(mcs, name, bases, namespace, **kargs):
        cls = super().__new__(mcs, name, bases, namespace)
        if ARG_WRAPPER_CLASS in kargs:
            cls.wrapper_class = kargs[ARG_WRAPPER_CLASS]
        return cls


WrapperT = TypeVar("WrapperT", bound=BaseWrapper)


class RemoveStrategy(Generic[WrapperT], metaclass=ABCMeta):
    """
    Parameter object to specify with items to remove from a list attribute of a :py:class:PersonWrapper.

    Removing items from a list attribute can follow different methods:
    - one can remove all items of the list
    - one can remove all items that match a certain criteria
    - one can remove only the first item that matches a certain criteria
    - one can remove all but the first item that matches a certain criteria

    While removing all items can be implemented rather easily, the other methods require more effort. We opted for the
    following process:
    1. The list of items to be removed is selected, e.g. all items that match a certain criteria.
    2. The RemoveStrategy is applied to narrow the list of suggestions down to the items that are actually removed.
    An example case is the deduplication of email addresses where the first email address is kept and all others are
    removed, cf. :py:class:RemoveSuggestedExceptFirst
    """

    @abstractmethod
    def remove_from(self,
                    all_enumerated: Iterator[Tuple[int, WrapperT]],
                    remove_suggestion: List[int] = None) -> List[int]:
        """
        Returns the list of indices of the items that should be removed from the list.
        """
        pass


class RemoveAllSuggested(Generic[WrapperT], RemoveStrategy[WrapperT]):
    """
    Implementation of a :py:class:RemoveStrategy that removes all list items that are suggested.
    """

    def remove_from(self,
                    all_enumerated: Iterator[Tuple[int, WrapperT]],
                    remove_suggestion: List[int] = None) -> List[int]:
        return remove_suggestion if remove_suggestion else list()


class RemoveFirstSuggested(Generic[WrapperT], RemoveStrategy[WrapperT]):
    """
    Implementation of a :py:class:RemoveStrategy that removes the first item of the ones that are suggested.
    """

    def remove_from(self,
                    all_enumerated: Iterator[Tuple[int, WrapperT]],
                    remove_suggestion: List[int] = None) -> List[int]:
        return remove_suggestion[0:1] if remove_suggestion and len(remove_suggestion) >= 1 else list()


class RemoveSuggestedExceptFirst(Generic[WrapperT], RemoveStrategy[WrapperT]):
    """
    Implementation of a :py:class:RemoveStrategy that removes all list items that are suggested except for the first.
    Most helpful with deduplication of values.
    """

    def remove_from(self,
                    all_enumerated: Iterator[Tuple[int, WrapperT]],
                    remove_suggestion: List[int] = None) -> List[int]:
        return remove_suggestion[1:] if remove_suggestion and len(remove_suggestion) >= 1 else list()


class BaseListWrapper(Generic[WrapperT], metaclass=ListWrapperMeta):
    """
    Base class for all wrappers of list attributes in the large object tree of a Person object.

    The classes derived from this BaseListWrapper are used e.g. for lists of addresses or lists of phone numbers while
    simple attributes as well as the items within the lists, i.e. the single addresses or single phone numbers are
    wrapped by BaseWrappers. The model object that is wrapped by the :py:class:PersonWrapper is delegated through to
    the list wrappers and further down to the :py:class:BaseWrappers of the list items.
    """

    def __init__(self, part_of_person_model: Optional[List[dict]], creation_callback: Callable[[], List[dict]]):
        """
        Constructor of the :py:class:BaseListWrapper.

        param part_of_person_model: The corresponding attribute of the model object wrapped by :py:class:PersonWrapper
        param creation_callback: A callback function that adds an empty list to the model object wrapped by the
            :py:class:PersonWrapper. This needs to be done with a callback that is retrieved by :py:class:PersonWrapper
            as we need to directly modify the model object that is a private member of the :py:class:PersonWrapper.
        """
        self.__part_of_person_model = part_of_person_model
        self.__creation_callback = creation_callback

    def _append_to_model(self, new_item: dict):
        """
        Appends a new item to the list attribute. Utilises the creation callback to create the list attribute if it
        does not exist yet.
        """
        if not self.__part_of_person_model:
            self.__part_of_person_model = self.__creation_callback()
        self.__part_of_person_model.append(new_item)

    def _remove_by_index(self, to_remove: List[int]):
        """
        Removes items from the list attribute by their index values. Deletion is done in reverse order to preserve
        the indices of the items that are to be deleted.
        """
        to_remove_sorted = sorted(to_remove, reverse=True)
        for index in to_remove_sorted:
            if index >= len(self.__part_of_person_model):
                raise IndexError("index too large on delete")
            del self.__part_of_person_model[index]

    def all(self) -> Iterator[WrapperT]:
        if not self.__part_of_person_model:
            return
        for entry in self.__part_of_person_model:
            yield self.__class__.wrapper_class(entry)

    def first(self) -> Optional[WrapperT]:
        return next(self.all(), None)

    def remove(self, remove_strategy: RemoveStrategy[WrapperT]):
        """
        Removes items from the list attribute by applying the given :py:class:RemoveStrategy.
        Caution: Tries to remove all items, i.e. applies no criteria to the values of the items.
        """
        all_enumerated = enumerate(self.all())
        remove_suggestion = [index for index, _ in all_enumerated]
        to_remove = remove_strategy.remove_from(all_enumerated, remove_suggestion)
        self._remove_by_index(to_remove)


DateValueWrapperT = TypeVar("DateValueWrapperT", bound=DateValueMixin)


class DateValueListMixin(Generic[DateValueWrapperT]):
    """
    Mixin for :py:class:BaseListWrapper that contain items that have a date value to provide common methods that deal
    with the date values.
    """

    @abstractmethod
    def _remove_by_index(self, to_remove: List[int]):
        """
        Enforces to have an "_remove_by_index" method that is (in all cases) implemented by :py:class:BaseListWrapper.
        """
        pass

    @abstractmethod
    def all(self) -> Iterator[DateValueWrapperT]:
        """
        Enforces to have an "all" method that is (in all cases) implemented by the :py:class:BaseListWrapper.
        """
        pass

    @abstractmethod
    def remove(self, remove_strategy: RemoveStrategy[DateValueWrapperT]):
        """
        Enforces to have a "remove" method that is (in all cases) implemented by the :py:class:BaseListWrapper.
        """
        pass

    def all_values(self) -> Iterator[DateValue]:
        for item in self.all():
            yield item.date_value

    def remove_all(self):
        self.remove(RemoveAllSuggested())

    def remove_by_value(self,
                        date_value: DateValue,
                        remove_strategy: RemoveStrategy[DateValueWrapperT] = RemoveAllSuggested()):
        """
        Removes all items from the list attribute that have the given value and are subsequently selected by the
        given :py:class:RemoveStrategy.
        """
        all_enumerated = enumerate(self.all())
        remove_suggestion = [index for index, item in all_enumerated if item.date_value == date_value]
        to_remove = remove_strategy.remove_from(all_enumerated, remove_suggestion)
        if not set(to_remove).issubset(set(remove_suggestion)):
            raise IndexError("Removal of items with other values requested")
        self._remove_by_index(to_remove)


StringValueWrapperT = TypeVar("StringValueWrapperT", bound=StringValueMixin)


class StringValueListMixin(Generic[StringValueWrapperT]):
    """
    Mixin for :py:class:BaseListWrapper that contain items that have a string value to provide common methods that deal
    with the string values.
    """

    @abstractmethod
    def _remove_by_index(self, to_remove: List[int]):
        """
        Enforces to have an "_remove_by_index" method that is (in all cases) implemented by :py:class:BaseListWrapper.
        """
        pass

    @abstractmethod
    def all(self) -> Iterator[StringValueWrapperT]:
        """
        Enforces to have an "all" method that is (in all cases) implemented by the :py:class:BaseListWrapper.
        """
        pass

    @abstractmethod
    def remove(self, remove_strategy: RemoveStrategy[StringValueWrapperT]):
        """
        Enforces to have a "remove" method that is (in all cases) implemented by the :py:class:BaseListWrapper.
        """
        pass

    def all_values(self) -> Iterator[str]:
        for item in self.all():
            yield item.value

    def remove_all(self):
        self.remove(RemoveAllSuggested())

    def remove_by_value(self,
                        value: str,
                        remove_strategy: RemoveStrategy[StringValueWrapperT] = RemoveAllSuggested()):
        """
        Removes all items from the list attribute that have the given value and are subsequently selected by the
        given :py:class:RemoveStrategy.
        """
        all_enumerated = enumerate(self.all())
        remove_suggestion = [index for index, item in all_enumerated if item.value == value]
        to_remove = remove_strategy.remove_from(all_enumerated, remove_suggestion)
        if not set(to_remove).issubset(set(remove_suggestion)):
            raise IndexError("Removal of items with other values requested")
        self._remove_by_index(to_remove)


TypeWrapperT = TypeVar("TypeWrapperT", bound=TypeMixin)


class TypeListMixin(Generic[TypeWrapperT]):

    @abstractmethod
    def _remove_by_index(self, to_remove: List[int]):
        """
        Enforces to have an "_remove_by_index" method that is (in all cases) implemented by :py:class:BaseListWrapper.
        """
        pass

    @abstractmethod
    def all(self) -> Iterator[TypeWrapperT]:
        """
        Enforces to have an "_remove_by_index" method that is (in all cases) implemented by :py:class:BaseListWrapper.
        """
        pass

    def first_of_type(self, vtype: str) -> Optional[TypeWrapperT]:
        for item in self.all():
            if item and item.vtype and item.vtype == vtype:
                return item
        return None

    def remove_by_type(self,
                       vtype: str,
                       remove_strategy: RemoveStrategy[StringValueWrapperT] = RemoveAllSuggested()):
        """
        Removes all items from the list attribute that have the given type and are subsequently selected by the
        given :py:class:RemoveStrategy.
        """
        all_enumerated = enumerate(self.all())
        remove_suggestion = [index for index, item in all_enumerated if item.vtype == vtype]
        to_remove = remove_strategy.remove_from(all_enumerated, remove_suggestion)
        if not set(to_remove).issubset(set(remove_suggestion)):
            raise IndexError("Removal of items with other types requested")
        self._remove_by_index(to_remove)


class AddressWrapper(BaseWrapper, TypeMixin):
    """
    Implementation of the :py:class:BaseWrapper for a single address object. For descriptions of the attributes
    see https://developers.google.com/people/api/rest/v1/people#address
    :py:class:PersonWrapper can contain multiple addresses in a :py:class:AddressesWrapper.
    """

    @property
    def formatted(self) -> str:
        return self._model_part.get("formattedValue", "")

    @property
    def po_box(self) -> str:
        return self._model_part.get("poBox", "")

    @po_box.setter
    def po_box(self, po_box: str):
        self._model_part["poBox"] = po_box

    @property
    def street_address(self) -> str:
        return self._model_part.get("streetAddress", "")

    @street_address.setter
    def street_address(self, street_address: str):
        self._model_part["streetAddress"] = street_address

    @property
    def extended_address(self) -> str:
        return self._model_part.get("extendedAddress", "")

    @extended_address.setter
    def extended_address(self, extended_address: str):
        self._model_part["extendedAddress"] = extended_address

    @property
    def city(self) -> str:
        return self._model_part.get("city", "")

    @city.setter
    def city(self, city: str):
        self._model_part["city"] = city

    @property
    def region(self) -> str:
        return self._model_part.get("region", "")

    @region.setter
    def region(self, region: str):
        self._model_part["region"] = region

    @property
    def postal_code(self) -> str:
        return self._model_part.get("postalCode", "")

    @postal_code.setter
    def postal_code(self, postal_code: str):
        self._model_part["postalCode"] = postal_code

    @property
    def country(self) -> str:
        return self._model_part.get("country", "")

    @country.setter
    def country(self, country: str):
        self._model_part["country"] = country

    @property
    def country_code(self) -> str:
        return self._model_part.get("countryCode", "")

    @country_code.setter
    def country_code(self, country_code: str):
        self._model_part["countryCode"] = country_code


class AddressesWrapper(BaseListWrapper[AddressWrapper], TypeListMixin[AddressWrapper],
                       metaclass=ListWrapperMeta, wrapper_class=AddressWrapper):
    """
    Implementation of the :py:class:BaseListWrapper for an addresses attribute of the :py:class:PersonWrapper. This list
    wrapper contains a list of :py:class:AddressWrapper.
    """

    def append_address(self, address_type: str, city: str) -> "AddressesWrapper":
        """
        Appends a new address to the list of addresses. The minimal information required is the city which is a
        reasonable but arbitrary choice. After appending the new address, the :py:class:AddressWrapper is returned and
        allows to set all other attributes of the address.
        """
        self._append_to_model({
            "city": city,
            FIELD_TYPE: address_type
        })
        return self


class BirthdayWrapper(BaseWrapper, DateValueMixin):
    """
    Implementation of the :py:class:BaseWrapper for a single birthday object. For descriptions of the attributes
    see https://developers.google.com/people/api/rest/v1/people#birthday
    Each :py:class:PersonWrapper can contain multiple birthdays in a :py:class:BirthdaysWrapper.
    """
    pass


class BirthdaysWrapper(BaseListWrapper[BirthdayWrapper],
                       DateValueListMixin[BirthdayWrapper],
                       metaclass=ListWrapperMeta, wrapper_class=BirthdayWrapper):
    """
    Implementation of the :py:class:BaseListWrapper for the birthday attribute of the :py:class:PersonWrapper.
    This list wrapper contains a list of :py:class:BirthdayWrapper.
    """

    def append_birthday(self, date_value: DateValue) -> "BirthdaysWrapper":
        """
        Appends a new birthday to the list.
        """
        self._append_to_model({
            FIELD_DATE: date_value.google_value()
        })
        return self

    def replace_birthday(self, date_value: DateValue) -> "BirthdaysWrapper":
        """
        Sets the birthday to the given date_value. If the list is empty, a new birthday is appended. If the list is
        non-empty, all current elements are discarded.
        """
        self.remove_all()
        self.append_birthday(date_value)
        return self


class EmailAddressWrapper(BaseWrapper, TypeMixin, StringValueMixin):
    """
    Implementation of the :py:class:BaseWrapper for a single email object. For descriptions of the attributes
    see https://developers.google.com/people/api/rest/v1/people#emailaddress
    Each :py:class:PersonWrapper can contain multiple email addresses in a :py:class:EmailAddressesWrapper.
    """
    pass


class EmailAddressesWrapper(BaseListWrapper[EmailAddressWrapper],
                            StringValueListMixin[EmailAddressWrapper],
                            TypeListMixin[EmailAddressWrapper],
                            metaclass=ListWrapperMeta, wrapper_class=EmailAddressWrapper):
    """
    Implementation of the :py:class:BaseListWrapper for the email addresses attribute of the :py:class:PersonWrapper.
    This list wrapper contains a list of :py:class:EmailAddressWrapper.
    """

    def append_email_address(self, address_type: str, address_value: str) -> "EmailAddressesWrapper":
        """
        Appends a new email address to the list. The minimal information required is the string value, i.e. the email.
        """
        self._append_to_model({
            FIELD_TYPE: address_type,
            FIELD_VALUE: address_value
        })
        return self


class EventWrapper(BaseWrapper, TypeMixin, DateValueMixin):
    """
    Implementation of the :py:class:BaseWrapper for a single event date. For descriptions of the attributes
    see https://developers.google.com/people/api/rest/v1/people#event
    Each :py:class:PersonWrapper can contain multiple email addresses in a :py:class:EventsWrapper.
    """
    pass


class EventsWrapper(BaseListWrapper[EventWrapper],
                    StringValueListMixin[EventWrapper],
                    TypeListMixin[EventWrapper],
                    metaclass=ListWrapperMeta, wrapper_class=EventWrapper):
    """
    Implementation of the :py:class:BaseListWrapper for the events attribute of the :py:class:PersonWrapper.
    This list wrapper contains a list of :py:class:EventsWrapper.
    """

    def append_event(self, event_type: str, event_date: str) -> "EventsWrapper":
        """
        Appends a new event to the list. The information required are the type and the date of the event.
        """
        self._append_to_model({
            FIELD_TYPE: event_type,
            FIELD_DATE: event_date
        })
        return self


class NameWrapper(BaseWrapper):
    """
    Implementation of the :py:class:BaseWrapper for a single name object. For descriptions of the attributes
    see https://developers.google.com/people/api/rest/v1/people#name
    Each :py:class:PersonWrapper can only contain one name item in its names list even though it is still a list.
    """

    @property
    def display_name(self) -> str:
        return self._model_part.get("displayName", "")

    @property
    def display_name_last_first(self) -> str:
        return self._model_part.get("displayNameLastFirst", "")

    @property
    def unstructured_name(self) -> str:
        return self._model_part.get("unstructuredName", "")

    @unstructured_name.setter
    def unstructured_name(self, unstructured_name: str):
        self._model_part["unstructuredName"] = unstructured_name

    @property
    def family_name(self) -> str:
        return self._model_part.get("familyName", "")

    @family_name.setter
    def family_name(self, family_name: str):
        self._model_part["familyName"] = family_name

    @property
    def given_name(self) -> str:
        return self._model_part.get("givenName", "")

    @given_name.setter
    def given_name(self, given_name: str):
        self._model_part["givenName"] = given_name

    @property
    def middle_name(self) -> str:
        return self._model_part.get("middleName", "")

    @middle_name.setter
    def middle_name(self, middle_name: str):
        self._model_part["middleName"] = middle_name

    @property
    def honorific_prefix(self) -> str:
        return self._model_part.get("honorificPrefix", "")

    @honorific_prefix.setter
    def honorific_prefix(self, honorific_prefix: str):
        self._model_part["honorificPrefix"] = honorific_prefix

    @property
    def honorific_suffix(self) -> str:
        return self._model_part.get("honorificSuffix", "")

    @honorific_suffix.setter
    def honorific_suffix(self, honorific_suffix: str):
        self._model_part["honorificSuffix"] = honorific_suffix


class NamesWrapper(BaseListWrapper[NameWrapper], metaclass=ListWrapperMeta, wrapper_class=NameWrapper):
    """
    Implementation of the :py:class:BaseListWrapper for the names attribute of the :py:class:PersonWrapper.
    With the names attribute the Google People API is a little special: There can be only zero or one name items
    in the list (Which makes sense, because a person has only one name).
    To add a little convenience, this wrapper provides all properties to access the single name item which introduces
    a lot of bloat in the code but makes it easier to use.
    """

    def _append_to_model(self, new_item: dict):
        """
        Appends a new name if and only if the names attribute of the :py:class:PersonWrapper is an empty list.
        We add a little check here to make sure that only one name item is added to the list.
        """
        if self.first():
            raise ValueError("Cannot append another name object, only one name item is allowed per person")
        super()._append_to_model(new_item)

    @property
    def display_name(self) -> Optional[str]:
        single_name = self.first()
        return single_name.display_name if single_name else None

    @property
    def display_name_last_first(self) -> str:
        single_name = self.first()
        return single_name.display_name_last_first if single_name else None

    @property
    def unstructured_name(self) -> str:
        single_name = self.first()
        return single_name.unstructured_name if single_name else None

    @unstructured_name.setter
    def unstructured_name(self, unstructured_name: str):
        single_name = self.first()
        if single_name:
            single_name.unstructured_name = unstructured_name
        else:
            self._append_to_model({"unstructuredName": unstructured_name})

    @property
    def family_name(self) -> str:
        single_name = self.first()
        return single_name.family_name if single_name else None

    @family_name.setter
    def family_name(self, family_name: str):
        single_name = self.first()
        if single_name:
            single_name.family_name = family_name
        else:
            self._append_to_model({"familyName": family_name})

    @property
    def given_name(self) -> str:
        single_name = self.first()
        return single_name.given_name if single_name else None

    @given_name.setter
    def given_name(self, given_name: str):
        single_name = self.first()
        if single_name:
            single_name.given_name = given_name
        else:
            self._append_to_model({"givenName": given_name})

    @property
    def middle_name(self) -> str:
        single_name = self.first()
        return single_name.middle_name if single_name else None

    @middle_name.setter
    def middle_name(self, middle_name: str):
        single_name = self.first()
        if single_name:
            single_name.middle_name = middle_name
        else:
            self._append_to_model({"middleName": middle_name})

    @property
    def honorific_prefix(self) -> str:
        single_name = self.first()
        return single_name.honorific_prefix if single_name else None

    @honorific_prefix.setter
    def honorific_prefix(self, honorific_prefix: str):
        single_name = self.first()
        if single_name:
            single_name.honorific_prefix = honorific_prefix
        else:
            self._append_to_model({"honorificPrefix": honorific_prefix})

    @property
    def honorific_suffix(self) -> str:
        single_name = self.first()
        return single_name.honorific_suffix if single_name else None

    @honorific_suffix.setter
    def honorific_suffix(self, honorific_suffix: str):
        single_name = self.first()
        if single_name:
            single_name.honorific_suffix = honorific_suffix
        else:
            self._append_to_model({"honorificSuffix": honorific_suffix})


class PhoneNumberWrapper(BaseWrapper, TypeMixin, StringValueMixin):
    """
    Implementation of the :py:class:BaseWrapper for a single phone number. For descriptions of the attributes
    see https://developers.google.com/people/api/rest/v1/people#phonenumber
    Each :py:class:PersonWrapper can contain multiple phone numbers in a :py:class:PhoneNumbersWrapper.
    """

    @property
    def value_canonical_form(self) -> str:
        return self._model_part.get("canonicalForm", "")


class PhoneNumbersWrapper(BaseListWrapper[PhoneNumberWrapper],
                          StringValueListMixin[PhoneNumberWrapper],
                          TypeListMixin[PhoneNumberWrapper],
                          metaclass=ListWrapperMeta, wrapper_class=PhoneNumberWrapper):
    """
    Implementation of the :py:class:BaseListWrapper for the phone numbers attribute of the :py:class:PersonWrapper.
    This list wrapper contains a list of :py:class:PhoneNumberWrapper.
    """

    def append_phone_number(self, number_type: str, number_value: str) -> "PhoneNumbersWrapper":
        """
        Appends a new phone number to the list. The minimal information required is the string value, i.e. the number.
        """
        self._append_to_model({
            FIELD_VALUE: number_value,
            FIELD_TYPE: number_type
        })
        return self


class PersonWrapper(ModelWrapper[PersonField]):
    """
    Implementation of the :py:class:ModelWrapper for the top level object of the Google People API that contains
    a person. For a detailed description of the attributes
    see https://developers.google.com/people/api/rest/v1/people#resource:-person
    """

    @property
    def logging_name(self) -> str:
        """
        Always returns an identifying string for the person. If the person has a display name, this is returned.
        Else we return the resource name.
        """
        if PersonField.names in self.field_mask:
            display_name = self.names.display_name
            if display_name:
                return display_name
        return self.resource_name

    @property
    def addresses(self) -> AddressesWrapper:
        return AddressesWrapper(
            self._model_field(PersonField.addresses),
            self._creation_callback(PersonField.addresses, []))

    @property
    def birthdays(self) -> BirthdaysWrapper:
        return BirthdaysWrapper(
            self._model_field(PersonField.birthdays),
            self._creation_callback(PersonField.birthdays, []))

    @property
    def email_addresses(self) -> EmailAddressesWrapper:
        return EmailAddressesWrapper(
            self._model_field(PersonField.email_addresses),
            self._creation_callback(PersonField.email_addresses, []))

    @property
    def events(self) -> EventsWrapper:
        return EventsWrapper(
            self._model_field(PersonField.events),
            self._creation_callback(PersonField.events, []))

    @property
    def names(self) -> NamesWrapper:
        return NamesWrapper(
            self._model_field(PersonField.names),
            self._creation_callback(PersonField.names, []))

    @property
    def phone_numbers(self) -> PhoneNumbersWrapper:
        return PhoneNumbersWrapper(
            self._model_field(PersonField.phone_numbers),
            self._creation_callback(PersonField.phone_numbers, []))
