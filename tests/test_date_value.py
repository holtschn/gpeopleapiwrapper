import unittest
from datetime import date, datetime

from gpeopleapiwrapper import persons


class TestDateValue(unittest.TestCase):

    def test_create_from_full_date(self):
        date_value = persons.DateValue.from_full_date(2023, 10, 15)

        self.assertIsNotNone(date_value)

        google_value = date_value.google_value()
        self.assertEqual(2023, google_value["year"])
        self.assertEqual(10, google_value["month"])
        self.assertEqual(15, google_value["day"])

    def test_create_from_date_object(self):
        date_object = date(2023, 10, 16)
        date_value = persons.DateValue.from_date(date_object)

        self.assertIsNotNone(date_value)

        google_value = date_value.google_value()
        self.assertEqual(2023, google_value["year"])
        self.assertEqual(10, google_value["month"])
        self.assertEqual(16, google_value["day"])

    def test_create_from_datetime_object(self):
        datetime_object = datetime(2023, 10, 17, 12, 30, 15)
        date_value = persons.DateValue.from_datetime(datetime_object)

        self.assertIsNotNone(date_value)

        google_value = date_value.google_value()
        self.assertEqual(2023, google_value["year"])
        self.assertEqual(10, google_value["month"])
        self.assertEqual(17, google_value["day"])

    def test_create_from_month_day(self):
        date_value = persons.DateValue.from_month_day(8, 24)

        self.assertIsNotNone(date_value)

        google_value = date_value.google_value()
        self.assertEqual(0, google_value["year"])
        self.assertEqual(8, google_value["month"])
        self.assertEqual(24, google_value["day"])

    def test_create_from_year_month(self):
        date_value = persons.DateValue.from_year_month(2022, 6)

        self.assertIsNotNone(date_value)

        google_value = date_value.google_value()
        self.assertEqual(2022, google_value["year"])
        self.assertEqual(6, google_value["month"])
        self.assertEqual(0, google_value["day"])

    def test_create_from_year_only(self):
        date_value = persons.DateValue.from_year_only(1916)

        self.assertIsNotNone(date_value)

        google_value = date_value.google_value()
        self.assertEqual(1916, google_value["year"])
        self.assertEqual(0, google_value["month"])
        self.assertEqual(0, google_value["day"])

    def test_non_object_str_and_repr(self):
        date_value = persons.DateValue.from_full_date(1998, 10, 15)

        self.assertTrue("1998" in str(date_value))
        self.assertTrue("10" in str(date_value))
        self.assertTrue("15" in str(date_value))

        self.assertFalse("<" in str(date_value))
        self.assertFalse(">" in str(date_value))

        self.assertTrue("1998" in repr(date_value))
        self.assertTrue("10" in repr(date_value))
        self.assertTrue("15" in repr(date_value))

        self.assertFalse("<" in repr(date_value))
        self.assertFalse(">" in repr(date_value))

    def test_equality_full_date(self):
        left_date = persons.DateValue.from_full_date(2019, 3, 17)
        right_date = persons.DateValue.from_full_date(2019, 3, 17)

        self.assertEqual(left_date, right_date)
        self.assertEqual(left_date.__hash__(), right_date.__hash__())

    def test_non_equality_full_date(self):
        left_date = persons.DateValue.from_full_date(2019, 3, 17)
        right_date_day = persons.DateValue.from_full_date(2019, 3, 16)
        right_date_month = persons.DateValue.from_full_date(2019, 4, 17)
        right_date_year = persons.DateValue.from_full_date(2018, 3, 17)

        self.assertNotEqual(left_date, right_date_day)
        self.assertNotEqual(left_date, right_date_month)
        self.assertNotEqual(left_date, right_date_year)

    def test_non_equality_different_types(self):
        full_date = persons.DateValue.from_full_date(1978, 1, 14)
        year_only = persons.DateValue.from_year_only(1978)
        year_month = persons.DateValue.from_year_month(1978, 1)
        month_day = persons.DateValue.from_month_day(1, 14)

        self.assertNotEqual(full_date, year_only)
        self.assertNotEqual(full_date, year_month)
        self.assertNotEqual(full_date, month_day)
        self.assertNotEqual(year_only, full_date)
        self.assertNotEqual(year_only, year_month)
        self.assertNotEqual(year_only, month_day)
        self.assertNotEqual(year_month, full_date)
        self.assertNotEqual(year_month, year_only)
        self.assertNotEqual(year_month, month_day)
        self.assertNotEqual(month_day, full_date)
        self.assertNotEqual(month_day, year_only)
        self.assertNotEqual(month_day, year_month)

    def test_non_equality_with_none(self):
        full_date = persons.DateValue.from_full_date(1978, 1, 14)
        year_only = persons.DateValue.from_year_only(1978)
        year_month = persons.DateValue.from_year_month(1978, 1)
        month_day = persons.DateValue.from_month_day(1, 14)

        self.assertNotEqual(full_date, None)
        self.assertNotEqual(year_only, None)
        self.assertNotEqual(year_month, None)
        self.assertNotEqual(month_day, None)

    def test_non_equality_with_other_object(self):
        full_date = persons.DateValue.from_full_date(1978, 1, 14)
        self.assertNotEqual(full_date, "fail")

    def test_visit_full_date(self):
        class TestVisitorFullDate(persons.DateValueVisitor):

            def __init__(self, test_case: unittest.TestCase):
                self.__test_case = test_case
                self.visited = False

            def visit_full_date(self, full_date: date):
                self.__test_case.assertEqual(2019, full_date.year)
                self.__test_case.assertEqual(9, full_date.month)
                self.__test_case.assertEqual(3, full_date.day)
                self.visited = True

            def visit_without_year(self, month: int, day: int):
                self.__test_case.fail("Should not be visited!")

            def visit_year_only(self, year: int):
                self.__test_case.fail("Should not be visited!")

            def visit_without_day(self, year: int, month: int):
                self.__test_case.fail("Should not be visited!")

        test_date = persons.DateValue.from_full_date(2019, 9, 3)
        test_visitor = TestVisitorFullDate(self)
        test_date.visit_value(test_visitor)
        self.assertTrue(test_visitor.visited)

    def test_visit_year_only(self):
        class TestVisitorYearOnly(persons.DateValueVisitor):

            def __init__(self, test_case: unittest.TestCase):
                self.__test_case = test_case
                self.visited = False

            def visit_full_date(self, full_date: date):
                self.__test_case.fail("Should not be visited!")

            def visit_without_year(self, month: int, day: int):
                self.__test_case.fail("Should not be visited!")

            def visit_year_only(self, year: int):
                self.__test_case.assertEqual(2019, year)
                self.visited = True

            def visit_without_day(self, year: int, month: int):
                self.__test_case.fail("Should not be visited!")

        test_date = persons.DateValue.from_year_only(2019)
        test_visitor = TestVisitorYearOnly(self)
        test_date.visit_value(test_visitor)
        self.assertTrue(test_visitor.visited)

    def test_visit_year_month(self):
        class TestVisitorYearMonth(persons.DateValueVisitor):

            def __init__(self, test_case: unittest.TestCase):
                self.__test_case = test_case
                self.visited = False

            def visit_full_date(self, full_date: date):
                self.__test_case.fail("Should not be visited!")

            def visit_without_year(self, month: int, day: int):
                self.__test_case.fail("Should not be visited!")

            def visit_year_only(self, year: int):
                self.__test_case.fail("Should not be visited!")

            def visit_without_day(self, year: int, month: int):
                self.__test_case.assertEqual(2019, year)
                self.__test_case.assertEqual(9, month)
                self.visited = True

        test_date = persons.DateValue.from_year_month(2019, 9)
        test_visitor = TestVisitorYearMonth(self)
        test_date.visit_value(test_visitor)
        self.assertTrue(test_visitor.visited)

    def test_visit_month_day(self):
        class TestVisitorMonthDay(persons.DateValueVisitor):

            def __init__(self, test_case: unittest.TestCase):
                self.__test_case = test_case
                self.visited = False

            def visit_full_date(self, full_date: date):
                self.__test_case.fail("Should not be visited!")

            def visit_without_year(self, month: int, day: int):
                self.__test_case.assertEqual(9, month)
                self.__test_case.assertEqual(3, day)
                self.visited = True

            def visit_year_only(self, year: int):
                self.__test_case.fail("Should not be visited!")

            def visit_without_day(self, year: int, month: int):
                self.__test_case.fail("Should not be visited!")

        test_date = persons.DateValue.from_month_day(9, 3)
        test_visitor = TestVisitorMonthDay(self)
        test_date.visit_value(test_visitor)
        self.assertTrue(test_visitor.visited)
