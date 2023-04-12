import json
import unittest
from os import path

from gpeopleapiwrapper import base, persons


class FixtureMixin:

    @staticmethod
    def read_fixture(filename: str) -> dict:
        with open(path.join(path.dirname(__file__), "fixtures/" + filename)) as fixture_file:
            return json.load(fixture_file)

    @staticmethod
    def read_fixture_tester_eva() -> persons.PersonWrapper:
        return persons.PersonWrapper(FixtureMixin.read_fixture("tester_eva.json"),
                                     [persons.PersonField.names,
                                      persons.PersonField.phone_numbers,
                                      persons.PersonField.email_addresses
                                      ])

    @staticmethod
    def read_fixture_tester_klaus() -> persons.PersonWrapper:
        return persons.PersonWrapper(FixtureMixin.read_fixture("tester_klaus.json"),
                                     [persons.PersonField.names,
                                      persons.PersonField.addresses,
                                      persons.PersonField.phone_numbers,
                                      persons.PersonField.email_addresses
                                      ])

    @staticmethod
    def read_fixture_tester_blank() -> persons.PersonWrapper:
        return persons.PersonWrapper(FixtureMixin.read_fixture("tester_blank.json"),
                                     [persons.PersonField.names,
                                      persons.PersonField.addresses,
                                      persons.PersonField.phone_numbers,
                                      persons.PersonField.email_addresses
                                      ])


class TestPersonWrapperBase(FixtureMixin, unittest.TestCase):

    def test_read_fixture_tester_eva(self):
        person = TestPersonWrapperBase.read_fixture_tester_eva()
        self.assertIsNotNone(person.names)
        self.assertIsNotNone(person.phone_numbers)
        self.assertIsNotNone(person.email_addresses)
        self.assertFalse(person.has_changes())

    def test_read_fixture_tester_klaus(self):
        person = TestPersonWrapperBase.read_fixture_tester_klaus()
        self.assertIsNotNone(person.names)
        self.assertIsNotNone(person.addresses)
        self.assertIsNotNone(person.phone_numbers)
        self.assertIsNotNone(person.email_addresses)
        self.assertFalse(person.has_changes())

    def test_read_fixture_tester_blank(self):
        person = TestPersonWrapperBase.read_fixture_tester_blank()
        self.assertIsNotNone(person.names)
        self.assertIsNotNone(person.addresses)
        self.assertIsNotNone(person.phone_numbers)
        self.assertIsNotNone(person.email_addresses)
        self.assertFalse(person.has_changes())

    def test_read_resource_name(self):
        person = TestPersonWrapperBase.read_fixture_tester_eva()
        self.assertEqual("people/ahGaPhi9oquoht9eichu", person.resource_name)

    def test_read_field_mask(self):
        person = TestPersonWrapperBase.read_fixture_tester_eva()
        self.assertEqual(person.field_mask, [
            persons.PersonField.names,
            persons.PersonField.phone_numbers,
            persons.PersonField.email_addresses
        ])

    def test_str(self):
        person = TestPersonWrapperBase.read_fixture_tester_eva()
        str_result = str(person)
        self.assertTrue("people/ahGaPhi9oquoht9eichu" in str_result)

    def test_repr(self):
        person = TestPersonWrapperBase.read_fixture_tester_eva()
        str_result = str([person])
        self.assertTrue("PersonWrapper" in str_result)
        self.assertTrue("people/ahGaPhi9oquoht9eichu" in str_result)

    def test_get_model(self):
        model_init = TestPersonWrapperBase.read_fixture("tester_eva.json")
        person = persons.PersonWrapper(model_init,
                                       [persons.PersonField.names,
                                        persons.PersonField.phone_numbers,
                                        persons.PersonField.email_addresses
                                        ])
        model_check = person.model_copy()
        self.assertEqual(person.model_copy(), model_check)

        model_check["phoneNumbers"] = []
        self.assertEqual(person.model_copy(), person.model_copy())

    def test_fail_for_not_included_attributes(self):
        person = TestPersonWrapperBase.read_fixture_tester_eva()
        with self.assertRaises(base.FieldNotInMaskError):
            fail = person.addresses

    def test_read_unset_attributes(self):
        person = TestPersonWrapperBase.read_fixture_tester_blank()
        self.assertListEqual([], list(person.addresses.all()))
        self.assertListEqual([], list(person.phone_numbers.all()))
        self.assertListEqual([], list(person.email_addresses.all()))

    def test_read_is_not_a_change(self):
        person = TestPersonWrapperBase.read_fixture_tester_eva()
        self.assertFalse(person.has_changes())
