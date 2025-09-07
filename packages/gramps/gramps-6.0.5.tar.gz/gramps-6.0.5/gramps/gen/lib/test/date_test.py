#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007 Donald N. Allingham
# Copyright (C) 2013-2014  Vassilii Khachaturov
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Unittest for testing dates"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...config import config
from ...datehandler import displayer as _dd
from ...datehandler import get_date_formats
from ...datehandler import parser as _dp
from ...datehandler import set_format
from ...datehandler._datedisplay import DateDisplayEn
from ...lib.date import Date, DateError, Span, Today, calendar_has_fixed_newyear

date_tests = {}

# first the "basics".
testset = "basic test"
dates = []
calendar = Date.CAL_GREGORIAN
for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, Date.QUAL_CALCULATED):
    for modifier in (
        Date.MOD_NONE,
        Date.MOD_BEFORE,
        Date.MOD_AFTER,
        Date.MOD_ABOUT,
        Date.MOD_FROM,
        Date.MOD_TO,
    ):
        for month in range(1, 13):
            d = Date()
            d.set(
                quality,
                modifier,
                calendar,
                (4, month, 1789, False),
                "Text comment",
            )
            dates.append(d)
    for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
        for month1 in range(1, 13):
            for month2 in range(1, 13):
                d = Date()
                d.set(
                    quality,
                    modifier,
                    calendar,
                    (4, month1, 1789, False, 5, month2, 1876, False),
                    "Text comment",
                )
                dates.append(d)
    modifier = Date.MOD_TEXTONLY
    d = Date()
    d.set(quality, modifier, calendar, Date.EMPTY, "This is a textual date")
    dates.append(d)
date_tests[testset] = dates

# incomplete dates (day or month missing)
testset = "partial date"
dates = []
calendar = Date.CAL_GREGORIAN
for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, Date.QUAL_CALCULATED):
    for modifier in (
        Date.MOD_NONE,
        Date.MOD_BEFORE,
        Date.MOD_AFTER,
        Date.MOD_ABOUT,
        Date.MOD_FROM,
        Date.MOD_TO,
    ):
        d = Date()
        d.set(quality, modifier, calendar, (0, 11, 1789, False), "Text comment")
        dates.append(d)
        d = Date()
        d.set(quality, modifier, calendar, (0, 0, 1789, False), "Text comment")
        dates.append(d)
    for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
        d = Date()
        d.set(
            quality,
            modifier,
            calendar,
            (4, 10, 1789, False, 0, 11, 1876, False),
            "Text comment",
        )
        dates.append(d)
        d = Date()
        d.set(
            quality,
            modifier,
            calendar,
            (4, 10, 1789, False, 0, 0, 1876, False),
            "Text comment",
        )
        dates.append(d)
        d = Date()
        d.set(
            quality,
            modifier,
            calendar,
            (0, 10, 1789, False, 5, 11, 1876, False),
            "Text comment",
        )
        dates.append(d)
        d = Date()
        d.set(
            quality,
            modifier,
            calendar,
            (0, 10, 1789, False, 0, 11, 1876, False),
            "Text comment",
        )
        dates.append(d)
        d = Date()
        d.set(
            quality,
            modifier,
            calendar,
            (0, 10, 1789, False, 0, 0, 1876, False),
            "Text comment",
        )
        dates.append(d)
        d = Date()
        d.set(
            quality,
            modifier,
            calendar,
            (0, 0, 1789, False, 5, 11, 1876, False),
            "Text comment",
        )
        dates.append(d)
        d = Date()
        d.set(
            quality,
            modifier,
            calendar,
            (0, 0, 1789, False, 0, 11, 1876, False),
            "Text comment",
        )
        dates.append(d)
        d = Date()
        d.set(
            quality,
            modifier,
            calendar,
            (0, 0, 1789, False, 0, 0, 1876, False),
            "Text comment",
        )
        dates.append(d)
date_tests[testset] = dates

# slash-dates
testset = "slash-dates"
dates = []
calendar = Date.CAL_GREGORIAN
for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, Date.QUAL_CALCULATED):
    for modifier in (
        Date.MOD_NONE,
        Date.MOD_BEFORE,
        Date.MOD_AFTER,
        Date.MOD_ABOUT,
        Date.MOD_FROM,
        Date.MOD_TO,
    ):
        # normal date
        d = Date()
        d.set(quality, modifier, calendar, (4, 11, 1789, True), "Text comment")
        dates.append(d)
    for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
        d = Date()
        d.set(
            quality,
            modifier,
            calendar,
            (4, 11, 1789, True, 5, 10, 1876, False),
            "Text comment",
        )
        dates.append(d)
        d = Date()
        d.set(
            quality,
            modifier,
            calendar,
            (4, 11, 1789, False, 5, 10, 1876, True),
            "Text comment",
        )
        dates.append(d)
        d = Date()
        d.set(
            quality,
            modifier,
            calendar,
            (4, 11, 1789, True, 5, 10, 1876, True),
            "Text comment",
        )
        dates.append(d)
date_tests[testset] = dates

# BCE
testset = "B. C. E."
dates = []
calendar = Date.CAL_GREGORIAN
for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, Date.QUAL_CALCULATED):
    for modifier in (
        Date.MOD_NONE,
        Date.MOD_BEFORE,
        Date.MOD_AFTER,
        Date.MOD_ABOUT,
        Date.MOD_FROM,
        Date.MOD_TO,
    ):
        # normal date
        d = Date()
        d.set(quality, modifier, calendar, (4, 11, -90, False), "Text comment")
        dates.append(d)
    for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
        d = Date()
        d.set(
            quality,
            modifier,
            calendar,
            (5, 10, -90, False, 4, 11, -90, False),
            "Text comment",
        )
        dates.append(d)
date_tests[testset] = dates

