import unittest

from tests import test_persons_base as tpb


class TestPersonWrapperNames(tpb.FixtureMixin, unittest.TestCase):

    def test_read_names_attributes(self):
        person = TestPersonWrapperNames.read_fixture_tester_extensive()

        names = person.names.first()
        self.assertIsNotNone(names)

        self.assertEqual("Klaus Tester", names.display_name)
        self.assertEqual("Tester, Klaus", names.display_name_last_first)
        self.assertEqual("Klaus Dieter Tester", names.unstructured_name)
        self.assertEqual("Tester", names.family_name)
        self.assertEqual("Klaus", names.given_name)
        self.assertEqual("Dieter", names.middle_name)
        self.assertEqual("Dr.", names.honorific_prefix)
        self.assertEqual("MA", names.honorific_suffix)

    def test_fail_update_names_readonly_display_name(self):
        person = TestPersonWrapperNames.read_fixture_tester_extensive()
        with self.assertRaises(AttributeError):
            person.names.first().display_name = "fail"

    def test_fail_update_names_readonly_display_name_last_first(self):
        person = TestPersonWrapperNames.read_fixture_tester_extensive()
        with self.assertRaises(AttributeError):
            person.names.first().display_name_last_first = "fail"

    def test_update_names_unstructured_name(self):
        person = TestPersonWrapperNames.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        names = person.names.first()
        names.unstructured_name = "[Updated] " + names.unstructured_name
        self.assertEqual("[Updated] Klaus Dieter Tester", person.names.first().unstructured_name)

        self.assertTrue(person.has_changes())

    def test_update_names_family_name(self):
        person = TestPersonWrapperNames.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        names = person.names.first()
        names.family_name = "[Updated] " + names.family_name
        self.assertEqual("[Updated] Tester", person.names.first().family_name)

        self.assertTrue(person.has_changes())

    def test_update_names_given_name(self):
        person = TestPersonWrapperNames.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        names = person.names.first()
        names.given_name = "[Updated] " + names.given_name
        self.assertEqual("[Updated] Klaus", person.names.first().given_name)

        self.assertTrue(person.has_changes())

    def test_update_names_middle_name(self):
        person = TestPersonWrapperNames.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        names = person.names.first()
        names.middle_name = "[Updated] " + names.middle_name
        self.assertEqual("[Updated] Dieter", person.names.first().middle_name)

        self.assertTrue(person.has_changes())

    def test_update_names_honorific_prefix(self):
        person = TestPersonWrapperNames.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        names = person.names.first()
        names.honorific_prefix = "[Updated] " + names.honorific_prefix
        self.assertEqual("[Updated] Dr.", person.names.first().honorific_prefix)

        self.assertTrue(person.has_changes())

    def test_update_names_honorific_suffix(self):
        person = TestPersonWrapperNames.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        names = person.names.first()
        names.honorific_suffix = "[Updated] " + names.honorific_suffix
        self.assertEqual("[Updated] MA", person.names.first().honorific_suffix)

        self.assertTrue(person.has_changes())

    def test_update_names_multiple_attributes(self):
        person = TestPersonWrapperNames.read_fixture_tester_extensive()
        self.assertFalse(person.has_changes())

        names = person.names.first()

        names.unstructured_name = "[Updated] " + names.unstructured_name
        names.family_name = "[Updated] " + names.family_name
        names.given_name = "[Updated] " + names.given_name
        names.middle_name = "[Updated] " + names.middle_name
        names.honorific_prefix = "[Updated] " + names.honorific_prefix
        names.honorific_suffix = "[Updated] " + names.honorific_suffix

        self.assertEqual("[Updated] Klaus Dieter Tester", person.names.first().unstructured_name)
        self.assertEqual("[Updated] Tester", person.names.first().family_name)
        self.assertEqual("[Updated] Klaus", person.names.first().given_name)
        self.assertEqual("[Updated] Dieter", person.names.first().middle_name)
        self.assertEqual("[Updated] Dr.", person.names.first().honorific_prefix)
        self.assertEqual("[Updated] MA", person.names.first().honorific_suffix)

        self.assertTrue(person.has_changes())
