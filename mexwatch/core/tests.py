from django.test import TestCase

# Create your tests here.
from core.utils import get_display_number


class UtilsTests(TestCase):

    def test_get_display_number(self):
        self.assertEquals('1.2346e-07', get_display_number(0.000000123456789))
        self.assertEquals('1.2346e-04', get_display_number(0.000123456789))
        self.assertEquals(0.001235, get_display_number(0.00123456789))
        self.assertEquals(0.1235, get_display_number(0.123456789))
        self.assertEquals(1.235, get_display_number(1.23456789))
        self.assertEquals(12.35, get_display_number(12.3456789))
        self.assertEquals(123.5, get_display_number(123.456789))
        self.assertEquals(1234, get_display_number(1234.56789))
        self.assertEquals(12345, get_display_number(12345.6789))
        self.assertEquals('123.4k', get_display_number(123456.789))
        self.assertEquals('1.234m', get_display_number(1234567.89))
        self.assertEquals('12.34m', get_display_number(12345678.9))
        self.assertEquals('123.4m', get_display_number(123456789))
        self.assertEquals('1.234b', get_display_number(1234567890))
        self.assertEquals('1.2346e+10', get_display_number(12345678900))
        self.assertEquals('1.2346e+13', get_display_number(12345678900000))

        self.assertEquals('-1.2346e-07', get_display_number(-0.000000123456789))
        self.assertEquals('-1.2346e-04', get_display_number(-0.000123456789))
        self.assertEquals(-0.001235, get_display_number(-0.00123456789))
        self.assertEquals(-0.1235, get_display_number(-0.123456789))
        self.assertEquals(-1.235, get_display_number(-1.23456789))
        self.assertEquals(-12.35, get_display_number(-12.3456789))
        self.assertEquals(-123.5, get_display_number(-123.456789))
        self.assertEquals(-1234, get_display_number(-1234.56789))
        self.assertEquals(-12345, get_display_number(-12345.6789))
        self.assertEquals('-123.4k', get_display_number(-123456.789))
        self.assertEquals('-1.234m', get_display_number(-1234567.89))
        self.assertEquals('-12.34m', get_display_number(-12345678.9))
        self.assertEquals('-123.4m', get_display_number(-123456789))
        self.assertEquals('-1.234b', get_display_number(-1234567890))
        self.assertEquals('-1.2346e+10', get_display_number(-12345678900))
        self.assertEquals('-1.2346e+13', get_display_number(-12345678900000))