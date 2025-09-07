
import sys
import os
import unittest
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from print_fa.print_fa import print_fa, Colors
import arabic_reshaper
from bidi.algorithm import get_display

class TestPrintFa(unittest.TestCase):

    def setUp(self):
        self.held_output = StringIO()
        sys.stdout = self.held_output

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def _get_expected_output(self, text):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text

    def test_basic_persian_text(self):
        text = "سلام دنیا"
        print_fa(text)
        output = self.held_output.getvalue().strip()
        expected_output = self._get_expected_output(text)
        self.assertIn(expected_output, output)

    def test_persian_with_english(self):
        text = "سلام World"
        print_fa(text)
        output = self.held_output.getvalue().strip()
        expected_output = self._get_expected_output(text)
        self.assertIn(expected_output, output)

    def test_colored_text(self):
        text = "متن قرمز"
        print_fa(text, color="red")
        output = self.held_output.getvalue().strip()
        expected_output = Colors.RED + self._get_expected_output(text) + Colors.RESET
        self.assertIn(expected_output, output)

    def test_bold_text(self):
        text = "متن پررنگ"
        print_fa(text, bold=True)
        output = self.held_output.getvalue().strip()
        expected_output = Colors.BOLD + self._get_expected_output(text) + Colors.RESET
        self.assertIn(expected_output, output)

    def test_underline_text(self):
        text = "متن زیرخط"
        print_fa(text, underline=True)
        output = self.held_output.getvalue().strip()
        expected_output = Colors.UNDERLINE + self._get_expected_output(text) + Colors.RESET
        self.assertIn(expected_output, output)

    def test_multiple_styles(self):
        text = "متن رنگی و پررنگ"
        print_fa(text, color="blue", bold=True)
        output = self.held_output.getvalue().strip()
        expected_output = Colors.BLUE + Colors.BOLD + self._get_expected_output(text) + Colors.RESET
        self.assertIn(expected_output, output)

    def test_invalid_color(self):
        text = "متن با رنگ نامعتبر"
        print_fa(text, color="purple")
        output = self.held_output.getvalue().strip()
        self.assertIn("Warning: Invalid color 'purple'. Using default color.", output)
        expected_output = self._get_expected_output(text)
        self.assertIn(expected_output, output)

if __name__ == '__main__':
    unittest.main()


