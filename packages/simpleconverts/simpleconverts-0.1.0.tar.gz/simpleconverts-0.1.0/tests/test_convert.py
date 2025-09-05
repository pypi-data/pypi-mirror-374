# tests/test_convert.py
import unittest
from simpleconverts.convert import convert, ConversionError

class TestConvert(unittest.TestCase):

    def test_distance(self):
        self.assertAlmostEqual(convert(10, "km", "mi"), 6.2137, places=4)

    def test_mass(self):
        self.assertAlmostEqual(convert(100, "kg", "lb"), 220.462, places=3)

    def test_temperature(self):
        self.assertAlmostEqual(convert(25, "C", "F"), 77.0, places=1)

    def test_volume(self):
        self.assertAlmostEqual(convert(2, "L", "cup"), 8.3333, places=3)

    def test_time(self):
        self.assertEqual(convert(1, "h", "min"), 60)

    def test_energy(self):
        self.assertAlmostEqual(convert(500, "cal", "kJ"), 2.092, places=3)

    def test_invalid(self):
        with self.assertRaises(ConversionError):
            convert(1, "m", "kg")

if __name__ == "__main__":
    unittest.main()
