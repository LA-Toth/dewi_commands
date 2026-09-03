# Copyright 2015-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import dewi_core.testcase

from dewi_commands.commands.edit.edit import convert_to_vim_args


class TestVimArgumentConverter(dewi_core.testcase.TestCase):
    def test_empty_list_is_not_changed(self):
        self.assert_equal([], convert_to_vim_args([]))

    def test_filename_is_not_changed(self):
        self.assert_equal(['path/to/file34.txt'], convert_to_vim_args(['path/to/file34.txt']))

    def test_file_colon_number_is_converted_to_line_number(self):
        self.assert_equal(['path/to/file34.txt', '+42'], convert_to_vim_args(['path/to/file34.txt:42']))
        self.assert_equal(['path/to/file34.txt', '+42'], convert_to_vim_args(['path/to/file34.txt:42:']))

    def test_file_names_with_line_and_column_number_are_converted(self):
        self.assert_equal(['path/to/file34.txt', '+42'], convert_to_vim_args(['path/to/file34.txt:42:12']))
        self.assert_equal(['path/to/file34.txt', '+42'], convert_to_vim_args(['path/to/file34.txt:42:12:']))

    def test_that_a_bracket_is_not_a_line_number(self):
        # '[' used to be a member of the character class of the line number,
        # as it was written as [[0-9], which also warns of a nested set.
        self.assert_equal(['path/to/file.txt:[42'], convert_to_vim_args(['path/to/file.txt:[42']))
        self.assert_equal(['path/to/file.txt:['], convert_to_vim_args(['path/to/file.txt:[']))

    def test_multiple_args_are_prefixed_by_p_option(self):
        self.assert_equal(
            ['-p', 'path/to/file34.txt:34', 'path/to/file35.txt'],
            convert_to_vim_args(['path/to/file34.txt:34', 'path/to/file35.txt']))
