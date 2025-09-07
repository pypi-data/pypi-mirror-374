# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013 Vassilii Khachaturov <vassilii@tarunz.org>
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

"""Unittest for argparser.py"""

import unittest
from unittest.mock import Mock
from ..argparser import ArgParser


class TestArgParser(unittest.TestCase):
    def setUp(self):
        pass

    def create_parser(*self_and_args):
        return ArgParser(list(self_and_args))

    def triggers_option_error(self, option):
        ap = self.create_parser(option)
        return (str(ap.errors).find("option " + option) >= 0, ap)

    def test_wrong_argument_triggers_option_error(self):
        bad, ap = self.triggers_option_error("--I-am-a-wrong-argument")
        self.assertTrue(bad, ap.__dict__)

    def test_y_shortopt_sets_auto_accept(self):
        bad, ap = self.triggers_option_error("-y")

        self.assertFalse(bad)

        expected_errors = [
            (
                "Error parsing the arguments",
                "Error parsing the arguments: [ -y ] \n"
                + "To use in the command-line mode, supply at least one input file to process.",
            )
        ]
        self.assertEqual(expected_errors, ap.errors)

        self.assertTrue(ap.auto_accept)

    def test_yes_longopt_sets_auto_accept(self):
        bad, ap = self.triggers_option_error("--yes")
        self.assertFalse(bad, ap.errors)
        self.assertTrue(ap.auto_accept)

    def test_q_shortopt_sets_quiet(self):
        bad, ap = self.triggers_option_error("-q")
        self.assertFalse(bad, ap.errors)
        self.assertTrue(ap.quiet)

    def test_quiet_longopt_sets_quiet(self):
        bad, ap = self.triggers_option_error("--quiet")
        self.assertFalse(bad, ap.errors)
        self.assertTrue(ap.quiet)

    def test_quiet_exists_by_default(self):
        ap = self.create_parser()
        self.assertTrue(hasattr(ap, "quiet"))

    def test_auto_accept_unset_by_default(self):
        ap = self.create_parser()
        self.assertFalse(ap.auto_accept)

    def test_exception(self):
        argument_parser = self.create_parser("-O")

        expected_errors = [
            (
                "Error parsing the arguments",
                "option -O requires argument\n"
                "Error parsing the arguments: [ -O ] \n"
                "Type gramps --help for an overview of commands, or read the manual pages.",
            )
        ]
        self.assertEqual(expected_errors, argument_parser.errors)

    def test_option_with_multiple_arguments(self):
        argument_parser = self.create_parser("-l", "family_tree_name")
        self.assertEqual(argument_parser.database_names, ["family_tree_name"])


if __name__ == "__main__":
    unittest.main()