# test for all other different calendars
testset = "Non-gregorian"
dates = []
for calendar in (
    Date.CAL_JULIAN,
    Date.CAL_HEBREW,
    Date.CAL_ISLAMIC,
    Date.CAL_FRENCH,
    Date.CAL_PERSIAN,
):
    for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, Date.QUAL_CALCULATED):
        for modifier in (
            Date.MOD_NONE,
            Date.MOD_BEFORE,
            Date.MOD_AFTER,
            Date.MOD_ABOUT,
            Date.MOD_FROM,
            Date.MOD_TO,
        ):
            d = Date()
            d.set(
                quality,
                modifier,
                calendar,
                (4, 11, 1789, False),
                "Text comment",
            )
            dates.append(d)
        for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
            d = Date()
            d.set(
                quality,
                modifier,
                calendar,
                (4, 10, 1789, False, 5, 11, 1876, False),
                "Text comment",
            )
            dates.append(d)


# CAL_SWEDISH    - Swedish calendar 1700-03-01 -> 1712-02-30!
class Context:
    def __init__(self, retval):
        self.retval = retval

    def __enter__(self):
        return self.retval

    def __exit__(self, *args, **kwargs):
        pass


with Context(Date.CAL_SWEDISH) as calendar:
    for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, Date.QUAL_CALCULATED):
        for modifier in (
            Date.MOD_NONE,
            Date.MOD_BEFORE,
            Date.MOD_AFTER,
            Date.MOD_ABOUT,
            Date.MOD_FROM,
            Date.MOD_TO,
        ):
            d = Date()
            d.set(
                quality,
                modifier,
                calendar,
                (4, 11, 1700, False),
                "Text comment",
            )
            dates.append(d)
        for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
            d = Date()
            d.set(
                quality,
                modifier,
                calendar,
                (4, 10, 1701, False, 5, 11, 1702, False),
                "Text comment",
            )
            dates.append(d)

quality = Date.QUAL_NONE
modifier = Date.MOD_NONE
for calendar in (
    Date.CAL_JULIAN,
    Date.CAL_ISLAMIC,
    Date.CAL_PERSIAN,
):
    for month in range(1, 13):
        d = Date()
        d.set(quality, modifier, calendar, (4, month, 1789, False), "Text comment")
        dates.append(d)

for calendar in (Date.CAL_HEBREW, Date.CAL_FRENCH):
    for month in range(1, 14):
        d = Date()
        d.set(quality, modifier, calendar, (4, month, 1789, False), "Text comment")
        dates.append(d)

date_tests[testset] = dates

swedish_dates = []
# CAL_SWEDISH    - Swedish calendar 1700-03-01 -> 1712-02-30!
with Context(Date.CAL_SWEDISH) as calendar:
    for year in range(1701, 1712):
        for month in range(1, 13):
            d = Date()
            d.set(
                quality,
                modifier,
                calendar,
                (4, month, year, False),
                "Text comment",
            )
            swedish_dates.append(d)


# -------------------------------------------------------------------------
#
# BaseDateTest
#
# -------------------------------------------------------------------------
class BaseDateTest(unittest.TestCase):
    """
    Base class for all date tests.
    """

    def setUp(self):
        config.set("behavior.date-before-range", 9999)
        config.set("behavior.date-after-range", 9999)
        config.set("behavior.date-about-range", 10)


# -------------------------------------------------------------------------
#
# ParserDateTest
#
# -------------------------------------------------------------------------
class ParserDateTest(BaseDateTest):
    """
    Date displayer and parser tests.
    """

    def do_case(self, testset):
        for index, date_format in enumerate(get_date_formats()):
            set_format(index)

            for dateval in date_tests[testset]:
                datestr = _dd.display(dateval)
                ndate = _dp.parse(datestr)
                self.assertTrue(
                    dateval.is_equal(ndate),
                    "dateval fails is_equal in format %d:\n"
                    "   '%s' != '%s'\n"
                    "   '%s' != '%s'\n"
                    % (index, dateval, ndate, dateval.__dict__, ndate.__dict__),
                )

    def test_basic(self):
        self.do_case("basic test")

    def test_partial(self):
        self.do_case("partial date")

    def test_slash(self):
        self.do_case("slash-dates")

    def test_bce(self):
        self.do_case("B. C. E.")

    def test_non_gregorian(self):
        self.do_case("Non-gregorian")


# -------------------------------------------------------------------------
#
# MatchDateTest
#
# -------------------------------------------------------------------------
ENGLISH_DATE_HANDLER = _dd.__class__ == DateDisplayEn


