import unittest

from tests import test_persons_base as tpb


class TestPersonWrapperEmailAddresses(tpb.FixtureMixin, unittest.TestCase):

    def test_read_email_addresses_attributes(self):
        person = TestPersonWrapperEmailAddresses.read_fixture_tester_extensive()

        email_address_home = person.email_addresses.first_of_type("home")
        self.assertIsNotNone(email_address_home)

        self.assertEqual("home", email_address_home.vtype)
        self.assertEqual("Home", email_address_home.formatted_type)
        self.assertEqual("klaus.tester@example.com", email_address_home.value)

        email_addresses_work = person.email_addresses.first_of_type("work")
        self.assertIsNotNone(email_addresses_work)

        self.assertEqual("work", email_addresses_work.vtype)
        self.assertEqual("Work", email_addresses_work.formatted_type)
        self.assertEqual("k.tester@company.de", email_addresses_work.value)

    def test_read_no_email_address_for_type_available(self):
        person = TestPersonWrapperEmailAddresses.read_fixture_tester_extensive()

        email_address_unavail = person.email_addresses.first_of_type("unavail")
        self.assertIsNone(email_address_unavail)

        self.assertFalse(person.has_changes())

    def test_read_all_email_address_values(self):
        person = TestPersonWrapperEmailAddresses.read_fixture_tester_extensive()

        self.assertEqual(2, len(list(person.email_addresses.all())))

        email_address_values = list(person.email_addresses.all_values())
        self.assertEqual(2, len(email_address_values))

        self.assertIn("k.tester@company.de", email_address_values)
        self.assertIn("klaus.tester@example.com", email_address_values)

    def test_fail_update_email_addresses_readonly_formatted_type(self):
        person = TestPersonWrapperEmailAddresses.read_fixture_tester_extensive()
        with self.assertRaises(AttributeError):
            person.email_addresses.first().formatted_type = "fail"

    def test_update_email_addresses_type(self):
        person = TestPersonWrapperEmailAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        email_address = person.email_addresses.first_of_type("home")
        email_address.vtype = "[Updated] " + email_address.vtype
        self.assertIsNotNone(person.email_addresses.first_of_type("[Updated] home"))
        self.assertEqual("[Updated] home", person.email_addresses.first_of_type("[Updated] home").vtype)

        self.assertTrue(person.has_changes())

    def test_update_email_addresses_value(self):
        person = TestPersonWrapperEmailAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        email_address = person.email_addresses.first_of_type("work")
        email_address.value = "[Updated] " + email_address.value
        self.assertEqual("[Updated] k.tester@company.de", person.email_addresses.first_of_type("work").value)

        self.assertTrue(person.has_changes())

    def test_append_email_address(self):
        person = TestPersonWrapperEmailAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        person.email_addresses.append_email_address("created", "newly.created@example.org")

        self.assertEqual(3, len(list(person.email_addresses.all())))
        self.assertEqual("newly.created@example.org", person.email_addresses.first_of_type("created").value)

        self.assertTrue(person.has_changes())

    def test_remove_email_address(self):
        person = TestPersonWrapperEmailAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        person.email_addresses.remove_by_value("klaus.tester@example.com")

        self.assertEqual(1, len(list(person.email_addresses.all())))
        self.assertEqual("k.tester@company.de", person.email_addresses.first().value)

        self.assertTrue(person.has_changes())

    def test_append_email_address_to_unset_attribute(self):
        person = TestPersonWrapperEmailAddresses.read_fixture_tester_empty()
        self.assertFalse(person.has_changes())

        person.email_addresses.append_email_address("created", "newly.created@example.org")

        self.assertEqual(1, len(list(person.email_addresses.all())))
        self.assertEqual("newly.created@example.org", person.email_addresses.first_of_type("created").value)

        self.assertTrue(person.has_changes())
