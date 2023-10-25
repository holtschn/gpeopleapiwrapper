import unittest

from gpeopleapiwrapper import persons
from tests import test_persons_base as tpb


class TestPersonWrapperBirthdays(tpb.FixtureMixin, unittest.TestCase):

    def test_read_birthday_attributes(self):
        person = self.read_fixture_tester_extensive()
        birthdays = person.birthdays.first()
        self.assertIsNotNone(birthdays)
        google_value = birthdays.date_value.google_value()
        self.assertEqual(1935, google_value["year"])
        self.assertEqual(6, google_value["month"])
        self.assertEqual(16, google_value["day"])
        self.assertFalse(person.has_changes())

    def test_append_birthday(self):
        person = self.read_fixture_tester_extensive()
        value_to_append = persons.DateValue.from_full_date(1978, 6, 14)
        person.birthdays.append_birthday(value_to_append)
        birthdays = list(person.birthdays.all_values())
        self.assertIsNotNone(birthdays)
        self.assertEqual(2, len(birthdays))
        self.assertTrue(value_to_append in birthdays)

    def test_append_birthday_to_unset_list_attribute(self):
        person = self.read_fixture_tester_empty()
        value_to_append = persons.DateValue.from_full_date(1978, 6, 14)
        person.birthdays.append_birthday(value_to_append)
        self.assertEqual(1, len(list(person.birthdays.all())))
        self.assertEqual(value_to_append, person.birthdays.first().date_value)
        self.assertTrue(person.has_changes())

    def test_replace_birthdays(self):
        person = self.read_fixture_tester_duplicates()
        replacement_value = persons.DateValue.from_month_day(9, 17)
        person.birthdays.replace_birthdays_with_single(replacement_value)
        birthdays = list(person.birthdays.all_values())
        self.assertIsNotNone(birthdays)
        self.assertEqual(1, len(birthdays))
        self.assertTrue(replacement_value in birthdays)