@unittest.skipUnless(
    ENGLISH_DATE_HANDLER,
    "This test of Date() matching logic can only run in US-English locale.",
)
class MatchDateTest(BaseDateTest):
    """
    Date match tests.
    """

    tests = [
        ("before 1960", "before 1961", True),
        ("before 1960", "before 1960", True),
        ("before 1961", "before 1961", True),
        ("jan 1, 1960", "jan 1, 1960", True),
        ("dec 31, 1959", "dec 31, 1959", True),
        ("before 1960", "jan 1, 1960", False),
        ("before 1960", "dec 31, 1959", True),
        ("abt 1960", "1960", True),
        ("abt 1960", "before 1960", True),
        ("1960", "1960", True),
        ("1960", "after 1960", False),
        ("1960", "before 1960", False),
        ("abt 1960", "abt 1960", True),
        ("before 1960", "after 1960", False),
        ("after jan 1, 1900", "jan 2, 1900", True),
        ("abt jan 1, 1900", "jan 1, 1900", True),
        ("from 1950 to 1955", "1950", True),
        ("from 1950 to 1955", "1951", True),
        ("from 1950 to 1955", "1952", True),
        ("from 1950 to 1955", "1953", True),
        ("from 1950 to 1955", "1954", True),
        ("from 1950 to 1955", "1955", True),
        ("from 1950 to 1955", "1956", False),
        ("from 1950 to 1955", "dec 31, 1955", True),
        ("from 1950 to 1955", "jan 1, 1955", True),
        ("from 1950 to 1955", "dec 31, 1949", False),
        ("from 1950 to 1955", "jan 1, 1956", False),
        ("from 1950", "1940", False),
        ("from 1950", "2000", True),
        ("from 1950", "jan 1, 1950", True),
        ("from 1950", "dec 31, 1949", False),
        ("to 1950", "1940", True),
        ("to 1950", "2000", False),
        ("to 1950", "dec 31, 1950", True),
        ("to 1950", "jan 1, 1951", False),
        ("after jul 4, 1980", "jul 4, 1980", False),
        ("after jul 4, 1980", "before jul 4, 1980", False),
        ("after jul 4, 1980", "about jul 4, 1980", True),
        ("after jul 4, 1980", "after jul 4, 1980", True),
        ("between 1750 and 1752", "1750", True),
        ("between 1750 and 1752", "about 1750", True),
        ("between 1750 and 1752", "between 1749 and 1750", True),
        ("between 1750 and 1752", "1749", False),
        ("invalid date", "invalid date", True),
        ("invalid date", "invalid", False, True),
        ("invalid date 1", "invalid date 2", False),
        ("abt jan 1, 2000", "dec 31, 1999", True),
        ("jan 1, 2000", "dec 31, 1999", False),
        ("aft jan 1, 2000", "dec 31, 1999", False),
        ("after jan 1, 2000", "after dec 31, 1999", True),
        ("after dec 31, 1999", "after jan 1, 2000", True),
        ("1 31, 2000", "jan 1, 2000", False),
        ("dec 31, 1999", "jan 1, 2000", False),
        ("jan 1, 2000", "before dec 31, 1999", False),
        ("aft jan 1, 2000", "before dec 31, 1999", False),
        ("before jan 1, 2000", "after dec 31, 1999", False),
        ("jan 1, 2000/1", "jan 1, 2000", False),
        ("jan 1, 2000/1", "jan 1, 2001", False),
        ("jan 1, 2000/1", "jan 1, 2000/1", True),
        ("jan 1, 2000/1", "jan 14, 2001", True),
        ("jan 1, 2000/1", "jan 1, 2001 (julian)", True),
        ("about 1984", "about 2005", False),
        ("about 1990", "about 2005", True),
        ("about 2007", "about 2006", True),
        ("about 1995", "after 2000", True),
        ("about 1995", "after 2005", False),
        ("about 2007", "about 2003", True),
        ("before 2007", "2000", True),
        # offsets
        # different calendar, same date
        ("1800-8-3", "15 Thermidor 8 (French Republican)", True),
        ("after 1800-8-3", "before 15 Thermidor 8 (French Republican)", False),
        ("ab cd", "54 ab cd 2000", True, False),
        ("1700-02-29 (Julian)", "1700-03-01 (Swedish)", True),
        ("1706-12-31 (Julian)", "1707-01-01 (Swedish)", True),
        ("1712-02-28 (Julian)", "1712-02-29 (Swedish)", True),
        ("1712-02-29 (Julian)", "1712-02-30 (Swedish)", True),
        # See bug# 7100
        ("1233-12-01", "1234-12-01 (Mar25)", True),
        ("1234-01-04", "1234-01-04 (Mar25)", True),
        # See bug# 7158
        # Some issues passing Travis close to midnight; not sure why:
        #             ("today", Today(), True),
        #             ("today (Hebrew)", Today(), True),
        ("today", "today", True),
        (Today(), Today(), True),
        # See bug# 7197
        ("1788-03-27", "1789-03-27 (Mar25)", True),
        ("1788-03-27 (Julian)", "1789-03-27 (Julian, Mar25)", True),
    ]

    def convert_to_date(self, d):
        return d if isinstance(d, Date) else _dp.parse(d)

    def do_case(self, d1, d2, expected1, expected2=None):
        """
        Tests two Gramps dates to see if they match.
        """
        if expected2 is None:
            expected2 = expected1

        self.assertMatch(d1, d2, expected1)
        self.assertMatch(d2, d1, expected2)

    def assertMatch(self, d1, d2, expected):
        date1 = self.convert_to_date(d1)
        date2 = self.convert_to_date(d2)
        result = date2.match(date1)
        self.assertEqual(
            result,
            expected,
            "'{}' {} '{}'\n({} vs {})".format(
                d1,
                ("did not match" if expected else "matched"),
                d2,
                date1.__dict__,
                date2.__dict__,
            ),
        )

    def test_match(self):
        for testdata in self.tests:
            self.do_case(*testdata)


# -------------------------------------------------------------------------
#
# ArithmeticDateTest
#
# -------------------------------------------------------------------------
class ArithmeticDateTest(BaseDateTest):
    """
    Date arithmetic tests.
    """

    tests = [
        # Date +/- int/tuple -> Date
        ("Date(2008, 1, 1) - 1", "Date(2007, 1, 1)"),
        ("Date(2008, 1, 1) + 1", "Date(2009, 1, 1)"),
        ("Date(2008, 1, 1) - (0,0,1)", "Date(2007, 12, 31)"),
        ("Date(2008, 1, 1) - (0,0,2)", "Date(2007, 12, 30)"),
        ("Date(2008) - (0,0,1)", "Date(2007, 12, 31)"),
        ("Date(2008) - 1", "Date(2007, 1, 1)"),
        ("Date(2008, 12, 31) + (0, 0, 1)", "Date(2009, 1, 1)"),
        ("Date(2000,1,1) - (0,11,0)", "Date(1999, 2, 1)"),
        ("Date(2000,1,1) - (0,1,0)", "Date(1999, 12, 1)"),
        ("Date(2008, 1, 1) + (0, 0, 32)", "Date(2008, 2, 2)"),
        ("Date(2008, 2, 1) + (0, 0, 32)", "Date(2008, 3, 4)"),
        ("Date(2000) - (0, 1, 0)", "Date(1999, 12, 1)"),
        ("Date(2000) + (0, 1, 0)", "Date(2000, 1, 0)"),  # Ok?
        ("Date(2000, 1, 1) - (0, 1, 0)", "Date(1999, 12, 1)"),
        ("Date(2000, 1, 1) - 1", "Date(1999, 1, 1)"),
        ("Date(2000) - 1", "Date(1999)"),
        ("Date(2000) + 1", "Date(2001)"),
        # Date +/- Date -> Span
        ("(Date(1876,5,7) - Date(1876,5,1)).tuple()", "(0, 0, 6)"),
        ("(Date(1876,5,7) - Date(1876,4,30)).tuple()", "(0, 0, 7)"),
        ("(Date(2000,1,1) - Date(1999,2,1)).tuple()", "(0, 11, 0)"),
        ("(Date(2000,1,1) - Date(1999,12,1)).tuple()", "(0, 1, 0)"),
        ("(Date(2007, 12, 23) - Date(1963, 12, 4)).tuple()", "(44, 0, 19)"),
        ("(Date(1963, 12, 4) - Date(2007, 12, 23)).tuple()", "(-44, 0, -19)"),
    ]

    def test_evaluate(self):
        for exp1, exp2 in self.tests:
            val1 = eval(exp1)
            val2 = eval(exp2)
            self.assertEqual(
                val1,
                val2,
                "'%s' should be '%s' but was '%s'" % (exp1, val2, val1),
            )


