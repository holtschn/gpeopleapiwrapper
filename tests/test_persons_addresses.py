import unittest

from tests import test_persons_base as tpb


class TestPersonWrapperAddresses(tpb.FixtureMixin, unittest.TestCase):

    def test_read_addresses_attributes(self):
        person = TestPersonWrapperAddresses.read_fixture_tester_extensive()

        addresses = person.addresses
        self.assertIsNotNone(addresses)

        self.assertIsNotNone(addresses.all())
        address_list = list(addresses.all())
        self.assertEqual(2, len(address_list))

        self.assertIsNotNone(address_list[0].vtype)
        self.assertIsNotNone(address_list[1].vtype)

        address_home = addresses.first_of_type("home")
        address_work = addresses.first_of_type("work")

        self.assertIsNotNone(address_home)
        self.assertEqual("Üncodingweg 30\nHamburg 22765\nGermany", address_home.formatted)
        self.assertEqual("Home", address_home.formatted_type)
        self.assertEqual("no home box", address_home.po_box)
        self.assertEqual("Üncodingweg 30", address_home.street_address)
        self.assertEqual("Stock Tür Stiege", address_home.extended_address)
        self.assertEqual("Bremen", address_home.city)
        self.assertEqual("Land Bremen", address_home.region)
        self.assertEqual("28195", address_home.postal_code)
        self.assertEqual("Germany", address_home.country)
        self.assertEqual("DE", address_home.country_code)

        self.assertIsNotNone(address_work)
        self.assertEqual("Teststraße 18\nHamburg 22765\nGermany", address_work.formatted)
        self.assertEqual("Work", address_work.formatted_type)
        self.assertEqual("no work box", address_work.po_box)
        self.assertEqual("Teststraße 18", address_work.street_address)
        self.assertEqual("Stiege Stock Tür", address_work.extended_address)
        self.assertEqual("Hamburg", address_work.city)
        self.assertEqual("Land Hamburg", address_work.region)
        self.assertEqual("22765", address_work.postal_code)
        self.assertEqual("Germany", address_work.country)
        self.assertEqual("DE", address_work.country_code)

    def test_fail_update_addresses_readonly_formatted(self):
        address_home = TestPersonWrapperAddresses.read_fixture_tester_extensive().addresses.first_of_type("home")
        self.assertIsNotNone(address_home)
        with self.assertRaises(AttributeError):
            address_home.formatted = "fail"

    def test_fail_update_addresses_readonly_formatted_type(self):
        address_home = TestPersonWrapperAddresses.read_fixture_tester_extensive().addresses.first_of_type("home")
        self.assertIsNotNone(address_home)
        with self.assertRaises(AttributeError):
            address_home.formatted_type = "fail"

    def test_update_addresses_type(self):
        person = TestPersonWrapperAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        address = person.addresses.first_of_type("home")
        address.vtype = "[Updated] " + address.vtype
        self.assertIsNotNone(person.addresses.first_of_type("[Updated] home"))
        self.assertEqual("[Updated] home", person.addresses.first_of_type("[Updated] home").vtype)

        self.assertTrue(person.has_changes())

    def test_update_addresses_po_box(self):
        person = TestPersonWrapperAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        address = person.addresses.first_of_type("home")
        address.po_box = "[Updated] " + address.po_box
        self.assertEqual("[Updated] no home box", person.addresses.first_of_type("home").po_box)

        self.assertTrue(person.has_changes())

    def test_update_addresses_street_address(self):
        person = TestPersonWrapperAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        address = person.addresses.first_of_type("home")
        address.street_address = "[Updated] " + address.street_address
        self.assertEqual("[Updated] Üncodingweg 30", person.addresses.first_of_type("home").street_address)

        self.assertTrue(person.has_changes())

    def test_update_addresses_extended_address(self):
        person = TestPersonWrapperAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        address = person.addresses.first_of_type("home")
        address.extended_address = "[Updated] " + address.extended_address
        self.assertEqual("[Updated] Stock Tür Stiege", person.addresses.first_of_type("home").extended_address)

        self.assertTrue(person.has_changes())

    def test_update_addresses_city(self):
        person = TestPersonWrapperAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        address = person.addresses.first_of_type("home")
        address.city = "[Updated] " + address.city
        self.assertEqual("[Updated] Bremen", person.addresses.first_of_type("home").city)

        self.assertTrue(person.has_changes())

    def test_update_addresses_region(self):
        person = TestPersonWrapperAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        address = person.addresses.first_of_type("home")
        address.region = "[Updated] " + address.region
        self.assertEqual("[Updated] Land Bremen", person.addresses.first_of_type("home").region)

        self.assertTrue(person.has_changes())

    def test_update_addresses_postal_code(self):
        person = TestPersonWrapperAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        address = person.addresses.first_of_type("home")
        address.postal_code = "[Updated] " + address.postal_code
        self.assertEqual("[Updated] 28195", person.addresses.first_of_type("home").postal_code)

        self.assertTrue(person.has_changes())

    def test_update_addresses_country(self):
        person = TestPersonWrapperAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        address = person.addresses.first_of_type("home")
        address.country = "[Updated] " + address.country
        self.assertEqual("[Updated] Germany", person.addresses.first_of_type("home").country)

        self.assertTrue(person.has_changes())

    def test_update_addresses_country_code(self):
        person = TestPersonWrapperAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        address = person.addresses.first_of_type("home")
        address.country_code = "[Updated] " + address.country_code
        self.assertEqual("[Updated] DE", person.addresses.first_of_type("home").country_code)

        self.assertTrue(person.has_changes())

    def test_update_addresses_multiple_attributes(self):
        person = TestPersonWrapperAddresses.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        address = person.addresses.first_of_type("work")

        address.po_box = "[Updated] " + address.po_box
        address.street_address = "[Updated] " + address.street_address
        address.extended_address = "[Updated] " + address.extended_address
        address.city = "[Updated] " + address.city
        address.region = "[Updated] " + address.region
        address.postal_code = "[Updated] " + address.postal_code
        address.country = "[Updated] " + address.country
        address.country_code = "[Updated] " + address.country_code

        self.assertEqual("[Updated] no work box", person.addresses.first_of_type("work").po_box)
        self.assertEqual("[Updated] Teststraße 18", person.addresses.first_of_type("work").street_address)
        self.assertEqual("[Updated] Stiege Stock Tür", person.addresses.first_of_type("work").extended_address)
        self.assertEqual("[Updated] Hamburg", person.addresses.first_of_type("work").city)
        self.assertEqual("[Updated] Land Hamburg", person.addresses.first_of_type("work").region)
        self.assertEqual("[Updated] 22765", person.addresses.first_of_type("work").postal_code)
        self.assertEqual("[Updated] Germany", person.addresses.first_of_type("work").country)
        self.assertEqual("[Updated] DE", person.addresses.first_of_type("work").country_code)

        self.assertTrue(person.has_changes())
