import unittest

from gpeopleapiwrapper import persons
from tests import test_persons_base as tpb


class TestPersonTypeMixins(tpb.FixtureMixin, unittest.TestCase):

    def test_read_all_of_type(self):
        person = self.read_fixture_tester_duplicates()
        all_values = list(person.email_addresses.all_of_type("home"))
        self.assertIsNotNone(all_values)
        self.assertEqual(3, len(all_values))
        self.assertEqual({"home"}, set([v.vtype for v in all_values]))
        self.assertFalse(person.has_changes())

    def test_read_all_of_type_missing(self):
        person = self.read_fixture_tester_duplicates()
        no_values = person.email_addresses.all_of_type("unavail")
        self.assertIsNotNone(no_values)
        self.assertEqual(0, len(list(no_values)))
        self.assertFalse(person.has_changes())

    def test_read_first_of_type(self):
        person = self.read_fixture_tester_average()
        first_value = person.email_addresses.first_of_type("other")
        self.assertIsNotNone(first_value)
        self.assertEqual("other", first_value.vtype)
        self.assertEqual("eva.tester@example.com", first_value.value)
        self.assertFalse(person.has_changes())

    def test_read_first_of_type_missing(self):
        person = self.read_fixture_tester_average()
        value_for_type_unavail = person.email_addresses.first_of_type("unavail")
        self.assertIsNone(value_for_type_unavail)
        self.assertFalse(person.has_changes())

    def test_remove_by_type_all(self):
        person = self.read_fixture_tester_duplicates()
        person.email_addresses.remove_by_type("home", persons.RemoveAllSuggested())
        self.assertEqual(1, len(list(person.email_addresses.all())))
        self.assertEqual("work", person.email_addresses.first().vtype)
        self.assertTrue(person.has_changes())

    def test_remove_by_type_first(self):
        person = self.read_fixture_tester_duplicates()
        person.email_addresses.remove_by_type("home", persons.RemoveFirstSuggested())
        self.assertEqual(3, len(list(person.email_addresses.all())))
        self.assertEqual(2, len(list(person.email_addresses.all_of_type("home"))))
        self.assertTrue(person.has_changes())

    def test_remove_by_type_keep_first(self):
        person = self.read_fixture_tester_duplicates()
        person.email_addresses.remove_by_type("home", persons.RemoveSuggestedExceptFirst())
        self.assertEqual(2, len(list(person.email_addresses.all())))
        self.assertEqual(1, len(list(person.email_addresses.all_of_type("home"))))
        self.assertEqual(1, len(list(person.email_addresses.all_of_type("work"))))
        self.assertTrue(person.has_changes())

    def test_type_wrapper_read_attributes(self):
        person = self.read_fixture_tester_average()
        type_wrapper = person.email_addresses.first_of_type("other")
        self.assertEqual("other", type_wrapper.vtype)
        self.assertEqual("eva.tester@example.com", type_wrapper.value)
        self.assertEqual("Other", type_wrapper.formatted_type)

    def test_type_wrapper_set_attributes(self):
        person = self.read_fixture_tester_average()
        type_wrapper = person.email_addresses.first_of_type("other")
        type_wrapper.vtype = "home"
        type_wrapper.value = "ave.retser@example.de"
        control_wrapper = person.email_addresses.first_of_type("home")
        self.assertEqual("home", control_wrapper.vtype)
        self.assertEqual("ave.retser@example.de", control_wrapper.value)

    def test_type_wrapper_set_read_only_attribute_fail(self):
        person = self.read_fixture_tester_average()
        type_wrapper = person.email_addresses.first_of_type("home")
        with self.assertRaises(AttributeError):
            type_wrapper.formatted_type = "fail"
