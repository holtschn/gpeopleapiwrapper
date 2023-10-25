import unittest

from gpeopleapiwrapper import persons
from tests import test_persons_base as tpb


class TestPersonWrapperEvents(tpb.FixtureMixin, unittest.TestCase):

    def test_read_event_attributes(self):
        person = self.read_fixture_tester_extensive()
        events = person.events.first()
        self.assertIsNotNone(events)
        self.assertEqual("wedding", events.vtype)
        google_value = events.date_value.google_value()
        self.assertEqual(1966, google_value["year"])
        self.assertEqual(6, google_value["month"])
        self.assertEqual(16, google_value["day"])
        self.assertFalse(person.has_changes())

    def test_append_event(self):
        person = self.read_fixture_tester_extensive()
        value_to_append = persons.DateValue.from_full_date(1978, 6, 14)
        person.events.append_event("anniversary", value_to_append)
        events = list(person.events.all_values())
        self.assertIsNotNone(events)
        self.assertEqual(2, len(events))
        self.assertTrue(value_to_append in events)

    def test_append_event_to_unset_list_attribute(self):
        person = self.read_fixture_tester_empty()
        value_to_append = persons.DateValue.from_full_date(1978, 6, 14)
        person.events.append_event("wedding", value_to_append)
        self.assertEqual(1, len(list(person.events.all())))
        self.assertEqual(value_to_append, person.events.first().date_value)
        self.assertTrue(person.has_changes())
