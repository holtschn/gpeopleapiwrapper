import unittest

from gpeopleapiwrapper import persons
from tests import test_persons_base as tpb


class TestPersonDateValueMixins(tpb.FixtureMixin, unittest.TestCase):

    def test_read_first_string_value(self):
        person = self.read_fixture_tester_extensive()
        string_value = person.phone_numbers.first()
        self.assertIsNotNone(string_value)
        self.assertFalse(person.has_changes())

    def test_read_first_no_string_value_available(self):
        person = self.read_fixture_tester_empty()
        string_value = person.phone_numbers.first()
        self.assertIsNone(string_value)
        self.assertFalse(person.has_changes())

    def test_read_all_string_wrappers(self):
        person = self.read_fixture_tester_duplicates()
        all_wrappers = list(person.phone_numbers.all())
        self.assertIsNotNone(all_wrappers)
        self.assertEqual(4, len(all_wrappers))
        self.assertFalse(person.has_changes())

    def test_read_all_string_values(self):
        person = self.read_fixture_tester_duplicates()
        all_values = list(person.phone_numbers.all_values())
        self.assertIsNotNone(all_values)
        self.assertEqual(4, len(all_values))
        self.assertFalse(person.has_changes())

    def test_remove_string_values_all(self):
        person = self.read_fixture_tester_extensive()
        person.phone_numbers.remove_all()
        self.assertEqual(0, len(list(person.phone_numbers.all())))

    def test_remove_by_string_value_all(self):
        person = self.read_fixture_tester_duplicates()
        value_to_remove = "+49 40 54637281"
        person.phone_numbers.remove_by_value(value_to_remove, persons.RemoveAllSuggested())
        self.assertEqual(1, len(list(person.phone_numbers.all())))
        self.assertNotIn(value_to_remove, list(person.phone_numbers.all_values()))

    def test_remove_by_string_value_first(self):
        person = self.read_fixture_tester_duplicates()
        value_to_remove = "+49 40 54637281"
        person.phone_numbers.remove_by_value(value_to_remove, persons.RemoveFirstSuggested())
        self.assertEqual(3, len(list(person.phone_numbers.all())))
        self.assertIn(value_to_remove, list(person.phone_numbers.all_values()))

    def test_remove_by_string_value_keep_first(self):
        person = self.read_fixture_tester_duplicates()
        value_to_remove = "+49 40 54637281"
        person.phone_numbers.remove_by_value(value_to_remove, persons.RemoveSuggestedExceptFirst())
        self.assertEqual(2, len(list(person.phone_numbers.all())))
        self.assertIn(value_to_remove, list(person.phone_numbers.all_values()))

    def test_read_string_value_attribute(self):
        person = self.read_fixture_tester_extensive()
        string_value = person.phone_numbers.first()
        self.assertIsNotNone(string_value)
        self.assertEqual("+49 40 54637281", string_value.value)
        self.assertFalse(person.has_changes())

    def test_set_string_value_attribute(self):
        person = self.read_fixture_tester_extensive()
        string_value = person.phone_numbers.first()
        self.assertIsNotNone(string_value)
        value_to_set = "+49 241 98347919"
        string_value.value = value_to_set
        self.assertEqual(value_to_set, person.phone_numbers.first().value)
