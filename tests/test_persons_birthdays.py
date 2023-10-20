import unittest

from gpeopleapiwrapper import persons
from tests import test_persons_base as tpb


class TestPersonWrapperBirthdays(tpb.FixtureMixin, unittest.TestCase):

    def test_read_birthday_attributes(self):
        person = TestPersonWrapperBirthdays.read_fixture_tester_extensive()

        birthdays = person.birthdays.first()
        self.assertIsNotNone(birthdays)

        google_value = birthdays.date_value.google_value()
        self.assertEqual(1935, google_value["year"])
        self.assertEqual(6, google_value["month"])
        self.assertEqual(16, google_value["day"])

        self.assertFalse(person.has_changes())

    def test_read_no_birthday_available(self):
        person = TestPersonWrapperBirthdays.read_fixture_tester_average()

        birthdays = person.birthdays.first()
        self.assertIsNone(birthdays)

        self.assertFalse(person.has_changes())

    def test_read_all_birthdays(self):
        person = TestPersonWrapperBirthdays.read_fixture_tester_duplicates()

        self.assertEqual(3, len(list(person.birthdays.all())))

        birthdays = list(person.birthdays.all())
        self.assertIsNotNone(birthdays)

        self.assertEqual(persons.DateValue.from_full_date(1935, 6, 16), birthdays[0].date_value)
        self.assertEqual(persons.DateValue.from_full_date(1935, 7, 16), birthdays[1].date_value)
        self.assertEqual(persons.DateValue.from_full_date(1935, 6, 16), birthdays[2].date_value)

        self.assertFalse(person.has_changes())

    def test_read_all_birthday_values(self):
        person = TestPersonWrapperBirthdays.read_fixture_tester_duplicates()

        self.assertEqual(3, len(list(person.birthdays.all())))

        birthdays = list(person.birthdays.all_values())
        self.assertIsNotNone(birthdays)

        self.assertEqual(persons.DateValue.from_full_date(1935, 6, 16), birthdays[0])
        self.assertEqual(persons.DateValue.from_full_date(1935, 7, 16), birthdays[1])
        self.assertEqual(persons.DateValue.from_full_date(1935, 6, 16), birthdays[2])

        self.assertFalse(person.has_changes())

    def test_update_birthday_attribute(self):
        person = TestPersonWrapperBirthdays.read_fixture_tester_extensive()

        birthdays = person.birthdays.first()
        self.assertIsNotNone(birthdays)

        birthdays.date_value = tpb.persons.DateValue.from_full_date(2014, 6, 14)

        google_value = birthdays.date_value.google_value()
        self.assertEqual(2014, google_value["year"])
        self.assertEqual(6, google_value["month"])
        self.assertEqual(14, google_value["day"])

    def test_append_birthday(self):
        person = TestPersonWrapperBirthdays.read_fixture_tester_extensive()

        person.birthdays.append_birthday(tpb.persons.DateValue.from_full_date(1978, 6, 14))
        self.assertEqual(2, len(list(person.birthdays.all())))

        birthdays = list(person.birthdays.all())
        self.assertIsNotNone(birthdays)

        self.assertEqual(persons.DateValue.from_full_date(1935, 6, 16), birthdays[0].date_value)
        self.assertEqual(persons.DateValue.from_full_date(1978, 6, 14), birthdays[1].date_value)

    def test_remove_all_birthdays(self):
        person = TestPersonWrapperBirthdays.read_fixture_tester_duplicates()

        person.birthdays.remove_all()
        self.assertEqual(0, len(list(person.birthdays.all())))

    def test_remove_birthday_by_value(self):
        person = TestPersonWrapperBirthdays.read_fixture_tester_extensive()

        person.birthdays.remove_by_value(tpb.persons.DateValue.from_full_date(1935, 6, 16))
        self.assertEqual(0, len(list(person.birthdays.all())))

    def test_remove_multiple_birthdays_by_value(self):
        person = TestPersonWrapperBirthdays.read_fixture_tester_duplicates()

        person.birthdays.remove_by_value(tpb.persons.DateValue.from_full_date(1935, 6, 16))
        self.assertEqual(1, len(list(person.birthdays.all())))

        birthday = person.birthdays.first()
        self.assertIsNotNone(birthday)

        self.assertEqual(persons.DateValue.from_full_date(1935, 7, 16), birthday.date_value)

    def test_remove_first_matching_birthday_by_value(self):
        person = TestPersonWrapperBirthdays.read_fixture_tester_duplicates()

        person.birthdays.remove_by_value(
            tpb.persons.DateValue.from_full_date(1935, 6, 16),
            tpb.persons.RemoveFirstSuggested())
        self.assertEqual(2, len(list(person.birthdays.all())))

        birthdays = list(person.birthdays.all_values())

        self.assertEqual(persons.DateValue.from_full_date(1935, 7, 16), birthdays[0])
        self.assertEqual(persons.DateValue.from_full_date(1935, 6, 16), birthdays[1])

    def test_replace_birthdays(self):
        person = TestPersonWrapperBirthdays.read_fixture_tester_duplicates()

        self.assertEqual(3, len(list(person.birthdays.all())))
        person.birthdays.replace_birthday(tpb.persons.DateValue.from_month_day(9, 17))
        self.assertEqual(1, len(list(person.birthdays.all())))

        birthday = person.birthdays.first()
        self.assertIsNotNone(birthday)

        self.assertEqual(persons.DateValue.from_month_day(9, 17), birthday.date_value)
