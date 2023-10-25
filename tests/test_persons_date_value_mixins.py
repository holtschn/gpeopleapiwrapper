import unittest

from gpeopleapiwrapper import persons
from tests import test_persons_base as tpb


class TestPersonDateValueMixins(tpb.FixtureMixin, unittest.TestCase):

    def test_read_first_date_value(self):
        person = self.read_fixture_tester_extensive()
        date_value = person.birthdays.first()
        self.assertIsNotNone(date_value)
        self.assertFalse(person.has_changes())

    def test_read_first_no_date_value_available(self):
        person = self.read_fixture_tester_average()
        date_value = person.birthdays.first()
        self.assertIsNone(date_value)
        self.assertFalse(person.has_changes())

    def test_read_all_date_wrappers(self):
        person = self.read_fixture_tester_duplicates()
        all_wrappers = list(person.birthdays.all())
        self.assertIsNotNone(all_wrappers)
        self.assertEqual(3, len(all_wrappers))
        self.assertFalse(person.has_changes())

    def test_read_all_date_values(self):
        person = self.read_fixture_tester_duplicates()
        all_values = list(person.birthdays.all_values())
        self.assertIsNotNone(all_values)
        self.assertEqual(3, len(all_values))
        self.assertFalse(person.has_changes())

    def test_remove_date_values_all(self):
        person = self.read_fixture_tester_extensive()
        person.birthdays.remove_all()
        self.assertEqual(0, len(list(person.birthdays.all())))

    def test_remove_by_date_value_all(self):
        person = self.read_fixture_tester_duplicates()
        value_to_remove = persons.DateValue.from_full_date(1935, 6, 16)
        person.birthdays.remove_by_value(value_to_remove, persons.RemoveAllSuggested())
        self.assertEqual(1, len(list(person.birthdays.all())))
        self.assertNotIn(value_to_remove, list(person.birthdays.all_values()))

    def test_remove_by_date_value_first(self):
        person = self.read_fixture_tester_duplicates()
        value_to_remove = persons.DateValue.from_full_date(1935, 6, 16)
        person.birthdays.remove_by_value(value_to_remove, persons.RemoveFirstSuggested())
        self.assertEqual(2, len(list(person.birthdays.all())))
        self.assertIn(value_to_remove, list(person.birthdays.all_values()))

    def test_remove_by_date_value_keep_first(self):
        person = self.read_fixture_tester_duplicates()
        value_to_remove = persons.DateValue.from_full_date(1935, 6, 16)
        person.birthdays.remove_by_value(value_to_remove, persons.RemoveSuggestedExceptFirst())
        self.assertEqual(2, len(list(person.birthdays.all())))
        self.assertIn(value_to_remove, list(person.birthdays.all_values()))

    def test_read_date_value_attribute(self):
        person = self.read_fixture_tester_extensive()
        date_value = person.birthdays.first()
        self.assertIsNotNone(date_value)
        self.assertEqual(persons.DateValue.from_full_date(1935, 6, 16), date_value.date_value)
        self.assertFalse(person.has_changes())

    def test_set_date_value_attribute(self):
        person = self.read_fixture_tester_extensive()
        date_value = person.birthdays.first()
        self.assertIsNotNone(date_value)
        value_to_set = persons.DateValue.from_full_date(1956, 2, 5)
        date_value.date_value = value_to_set
        self.assertEqual(value_to_set, person.birthdays.first().date_value)