# -------------------------------------------------------------------------
#
# SpanTest
#
# -------------------------------------------------------------------------
class SpanTest(BaseDateTest):
    """
    Test spans.
    """

    tests = [
        ((2000, 1, 31), (2000, 1, 1), 30),
        ((1799, 11, 19), (8, 2, 18, Date.CAL_FRENCH), 10),
        ((8, 2, 18, Date.CAL_FRENCH), (1799, 11, 4), 5),
        ((8, 2, 18, Date.CAL_FRENCH), (3, 2, 9, Date.CAL_FRENCH), 1836),
    ]

    def test_evaluate(self):
        for value1, value2, duration in self.tests:
            date1 = self._get_date(value1)
            date2 = self._get_date(value2)
            span1 = Span(date1, date2)
            self.assertEqual(int(span1), duration)
            span2 = Span(date2, date1)
            self.assertEqual(int(span2), -duration)

    def _get_date(self, value):
        date = Date()
        if len(value) == 4:
            date.set_calendar(value[3])
        date.set_yr_mon_day(value[0], value[1], value[2])
        return date


# -------------------------------------------------------------------------
#
# DateComparisonTest
#
# -------------------------------------------------------------------------
@unittest.skipUnless(
    ENGLISH_DATE_HANDLER,
    "This test of Date() matching logic can only run in US-English locale.",
)
class DateComparisonTest(BaseDateTest):
    """
    Date comparison tests.
    """

    tests = [
        ("1960", "=", "1960", True),
        ("1960", "=", "1961", False),
        ("1960", "!=", "1960", False),
        ("1960", "!=", "1961", True),
        ("1960", "==", "1960", True),
        ("1960", "==", "1961", False),
        ("1960", "<", "1959", False),
        ("1960", "<", "1960", True),
        ("1960", "<", "1961", True),
        ("1960", ">", "1959", True),
        ("1960", ">", "1960", True),
        ("1960", ">", "1961", False),
        ("1960", "<<", "1959", False),
        ("1960", "<<", "1960", False),
        ("1960", "<<", "1961", True),
        ("1960", ">>", "1959", True),
        ("1960", ">>", "1960", False),
        ("1960", ">>", "1961", False),
        ("1960", "<=", "1959", False),
        ("1960", "<=", "1960", True),
        ("1960", "<=", "1961", True),
        ("1960", ">=", "1959", True),
        ("1960", ">=", "1960", True),
        ("1960", ">=", "1961", False),
        ("1960-01-01", "=", "1960-01-01", True),
        ("1960-01-01", "=", "1960-01-02", False),
        ("1960-01-01", "!=", "1960-01-01", False),
        ("1960-01-01", "!=", "1960-01-02", True),
        ("1960-01-01", "==", "1960-01-01", True),
        ("1960-01-01", "==", "1960-01-02", False),
        ("1960-01-01", "<", "1959-12-31", False),
        ("1960-01-01", "<", "1960-01-01", False),
        ("1960-01-01", "<", "1960-01-02", True),
        ("1960-01-01", ">", "1959-12-31", True),
        ("1960-01-01", ">", "1960-01-01", False),
        ("1960-01-01", ">", "1960-01-02", False),
        ("1960-01-01", "<<", "1959-12-31", False),
        ("1960-01-01", "<<", "1960-01-01", False),
        ("1960-01-01", "<<", "1960-01-02", True),
        ("1960-01-01", ">>", "1959-12-31", True),
        ("1960-01-01", ">>", "1960-01-01", False),
        ("1960-01-01", ">>", "1960-01-02", False),
        ("before 1960-01-01", "=", "1959-12-31", True),
        ("before 1960-01-01", "=", "1960-01-01", False),
        ("about 1960-01-01", "=", "1959-12-31", True),
        ("about 1960-01-01", "=", "1960-01-01", True),
        ("about 1960-01-01", "=", "1960-01-02", True),
        ("after 1960-01-01", "=", "1960-01-01", False),
        ("after 1960-01-01", "=", "1960-01-02", True),
        ("between 1960-01-01 and 1960-01-03", "=", "1959-12-31", False),
        ("between 1960-01-01 and 1960-01-03", "=", "1960-01-01", True),
        ("between 1960-01-01 and 1960-01-03", "=", "1960-01-02", True),
        ("between 1960-01-01 and 1960-01-03", "=", "1960-01-02", True),
        ("between 1960-01-01 and 1960-01-03", "=", "1960-01-04", False),
        ("before 1960-01-01", "==", "1959-12-31", False),  # !
        ("before 1960-01-01", "==", "1960-01-01", True),  # !
        ("before 1960-01-01", "==", "1960-01-02", False),  # !
        ("about 1960-01-01", "==", "1959-12-31", False),  # !
        ("about 1960-01-01", "==", "1960-01-01", True),
        ("about 1960-01-01", "==", "1960-01-02", False),  # !
        ("after 1960-01-01", "==", "1960-01-01", True),  # !
        ("after 1960-01-01", "==", "1960-01-02", False),  # !
        ("between 1960-01-01 and 1960-01-03", "==", "1959-12-31", False),
        ("between 1960-01-01 and 1960-01-03", "==", "1960-01-01", True),
        ("between 1960-01-01 and 1960-01-03", "==", "1960-01-02", False),
        ("between 1960-01-01 and 1960-01-03", "==", "1960-01-02", False),
        ("between 1960-01-01 and 1960-01-03", "==", "1960-01-04", False),
        (
            "4713-01-01 B.C. (Julian)",
            "=",
            "to 1960",
            False,
        ),  # Corner case, logically True.
        ("4713-01-02 B.C. (Julian)", "=", "to 1960", True),
        ("4713-01-02 B.C. (Julian)", "<", "to 1960", True),
        ("4713-01-02 B.C. (Julian)", "<=", "to 1960", True),
        ("4713-01-02 B.C. (Julian)", "<<", "to 1960", False),
        ("from 1960", "=", "from 1960", True),
        ("from 1960", "=", "from 1961", True),
        ("from 1960", "!=", "from 1960", False),
        ("from 1960", "!=", "from 1961", True),
        ("from 1960", "==", "from 1960", True),
        ("from 1960", "==", "from 1961", False),
        ("from 1960", "<", "from 1959", True),
        ("from 1960", "<", "from 1960", True),
        ("from 1960", "<", "from 1961", True),
        ("from 1960", ">", "from 1959", True),
        ("from 1960", ">", "from 1960", True),
        ("from 1960", ">", "from 1961", True),
        ("from 1960", "<<", "from 1959", False),
        ("from 1960", "<<", "from 1960", False),
        ("from 1960", "<<", "from 1961", False),
        ("from 1960", ">>", "from 1959", False),
        ("from 1960", ">>", "from 1960", False),
        ("from 1960", ">>", "from 1961", False),
        ("from 1960", "<=", "from 1959", False),
        ("from 1960", "<=", "from 1960", True),
        ("from 1960", "<=", "from 1961", True),
        ("from 1960", ">=", "from 1959", True),
        ("from 1960", ">=", "from 1960", True),
        ("from 1960", ">=", "from 1961", False),
        ("from 1960", "=", "to 1959", False),
        ("from 1960", "=", "to 1960", True),
        ("from 1960", "=", "to 1961", True),
        ("from 1960", "!=", "to 1959", True),
        ("from 1960", "!=", "to 1960", False),
        ("from 1960", "!=", "to 1961", True),
        ("from 1960", "==", "to 1959", False),
        ("from 1960", "==", "to 1960", True),
        ("from 1960", "==", "to 1961", False),
        ("from 1960", "<", "to 1959", False),
        ("from 1960", "<", "to 1960", True),
        ("from 1960", "<", "to 1961", True),
        ("from 1960", ">", "to 1959", True),
        ("from 1960", ">", "to 1960", True),
        ("from 1960", ">", "to 1961", True),
        ("from 1960", "<<", "to 1959", False),
        ("from 1960", "<<", "to 1960", False),
        ("from 1960", "<<", "to 1961", False),
        ("from 1960", ">>", "to 1959", True),
        ("from 1960", ">>", "to 1960", False),
        ("from 1960", ">>", "to 1961", False),
        ("from 1960", "<=", "to 1959", False),
        ("from 1960", "<=", "to 1960", True),
        ("from 1960", "<=", "to 1961", True),
        ("from 1960", ">=", "to 1959", True),
        ("from 1960", ">=", "to 1960", True),
        ("from 1960", ">=", "to 1961", False),
        ("to 1960", "=", "from 1959", True),
        ("to 1960", "=", "from 1960", True),
        ("to 1960", "=", "from 1961", False),
        ("to 1960", "!=", "from 1959", True),
        ("to 1960", "!=", "from 1960", False),
        ("to 1960", "!=", "from 1961", True),
        ("to 1960", "==", "from 1959", False),
        ("to 1960", "==", "from 1960", True),
        ("to 1960", "==", "from 1961", False),
        ("to 1960", "<", "from 1959", True),
        ("to 1960", "<", "from 1960", True),
        ("to 1960", "<", "from 1961", True),
        ("to 1960", ">", "from 1959", True),
        ("to 1960", ">", "from 1960", True),
        ("to 1960", ">", "from 1961", False),
        ("to 1960", "<<", "from 1959", False),
        ("to 1960", "<<", "from 1960", False),
        ("to 1960", "<<", "from 1961", True),
        ("to 1960", ">>", "from 1959", False),
        ("to 1960", ">>", "from 1960", False),
        ("to 1960", ">>", "from 1961", False),
        ("to 1960", "<=", "from 1959", False),
        ("to 1960", "<=", "from 1960", True),
        ("to 1960", "<=", "from 1961", True),
        ("to 1960", ">=", "from 1959", True),
        ("to 1960", ">=", "from 1960", True),
        ("to 1960", ">=", "from 1961", False),
        ("to 1960", "=", "to 1959", True),
        ("to 1960", "=", "to 1960", True),
        ("to 1960", "=", "to 1961", True),
        ("to 1960", "!=", "to 1959", True),
        ("to 1960", "!=", "to 1960", False),
        ("to 1960", "!=", "to 1961", True),
        ("to 1960", "==", "to 1959", False),
        ("to 1960", "==", "to 1960", True),
        ("to 1960", "==", "to 1961", False),
        ("to 1960", "<", "to 1959", True),
        ("to 1960", "<", "to 1960", True),
        ("to 1960", "<", "to 1961", True),
        ("to 1960", ">", "to 1959", True),
        ("to 1960", ">", "to 1960", True),
        ("to 1960", ">", "to 1961", True),
        ("to 1960", "<<", "to 1959", False),
        ("to 1960", "<<", "to 1960", False),
        ("to 1960", "<<", "to 1961", False),
        ("to 1960", ">>", "to 1959", False),
        ("to 1960", ">>", "to 1960", False),
        ("to 1960", ">>", "to 1961", False),
        ("to 1960", "<=", "to 1959", False),
        ("to 1960", "<=", "to 1960", True),
        ("to 1960", "<=", "to 1961", True),
        ("to 1960", ">=", "to 1959", True),
        ("to 1960", ">=", "to 1960", True),
        ("to 1960", ">=", "to 1961", False),
        ("from 1960 to 1961", "=", "from 1958 to 1959", False),
        ("from 1960 to 1961", "=", "from 1959 to 1960", True),
        ("from 1960 to 1961", "=", "from 1960 to 1961", True),
        ("from 1960 to 1961", "=", "from 1961 to 1962", True),
        ("from 1960 to 1961", "=", "from 1962 to 1963", False),
        ("from 1960 to 1961", "!=", "from 1958 to 1959", True),
        ("from 1960 to 1961", "!=", "from 1959 to 1960", True),
        ("from 1960 to 1961", "!=", "from 1960 to 1961", False),
        ("from 1960 to 1961", "!=", "from 1961 to 1962", True),
        ("from 1960 to 1961", "!=", "from 1962 to 1963", True),
        ("from 1960 to 1961", "==", "from 1959 to 1960", False),
        ("from 1960 to 1961", "==", "from 1960 to 1961", True),
        ("from 1960 to 1961", "==", "from 1961 to 1962", False),
        ("from 1960 to 1961", "<", "from 1958 to 1959", False),
        ("from 1960 to 1961", "<", "from 1959 to 1960", True),
        ("from 1960 to 1961", "<", "from 1960 to 1961", True),
        ("from 1960 to 1961", "<", "from 1961 to 1962", True),
        ("from 1960 to 1961", "<", "from 1962 to 1963", True),
        ("from 1960 to 1961", ">", "from 1958 to 1959", True),
        ("from 1960 to 1961", ">", "from 1959 to 1960", True),
        ("from 1960 to 1961", ">", "from 1960 to 1961", True),
        ("from 1960 to 1961", ">", "from 1961 to 1962", True),
        ("from 1960 to 1961", ">", "from 1962 to 1963", False),
        ("from 1960 to 1961", "<<", "from 1958 to 1959", False),
        ("from 1960 to 1961", "<<", "from 1959 to 1960", False),
        ("from 1960 to 1961", "<<", "from 1960 to 1961", False),
        ("from 1960 to 1961", "<<", "from 1961 to 1962", False),
        ("from 1960 to 1961", "<<", "from 1962 to 1963", True),
        ("from 1960 to 1961", ">>", "from 1958 to 1959", True),
        ("from 1960 to 1961", ">>", "from 1959 to 1960", False),
        ("from 1960 to 1961", ">>", "from 1960 to 1961", False),
        ("from 1960 to 1961", ">>", "from 1961 to 1962", False),
        ("from 1960 to 1961", ">>", "from 1962 to 1963", False),
        ("from 1960 to 1961", "<=", "from 1958 to 1959", False),
        ("from 1960 to 1961", "<=", "from 1959 to 1960", False),
        ("from 1960 to 1961", "<=", "from 1960 to 1961", True),
        ("from 1960 to 1961", "<=", "from 1961 to 1962", True),
        ("from 1960 to 1961", "<=", "from 1962 to 1963", True),
        ("from 1960 to 1961", ">=", "from 1958 to 1959", True),
        ("from 1960 to 1961", ">=", "from 1959 to 1960", True),
        ("from 1960 to 1961", ">=", "from 1960 to 1961", True),
        ("from 1960 to 1961", ">=", "from 1961 to 1962", False),
        ("from 1960 to 1961", ">=", "from 1962 to 1963", False),
        (
            "from 1960-01-01 to 1961-01-01",
            "=",
            "from 1958-01-01 to 1959-12-31",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "=",
            "from 1958-01-01 to 1960-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "=",
            "from 1958-01-01 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "=",
            "from 1958-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "=",
            "from 1960-01-01 to 1960-12-31",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "=",
            "from 1960-01-01 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "=",
            "from 1960-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "=",
            "from 1960-12-31 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "=",
            "from 1960-12-31 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "=",
            "from 1961-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "=",
            "from 1961-01-02 to 1961-01-03",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "!=",
            "from 1958-01-01 to 1959-12-31",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "!=",
            "from 1958-01-01 to 1960-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "!=",
            "from 1958-01-01 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "!=",
            "from 1958-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "!=",
            "from 1960-01-01 to 1960-12-31",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "!=",
            "from 1960-01-01 to 1961-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "!=",
            "from 1960-01-01 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "!=",
            "from 1960-12-31 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "!=",
            "from 1960-12-31 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "!=",
            "from 1961-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "!=",
            "from 1961-01-02 to 1961-01-03",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "==",
            "from 1958-01-01 to 1959-12-31",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "==",
            "from 1958-01-01 to 1960-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "==",
            "from 1958-01-01 to 1961-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "==",
            "from 1958-01-01 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "==",
            "from 1960-01-01 to 1960-12-31",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "==",
            "from 1960-01-01 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "==",
            "from 1960-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "==",
            "from 1960-12-31 to 1961-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "==",
            "from 1960-12-31 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "==",
            "from 1961-01-01 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "==",
            "from 1961-01-02 to 1961-01-03",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<",
            "from 1958-01-01 to 1959-12-31",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<",
            "from 1958-01-01 to 1960-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<",
            "from 1958-01-01 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<",
            "from 1958-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<",
            "from 1960-01-01 to 1960-12-31",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<",
            "from 1960-01-01 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<",
            "from 1960-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<",
            "from 1960-12-31 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<",
            "from 1960-12-31 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<",
            "from 1961-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<",
            "from 1961-01-02 to 1961-01-03",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">",
            "from 1958-01-01 to 1959-12-31",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">",
            "from 1958-01-01 to 1960-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">",
            "from 1958-01-01 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">",
            "from 1958-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">",
            "from 1960-01-01 to 1960-12-31",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">",
            "from 1960-01-01 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">",
            "from 1960-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">",
            "from 1960-12-31 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">",
            "from 1960-12-31 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">",
            "from 1961-01-01 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">",
            "from 1961-01-02 to 1961-01-03",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<<",
            "from 1958-01-01 to 1959-12-31",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<<",
            "from 1958-01-01 to 1960-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<<",
            "from 1958-01-01 to 1961-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<<",
            "from 1958-01-01 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<<",
            "from 1960-01-01 to 1960-12-31",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<<",
            "from 1960-01-01 to 1961-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<<",
            "from 1960-01-01 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<<",
            "from 1960-12-31 to 1961-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<<",
            "from 1960-12-31 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<<",
            "from 1961-01-01 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<<",
            "from 1961-01-02 to 1961-01-03",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">>",
            "from 1958-01-01 to 1959-12-31",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">>",
            "from 1958-01-01 to 1960-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">>",
            "from 1958-01-01 to 1961-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">>",
            "from 1958-01-01 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">>",
            "from 1960-01-01 to 1960-12-31",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">>",
            "from 1960-01-01 to 1961-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">>",
            "from 1960-01-01 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">>",
            "from 1960-12-31 to 1961-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">>",
            "from 1960-12-31 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">>",
            "from 1961-01-01 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">>",
            "from 1961-01-02 to 1961-01-03",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<=",
            "from 1958-01-01 to 1959-12-31",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<=",
            "from 1958-01-01 to 1960-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<=",
            "from 1958-01-01 to 1961-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<=",
            "from 1958-01-01 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<=",
            "from 1960-01-01 to 1960-12-31",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<=",
            "from 1960-01-01 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<=",
            "from 1960-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<=",
            "from 1960-12-31 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<=",
            "from 1960-12-31 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<=",
            "from 1961-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            "<=",
            "from 1961-01-02 to 1961-01-03",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">=",
            "from 1958-01-01 to 1959-12-31",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">=",
            "from 1958-01-01 to 1960-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">=",
            "from 1958-01-01 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">=",
            "from 1958-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">=",
            "from 1960-01-01 to 1960-12-31",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">=",
            "from 1960-01-01 to 1961-01-01",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">=",
            "from 1960-01-01 to 1961-01-02",
            True,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">=",
            "from 1960-12-31 to 1961-01-01",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">=",
            "from 1960-12-31 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">=",
            "from 1961-01-01 to 1961-01-02",
            False,
        ),
        (
            "from 1960-01-01 to 1961-01-01",
            ">=",
            "from 1961-01-02 to 1961-01-03",
            False,
        ),
    ]

    def convert_to_date(self, d):
        return d if isinstance(d, Date) else _dp.parse(d)

    def do_case(self, d1, op, d2, expected):
        """
        Compare two Gramps dates.
        """
        failstr = d1 + " " + op + " " + d2 + " should be {}".format(expected)
        date1 = self.convert_to_date(d1)
        date2 = self.convert_to_date(d2)
        if op == "=":
            self.assertEqual(date1.match(date2), expected, failstr)
        elif op == "!=":
            self.assertEqual(date1 != date2, expected, failstr)
        elif op == "==":
            self.assertEqual(date1 == date2, expected, failstr)
        elif op == "<":
            self.assertEqual(date1 < date2, expected, failstr)
        elif op == "<<":
            self.assertEqual(date1 << date2, expected, failstr)
        elif op == ">":
            self.assertEqual(date1 > date2, expected, failstr)
        elif op == ">>":
            self.assertEqual(date1 >> date2, expected, failstr)
        elif op == "<=":
            self.assertEqual(date1 <= date2, expected, failstr)
        elif op == ">=":
            self.assertEqual(date1 >= date2, expected, failstr)

    def test_comparison(self):
        for testdata in self.tests:
            self.do_case(*testdata)


