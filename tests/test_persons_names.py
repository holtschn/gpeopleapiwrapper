import unittest

from gpeopleapiwrapper import persons
from tests import test_persons_base as tpb


class TestPersonWrapperNames(tpb.FixtureMixin, unittest.TestCase):

    def _check_extensive_names(self, names: persons.NameWrapper | persons.NamesWrapper):
        self.assertEqual("Klaus Tester", names.display_name)
        self.assertEqual("Tester, Klaus", names.display_name_last_first)
        self.assertEqual("Klaus Dieter Tester", names.unstructured_name)
        self.assertEqual("Tester", names.family_name)
        self.assertEqual("Klaus", names.given_name)
        self.assertEqual("Dieter", names.middle_name)
        self.assertEqual("Dr.", names.honorific_prefix)
        self.assertEqual("MA", names.honorific_suffix)

    def test_read_names_attributes(self):
        person = self.read_fixture_tester_extensive()
        names = person.names.first()
        self.assertIsNotNone(names)
        self._check_extensive_names(names)
        self.assertFalse(person.has_changes())

    def test_read_names_attributes_convenience(self):
        person = self.read_fixture_tester_extensive()
        names = person.names
        self.assertIsNotNone(names)
        self._check_extensive_names(names)
        self.assertFalse(person.has_changes())

    def test_fail_update_names_readonly_display_name(self):
        person = self.read_fixture_tester_extensive()
        with self.assertRaises(AttributeError):
            person.names.first().display_name = "fail"

    def test_fail_update_names_readonly_display_name_last_first(self):
        person = self.read_fixture_tester_extensive()
        with self.assertRaises(AttributeError):
            person.names.first().display_name_last_first = "fail"

    def _check_update_names_attribute(self,
                                      attribute: str,
                                      use_convenience: bool = False,
                                      use_empty: bool = False):
        person = self.read_fixture_tester_empty() if use_empty else self.read_fixture_tester_extensive()

        names_to_update = person.names if use_convenience else person.names.first()
        initial_value = getattr(names_to_update, attribute)
        target_value = "[Updated] " + (initial_value if initial_value else "")
        setattr(names_to_update, attribute, target_value)

        names_to_check = person.names.first()
        self.assertEqual(target_value, getattr(names_to_check, attribute))
        names_to_check_convenience = person.names
        self.assertEqual(target_value, getattr(names_to_check_convenience, attribute))
        self.assertTrue(person.has_changes())

    def _check_update_names_attribute_situations(self, attribute: str):
        self._check_update_names_attribute(attribute=attribute, use_convenience=False, use_empty=False)
        self._check_update_names_attribute(attribute=attribute, use_convenience=True, use_empty=False)
        self._check_update_names_attribute(attribute=attribute, use_convenience=True, use_empty=True)

    def test_update_names_unstructured_name(self):
        self._check_update_names_attribute_situations("unstructured_name")

    def test_update_names_family_name(self):
        self._check_update_names_attribute_situations("family_name")

    def test_update_names_given_name(self):
        self._check_update_names_attribute_situations("given_name")

    def test_update_names_middle_name(self):
        self._check_update_names_attribute_situations("middle_name")

    def test_update_names_honorific_prefix(self):
        self._check_update_names_attribute_situations("honorific_prefix")

    def test_update_names_honorific_suffix(self):
        self._check_update_names_attribute_situations("honorific_suffix")

    def test_update_names_multiple_attributes(self):
        person = self.read_fixture_tester_extensive()
        names = person.names.first()

        names.unstructured_name = "[Changed] " + names.unstructured_name
        names.family_name = "[Changed] " + names.family_name
        names.given_name = "[Changed] " + names.given_name
        names.middle_name = "[Changed] " + names.middle_name
        names.honorific_prefix = "[Changed] " + names.honorific_prefix
        names.honorific_suffix = "[Changed] " + names.honorific_suffix

        self.assertEqual("[Changed] Klaus Dieter Tester", person.names.first().unstructured_name)
        self.assertEqual("[Changed] Tester", person.names.first().family_name)
        self.assertEqual("[Changed] Klaus", person.names.first().given_name)
        self.assertEqual("[Changed] Dieter", person.names.first().middle_name)
        self.assertEqual("[Changed] Dr.", person.names.first().honorific_prefix)
        self.assertEqual("[Changed] MA", person.names.first().honorific_suffix)

        self.assertTrue(person.has_changes())

    def test_fail_on_adding_second_names(self):
        person = self.read_fixture_tester_extensive()
        with self.assertRaises(ValueError):
            person.names._append_to_model({"displayName": "Eva Tester"})
