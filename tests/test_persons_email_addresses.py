import unittest

from tests import test_persons_base as tpb


class TestPersonWrapperEmailAddresses(tpb.FixtureMixin, unittest.TestCase):

    def test_read_email_address_attributes(self):
        person = self.read_fixture_tester_extensive()

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

        self.assertFalse(person.has_changes())

    def test_fail_update_email_addresses_readonly_formatted_type(self):
        person = self.read_fixture_tester_extensive()
        with self.assertRaises(AttributeError):
            person.email_addresses.first().formatted_type = "fail"

    def test_append_email_address(self):
        person = self.read_fixture_tester_extensive()
        person.email_addresses.append_email_address("created", "newly.created@example.org")
        self.assertEqual(3, len(list(person.email_addresses.all())))
        self.assertEqual("newly.created@example.org", person.email_addresses.first_of_type("created").value)
        self.assertTrue(person.has_changes())

    def test_append_email_address_to_unset_list_attribute(self):
        person = self.read_fixture_tester_empty()
        person.email_addresses.append_email_address("created", "newly.created@example.org")
        self.assertEqual(1, len(list(person.email_addresses.all())))
        self.assertEqual("newly.created@example.org", person.email_addresses.first_of_type("created").value)
        self.assertTrue(person.has_changes())