# -------------------------------------------------------------------------
#
# AgeTest
#
# -------------------------------------------------------------------------
@unittest.skipUnless(
    ENGLISH_DATE_HANDLER,
    "This test of Date() matching logic can only run in US-English locale.",
)
class AgeTest(BaseDateTest):
    """
    Age tests.
    """

    tests = [
        ("1960", "1960", "0 days"),  # Logically (less than 1 year)
        (
            "1960-01",
            "1960-01",
            "0 days",
        ),  # Logically (less than 1 month)
        (
            "1960-01",
            "1960-02",
            "1 month",
        ),  # Logically (between 1 month and 1 month, 27|28) days)
        ("1960-01-01", "1960-01-02", "1 day"),
        ("1960-01-01", "1960-01-31", "30 days"),
        ("after 1960-01-01", "1960-01-31", "less than 29 days"),
        ("1960-01-01", "1960-02-02", "1 month, 1 day"),
        ("1960-01-01", "1961-02-02", "1 year, 1 month"),
        ("1960-01-01", "1965-01-01", "5 years"),
        (
            "1960-01-01",
            "1965-02-02",
            "5 years, 1 month",
        ),
        (
            "about 1960-01-01",
            "before 1965-02-02",
            "less than about 5 years, 1 month",
        ),
        (
            "about 1960-01-01",
            "after 1965-02-02",
            "more than about 5 years, 1 month",
        ),
        (
            "1960",
            "2000",
            "40 years",
        ),
        ("", "1760", "unknown"),
        ("", "1960", "unknown"),
        ("", "2020", "unknown"),
        ("", "3020", "unknown"),
        ("2000", "", "unknown"),
    ]

    def convert_to_date(self, d):
        return d if isinstance(d, Date) else _dp.parse(d)

    def do_case(self, d1, d2, exp_age):
        span = Span(self.convert_to_date(d2), self.convert_to_date(d1))
        age = span.as_age()
        failstr = (
            "Birth at "
            + d1
            + ", death at "
            + d2
            + " gives age "
            + age
            + ". Should be {}".format(exp_age)
        )
        self.assertEqual(age, exp_age, failstr)

    def test_age(self):
        for testdata in self.tests:
            self.do_case(*testdata)


