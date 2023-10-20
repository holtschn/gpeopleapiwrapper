import unittest

from tests import test_persons_base as tpb


class TestPersonWrapperPhoneNumbers(tpb.FixtureMixin, unittest.TestCase):

    def test_read_phone_numbers_attributes(self):
        person = TestPersonWrapperPhoneNumbers.read_fixture_tester_extensive()

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

    def test_read_no_phone_number_for_type_available(self):
        person = TestPersonWrapperPhoneNumbers.read_fixture_tester_extensive()

        phone_number_unavail = person.phone_numbers.first_of_type("unavail")
        self.assertIsNone(phone_number_unavail)

        self.assertFalse(person.has_changes())

    def test_read_all_phone_number_values(self):
        person = TestPersonWrapperPhoneNumbers.read_fixture_tester_extensive()

        self.assertEqual(2, len(list(person.phone_numbers.all())))

        phone_number_values = list(person.phone_numbers.all_values())
        self.assertEqual(2, len(phone_number_values))

        self.assertIn("+49 40 54637281", phone_number_values)
        self.assertIn("+49 40 9384756", phone_number_values)

    def test_fail_update_phone_numbers_readonly_formatted_type(self):
        person = TestPersonWrapperPhoneNumbers.read_fixture_tester_extensive()
        with self.assertRaises(AttributeError):
            person.phone_numbers.first().formatted_type = "fail"

    def test_fail_update_phone_numbers_readonly_value_canonical_form(self):
        person = TestPersonWrapperPhoneNumbers.read_fixture_tester_extensive()
        with self.assertRaises(AttributeError):
            person.phone_numbers.first().value_canonical_form = "fail"

    def test_update_phone_numbers_type(self):
        person = TestPersonWrapperPhoneNumbers.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        phone_number = person.phone_numbers.first_of_type("home")
        phone_number.vtype = "[Updated] " + phone_number.vtype
        self.assertIsNotNone(person.phone_numbers.first_of_type("[Updated] home"))
        self.assertEqual("[Updated] home", person.phone_numbers.first_of_type("[Updated] home").vtype)

        self.assertTrue(person.has_changes())

    def test_update_phone_numbers_value(self):
        person = TestPersonWrapperPhoneNumbers.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        phone_number = person.phone_numbers.first_of_type("work")
        phone_number.value = "[Updated] " + phone_number.value
        self.assertEqual("[Updated] +49 40 54637281", person.phone_numbers.first_of_type("work").value)

        self.assertTrue(person.has_changes())

    def test_append_phone_number(self):
        person = TestPersonWrapperPhoneNumbers.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        person.phone_numbers.append_phone_number("created", "+49 89 84629838")

        self.assertEqual(3, len(list(person.phone_numbers.all())))
        self.assertEqual("+49 89 84629838", person.phone_numbers.first_of_type("created").value)

        self.assertTrue(person.has_changes())

    def test_remove_phone_number(self):
        person = TestPersonWrapperPhoneNumbers.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        person.phone_numbers.remove_by_value("+49 40 54637281")

        self.assertEqual(1, len(list(person.phone_numbers.all())))
        self.assertEqual("+49 40 9384756", person.phone_numbers.first().value)

        self.assertTrue(person.has_changes())

    def test_append_phone_number_to_unset_attribute(self):
        person = TestPersonWrapperPhoneNumbers.read_fixture_tester_empty()
        self.assertFalse(person.has_changes())

        person.phone_numbers.append_phone_number("created", "+49 40 9384756")

        self.assertEqual(1, len(list(person.phone_numbers.all())))
        self.assertEqual("+49 40 9384756", person.phone_numbers.first_of_type("created").value)

        self.assertTrue(person.has_changes())
