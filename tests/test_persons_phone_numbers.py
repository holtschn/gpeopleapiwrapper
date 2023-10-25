import unittest

from tests import test_persons_base as tpb


class TestPersonWrapperPhoneNumbers(tpb.FixtureMixin, unittest.TestCase):

    def test_read_phone_number_attributes(self):
        person = self.read_fixture_tester_extensive()

        phone_number_home = person.phone_numbers.first_of_type("home")
        self.assertIsNotNone(phone_number_home)
        self.assertEqual("home", phone_number_home.vtype)
        self.assertEqual("Home", phone_number_home.formatted_type)
        self.assertEqual("+49 40 9384756", phone_number_home.value)
        self.assertEqual("+49409384756", phone_number_home.value_canonical_form)

        phone_number_work = person.phone_numbers.first_of_type("work")
        self.assertIsNotNone(phone_number_work)
        self.assertEqual("work", phone_number_work.vtype)
        self.assertEqual("Work", phone_number_work.formatted_type)
        self.assertEqual("+49 40 54637281", phone_number_work.value)
        self.assertEqual("+494054637281", phone_number_work.value_canonical_form)

        self.assertFalse(person.has_changes())

    def test_fail_update_phone_numbers_readonly_formatted_type(self):
        person = self.read_fixture_tester_extensive()
        with self.assertRaises(AttributeError):
            person.phone_numbers.first().formatted_type = "fail"

    def test_fail_update_phone_numbers_readonly_value_canonical_form(self):
        person = self.read_fixture_tester_extensive()
        with self.assertRaises(AttributeError):
            person.phone_numbers.first().value_canonical_form = "fail"

    def test_append_phone_number(self):
        person = self.read_fixture_tester_extensive()
        person.phone_numbers.append_phone_number("created", "+49 89 84629838")
        self.assertEqual(3, len(list(person.phone_numbers.all())))
        self.assertEqual("+49 89 84629838", person.phone_numbers.first_of_type("created").value)
        self.assertTrue(person.has_changes())

    def test_append_phone_number_to_unset_list_attribute(self):
        person = self.read_fixture_tester_empty()
        person.phone_numbers.append_phone_number("created", "+49 40 9384756")
        self.assertEqual(1, len(list(person.phone_numbers.all())))
        self.assertEqual("+49 40 9384756", person.phone_numbers.first_of_type("created").value)
        self.assertTrue(person.has_changes())