# -------------------------------------------------------------------------
#
# SwedishDateTest
#
# -------------------------------------------------------------------------
class SwedishDateTest(BaseDateTest):
    """
    Swedish calendar tests.
    """

    def test_swedish(self):
        for date in swedish_dates:
            self.assertEqual(date.sortval, date.to_calendar("gregorian").sortval)


class Test_set2(BaseDateTest):
    """
    Test the Date.set2_... setters -- the ones to manipulate the 2nd date
    of a compound date
    """

    def setUp(self):
        self.date = d = Date()
        d.set(
            modifier=Date.MOD_RANGE,
            # d  m  y    sl--d  m  y    sl
            value=(1, 1, 2000, 0, 1, 1, 2010, 0),
        )

    def testStartStopSanity(self):
        start, stop = self.date.get_start_stop_range()
        self.assertEqual(start, (2000, 1, 1))
        self.assertEqual(stop, (2010, 1, 1))

    def test_set2_ymd_overrides_stop_date(self):
        self.date.set2_yr_mon_day(2013, 2, 2)
        start, stop = self.date.get_start_stop_range()
        self.assertEqual(start, (2000, 1, 1))
        self.assertEqual(stop, (2013, 2, 2))

    def test_set_ymd_overrides_both_dates(self):
        self.date.set_yr_mon_day(2013, 2, 2, remove_stop_date=True)
        start, stop = self.date.get_start_stop_range()
        self.assertEqual(start, stop)
        self.assertEqual(stop, (2013, 2, 2))

    def test_set_ymd_offset_updates_both_ends(self):
        self.date.set_yr_mon_day_offset(+2, +2, +2)
        start, stop = self.date.get_start_stop_range()
        self.assertEqual(start, (2002, 3, 3))
        self.assertEqual(stop, (2012, 3, 3))

    def test_set2_ymd_offset_updates_stop_date(self):
        self.date.set2_yr_mon_day_offset(+7, +5, +5)
        start, stop = self.date.get_start_stop_range()
        self.assertEqual(start, (2000, 1, 1))
        self.assertEqual(stop, (2017, 6, 6))

    def test_copy_offset_ymd_preserves_orig(self):
        copied = self.date.copy_offset_ymd(year=-1)
        self.testStartStopSanity()
        start, stop = copied.get_start_stop_range()
        self.assertEqual(start, (1999, 1, 1))
        self.assertEqual(stop, (2009, 1, 1))

    def test_copy_ymd_preserves_orig(self):
        copied = self.date.copy_ymd(year=1000, month=10, day=10, remove_stop_date=True)
        self.testStartStopSanity()
        start, stop = copied.get_start_stop_range()
        self.assertEqual(start, (1000, 10, 10))
        self.assertEqual(stop, (1000, 10, 10))

    def _test_set2_function_raises_error_unless_compound(self, function):
        for mod in (
            Date.MOD_NONE,
            Date.MOD_BEFORE,
            Date.MOD_AFTER,
            Date.MOD_ABOUT,
            Date.MOD_TEXTONLY,
        ):
            self.date.set_modifier(mod)
            try:
                function(self.date)
                self.assertTrue(
                    False,
                    "Modifier: {}, dateval: {} - exception expected!".format(
                        mod, self.date.dateval
                    ),
                )
            except DateError:
                pass

    def test_set2_ymd_raises_error_unless_compound(self):
        self._test_set2_function_raises_error_unless_compound(
            lambda date: date.set2_yr_mon_day(2013, 2, 2)
        )

    def test_set2_ymd_offset_raises_error_unless_compound(self):
        self._test_set2_function_raises_error_unless_compound(
            lambda date: date.set2_yr_mon_day_offset(year=-1)
        )


class Test_set_newyear(BaseDateTest):
    def test_raises_error_iff_calendar_has_fixed_newyear(self):
        for cal in Date.CALENDARS:
            d = Date(1111, 2, 3)
            should_raise = calendar_has_fixed_newyear(cal)
            message = "{name} {cal}".format(name=Date.calendar_names[cal], cal=cal)
            try:
                d.set(calendar=cal, newyear=2)
                self.assertFalse(should_raise, message)
            except DateError:
                self.assertTrue(should_raise, message)


# -------------------------------------------------------------------------
#
# EmptyDateTest
#
# -------------------------------------------------------------------------
class EmptyDateTest(BaseDateTest):
    """
    Tests for empty dates.
    """

    def test_empty(self):
        d = Date()
        self.assertTrue(d.is_empty())

    def test_text_only_empty(self):
        d = Date()
        d.set(text="First of Jan", modifier=Date.MOD_TEXTONLY)
        self.assertFalse(d.is_empty())

    def test_single_empty(self):
        d = Date()
        d.set(value=(1, 1, 1900, False), modifier=Date.MOD_NONE)
        self.assertFalse(d.is_empty())

    def test_range_empty(self):
        d = Date()
        d.set(
            value=(1, 1, 1900, False, 1, 1, 1910, False),
            modifier=Date.MOD_RANGE,
        )
        self.assertFalse(d.is_empty())

    def test_span_empty(self):
        d = Date()
        d.set(value=(1, 1, 1900, False, 1, 1, 1910, False), modifier=Date.MOD_SPAN)
        self.assertFalse(d.is_empty())


# -------------------------------------------------------------------------
#
# AnniversaryDateTest
#
# -------------------------------------------------------------------------
class AnniversaryDateTest(BaseDateTest):
    """
    Tests for leap day anniversary dates.
    """

    def test_leapyear_1(self):
        config.set("preferences.february-29", 0)
        d = Date(1904, 2, 29)
        self.assertEqual(d.anniversary(1908), (2, 29))

    def test_leapyear_2(self):
        config.set("preferences.february-29", 1)
        d = Date(1904, 2, 29)
        self.assertEqual(d.anniversary(1908), (2, 29))

    def test_nonleapyear_before(self):
        config.set("preferences.february-29", 0)
        d = Date(1904, 2, 29)
        self.assertEqual(d.anniversary(1910), (2, 28))

    def test_nonleapyear_after(self):
        config.set("preferences.february-29", 1)
        d = Date(1904, 2, 29)
        self.assertEqual(d.anniversary(1910), (3, 1))

    def test_nonleapyear_keep(self):
        config.set("preferences.february-29", 2)
        d = Date(1904, 2, 29)
        self.assertEqual(d.anniversary(1910), (2, 29))


if __name__ == "__main__":
    unittest.main()
